from pathlib import Path

from leolm.deployment.offline import OfflineProvisioner
from leolm.deployment.profile import DeviceProfile


def valid_profile():
    return DeviceProfile({
        "DEVICE_ID": "one", "DEVICE_HOSTNAME": "one", "WIFI_SSID": "wifi",
        "WIFI_PASSWORD": "fake-password", "WIFI_COUNTRY": "IT", "TARGET_USER": "leolm",
        "LEOLM_CONVERSATION_API_KEY": "fake-api", "LEOLM_PORCUPINE_ACCESS_KEY": "fake-access",
        "LEOLM_MODEL": "test/model", "LEOLM_LANGUAGE": "it-IT", "LEOLM_WAKE_WORD": "Panda",
        "LEOLM_WAKE_WORD_PATH": "wake.ppn", "LEOLM_WAKE_MODEL_PATH": "model.pv",
        "LEOLM_INPUT_DEVICE": "input", "LEOLM_OUTPUT_DEVICE": "output",
    }, Path("profile.env"))


def test_offline_provisioning_is_repeatable_and_protects_files(tmp_path):
    root = tmp_path / "target"
    root.mkdir()
    provisioner = OfflineProvisioner(root)
    first = provisioner.provision(valid_profile())
    second = provisioner.provision(valid_profile())
    assert first.state == second.state == "committed"
    env = root / "opt/leolm/one/.env"
    assert env.exists()
    assert env.stat().st_mode & 0o777 == 0o600
    assert (root / "etc/NetworkManager/system-connections/LeoLM-one.nmconnection").stat().st_mode & 0o777 == 0o600
    assert (root / "etc/systemd/system/leolm.service").exists()


def test_cross_architecture_stages_bootstrap(tmp_path):
    root = tmp_path / "target"
    root.mkdir()
    report = OfflineProvisioner(root).provision(valid_profile())
    assert report.state == "committed"
    assert (root / "opt/leolm/one/.bootstrap-pending").exists()
