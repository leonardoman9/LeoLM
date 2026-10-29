from leolm.deployment.profile import DeviceProfile
from leolm.deployment.render import service_unit


def test_service_has_network_ordering_and_restart_limits():
    profile = DeviceProfile({"DEVICE_ID": "one", "TARGET_USER": "leolm"}, None)
    unit = service_unit(profile)
    assert "After=network-online.target" in unit
    assert "Restart=on-failure" in unit
    assert "StartLimitBurst=3" in unit
    assert "User=leolm" in unit
