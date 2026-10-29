from leolm.deployment.profile import DeviceProfile
from leolm.deployment.render import service_unit


def test_restart_is_delayed_and_bounded():
    profile = DeviceProfile({"DEVICE_ID": "one", "TARGET_USER": "leolm"}, None)
    unit = service_unit(profile)
    assert "RestartSec=10" in unit
    assert "StartLimitIntervalSec=300" in unit


def test_service_is_single_unit_per_device():
    profile = DeviceProfile({"DEVICE_ID": "one", "TARGET_USER": "leolm"}, None)
    assert service_unit(profile).count("ExecStart=") == 1
