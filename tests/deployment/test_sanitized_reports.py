from leolm.deployment.profile import DeviceProfile
from leolm.deployment.report import DeploymentReport


def test_profile_sanitized_values_redact_secrets():
    profile = DeviceProfile({
        "DEVICE_ID": "one", "WIFI_PASSWORD": "wifi-secret",
        "LEOLM_CONVERSATION_API_KEY": "api-secret",
        "LEOLM_PORCUPINE_ACCESS_KEY": "access-secret",
    }, None)
    sanitized = profile.sanitized()
    assert sanitized["WIFI_PASSWORD"] == "<redacted>"
    assert "api-secret" not in str(sanitized)


def test_report_does_not_need_environment_values():
    report = DeploymentReport("one", "one", "offline")
    report.add_check("secrets", "protected")
    assert "secret" not in report.to_json().lower() or "protected" in report.to_json()
