from leolm.deployment.profile import DeviceProfile
from leolm.deployment.render import bootstrap_script, service_unit


def test_bootstrap_is_one_shot_after_network():
    profile = DeviceProfile({"DEVICE_ID": "one", "TARGET_USER": "leolm"}, None)
    unit = service_unit(profile, bootstrap=True)
    assert "Type=oneshot" in unit
    assert "After=network-online.target" in unit
    assert "RemainAfterExit=yes" in unit


def test_bootstrap_disables_itself_after_success():
    assert "systemctl', 'disable', '--now', 'leolm-bootstrap.service'" in bootstrap_script()
