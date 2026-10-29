from leolm.errors import redact


def test_redact_removes_all_secret_values():
    assert redact("key=test-only-api-key token=test-only-porcupine-key", ("test-only-api-key", "test-only-porcupine-key")) == "key=[REDACTED] token=[REDACTED]"
