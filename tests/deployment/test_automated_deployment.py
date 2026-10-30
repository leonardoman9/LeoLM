from pathlib import Path
import subprocess

from leolm.deployment.manifest import redacted_plan
from leolm.deployment.profile import DeviceProfile
from leolm.deployment.ssh import SSHProvisioner
from leolm.deployment.transport import FakeTransport


def model_directory(tmp_path):
    root = tmp_path / "vosk-model-small-it-0.22"
    for relative in ("am/final.mdl", "conf/model.conf", "graph/HCLr.fst", "graph/Gr.fst"):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    return root


def profile(tmp_path) -> DeviceProfile:
    return DeviceProfile({
        "DEVICE_ID": "one", "DEVICE_HOSTNAME": "one", "WIFI_SSID": "wifi",
        "WIFI_PASSWORD": "wifi-secret", "WIFI_COUNTRY": "IT", "TARGET_USER": "leolm",
        "LEOLM_CONVERSATION_API_KEY": "api-secret",
        "LEOLM_MODEL": "test/model", "LEOLM_LANGUAGE": "it-IT", "LEOLM_WAKE_WORD": "Panda",
        "LEOLM_VOSK_MODEL_PATH": str(model_directory(tmp_path)), "LEOLM_WAKE_SAMPLE_RATE": "16000",
        "LEOLM_INPUT_DEVICE": "input", "LEOLM_OUTPUT_DEVICE": "output",
    }, Path("profile.env"))


def test_plan_is_redacted_and_complete(tmp_path):
    plan = redacted_plan(profile(tmp_path), "ssh")
    rendered = str(plan)
    assert "api-secret" not in rendered
    assert "wifi-secret" not in rendered
    assert "opt/leolm/one/.env" in rendered
    assert "install-target-dependencies" in rendered


def test_ssh_provisioner_runs_complete_target_flow_without_real_ssh(tmp_path):
    transport = FakeTransport()
    report = SSHProvisioner("pi.local", transport=transport).provision(profile(tmp_path))
    assert report.state == "committed"
    assert any("pip" in call for call in transport.calls)
    assert any("import vosk" in " ".join(call) for call in transport.calls)
    model_check = next(index for index, call in enumerate(transport.calls) if any("am/final.mdl" in item for item in call))
    service_enable = next(index for index, call in enumerate(transport.calls) if "systemctl" in call and "enable" in call)
    assert model_check < service_enable
    assert any("systemctl" in call and "enable" in call for call in transport.calls)
    assert all("api-secret" not in " ".join(call) for call in transport.calls)


def test_ssh_quotes_remote_shell_script_as_one_argument(monkeypatch):
    captured = {}

    def run(command, **kwargs):
        captured["command"] = command
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr("leolm.deployment.ssh.subprocess.run", run)
    SSHProvisioner("pi.local")._ssh("sh", "-c", "test -d /opt/leolm/one")
    assert captured["command"][-1] == "'test -d /opt/leolm/one'"
