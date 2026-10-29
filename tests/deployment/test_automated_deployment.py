from pathlib import Path

from leolm.deployment.manifest import redacted_plan
from leolm.deployment.profile import DeviceProfile
from leolm.deployment.ssh import SSHProvisioner
from leolm.deployment.transport import FakeTransport


def profile() -> DeviceProfile:
    return DeviceProfile({
        "DEVICE_ID": "one", "DEVICE_HOSTNAME": "one", "WIFI_SSID": "wifi",
        "WIFI_PASSWORD": "wifi-secret", "WIFI_COUNTRY": "IT", "TARGET_USER": "leolm",
        "LEOLM_CONVERSATION_API_KEY": "api-secret", "LEOLM_PORCUPINE_ACCESS_KEY": "access-secret",
        "LEOLM_MODEL": "test/model", "LEOLM_LANGUAGE": "it-IT", "LEOLM_WAKE_WORD": "Panda",
        "LEOLM_WAKE_WORD_PATH": "wake.ppn", "LEOLM_WAKE_MODEL_PATH": "model.pv",
        "LEOLM_INPUT_DEVICE": "input", "LEOLM_OUTPUT_DEVICE": "output",
    }, Path("profile.env"))


def test_plan_is_redacted_and_complete():
    plan = redacted_plan(profile(), "ssh")
    rendered = str(plan)
    assert "api-secret" not in rendered
    assert "wifi-secret" not in rendered
    assert "opt/leolm/one/.env" in rendered
    assert "install-target-dependencies" in rendered


def test_ssh_provisioner_runs_complete_target_flow_without_real_ssh():
    transport = FakeTransport()
    report = SSHProvisioner("pi.local", transport=transport).provision(profile())
    assert report.state == "committed"
    assert any("pip" in call for call in transport.calls)
    assert any("systemctl" in call and "enable" in call for call in transport.calls)
    assert all("api-secret" not in " ".join(call) for call in transport.calls)
