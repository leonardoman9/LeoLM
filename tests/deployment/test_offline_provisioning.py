from pathlib import Path

from leolm.deployment.offline import OfflineProvisioner
from leolm.deployment.profile import DeviceProfile


def model_directory(tmp_path):
    root = tmp_path / "vosk-model-small-it-0.22"
    for relative in ("am/final.mdl", "conf/model.conf", "graph/HCLr.fst", "graph/Gr.fst"):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    return root


def valid_profile(tmp_path):
    return DeviceProfile({
        "DEVICE_ID": "one", "DEVICE_HOSTNAME": "one", "WIFI_SSID": "wifi",
        "WIFI_PASSWORD": "fake-password", "WIFI_COUNTRY": "IT", "TARGET_USER": "leolm",
        "LEOLM_CONVERSATION_API_KEY": "fake-api",
        "LEOLM_MODEL": "test/model", "LEOLM_LANGUAGE": "it-IT", "LEOLM_WAKE_WORD": "Panda",
        "LEOLM_VOSK_MODEL_PATH": str(model_directory(tmp_path)), "LEOLM_WAKE_SAMPLE_RATE": "16000",
        "LEOLM_INPUT_DEVICE": "input", "LEOLM_OUTPUT_DEVICE": "output",
    }, Path("profile.env"))


def test_offline_provisioning_is_repeatable_and_protects_files(tmp_path):
    root = tmp_path / "target"
    root.mkdir()
    provisioner = OfflineProvisioner(root)
    first = provisioner.provision(valid_profile(tmp_path))
    second = provisioner.provision(valid_profile(tmp_path))
    assert first.state == second.state == "committed"
    env = root / "opt/leolm/one/.env"
    assert env.exists()
    assert env.stat().st_mode & 0o777 == 0o600
    assert (root / "etc/NetworkManager/system-connections/LeoLM-one.nmconnection").stat().st_mode & 0o777 == 0o600
    assert (root / "etc/systemd/system/leolm.service").exists()
    assert (root / "opt/leolm/one/models/vosk-model-small-it-0.22/am/final.mdl").is_file()
    assert (root / "opt/leolm/one/deploy/assets/vosk-model-small-it-0.22.lock.json").is_file()


def test_cross_architecture_stages_bootstrap(tmp_path):
    root = tmp_path / "target"
    root.mkdir()
    report = OfflineProvisioner(root).provision(valid_profile(tmp_path))
    assert report.state == "committed"
    assert (root / "opt/leolm/one/.bootstrap-pending").exists()
