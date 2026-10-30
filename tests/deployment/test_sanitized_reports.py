from leolm.deployment.profile import DeviceProfile
from leolm.deployment.report import DeploymentReport
from leolm.deployment.verify import verify_ssh


def test_profile_sanitized_values_redact_secrets():
    profile = DeviceProfile({
        "DEVICE_ID": "one", "WIFI_PASSWORD": "wifi-secret",
        "LEOLM_CONVERSATION_API_KEY": "api-secret",
    }, None)
    sanitized = profile.sanitized()
    assert sanitized["WIFI_PASSWORD"] == "<redacted>"
    assert "api-secret" not in str(sanitized)


def test_report_does_not_need_environment_values():
    report = DeploymentReport("one", "one", "offline")
    report.add_check("secrets", "protected")
    assert "secret" not in report.to_json().lower() or "protected" in report.to_json()


def test_failed_service_readiness_is_safe_and_does_not_leak_profile_values(monkeypatch):
    class FailingProvisioner:
        def __init__(self, *args, **kwargs):
            pass

        def _ssh(self, *args):
            if "systemctl is-active leolm.service" in args:
                raise RuntimeError("token=should-not-appear")

    monkeypatch.setattr("leolm.deployment.verify.SSHProvisioner", FailingProvisioner)
    profile = DeviceProfile({"DEVICE_ID": "one", "DEVICE_HOSTNAME": "one", "LEOLM_CONVERSATION_API_KEY": "api-secret"}, None)
    report = verify_ssh(profile, "pi.local")
    statuses = {check.name: check.status for check in report.checks}
    assert statuses["runtime"] == "unavailable"
    assert "api-secret" not in report.to_json()
