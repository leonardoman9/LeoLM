from pathlib import Path

import pytest

from leolm.config import load_config, validate_vosk_model_path
from leolm.errors import ConfigurationError


def test_load_config_validates_environment(fake_env):
    config = load_config(fake_env)
    assert config.model
    assert config.context_idle_timeout == 600
    assert config.retry_count == 2


def test_missing_secret_is_reported_without_value(fake_env):
    fake_env.pop("LEOLM_CONVERSATION_API_KEY")
    with pytest.raises(ConfigurationError, match="LEOLM_CONVERSATION_API_KEY"):
        load_config(fake_env)


@pytest.mark.parametrize("name,value", [("LEOLM_RETRY_COUNT", "3"), ("LEOLM_NETWORK_TIMEOUT_SECONDS", "0"), ("LEOLM_WAKE_SAMPLE_RATE", "0")])
def test_invalid_ranges_are_rejected(fake_env, name, value):
    fake_env[name] = value
    with pytest.raises(ConfigurationError):
        load_config(fake_env)


def test_vosk_model_path_is_validated_without_exposing_configuration(fake_env, tmp_path):
    fake_env["LEOLM_VOSK_MODEL_PATH"] = str(tmp_path / "missing-model")
    with pytest.raises(ConfigurationError) as error:
        validate_vosk_model_path(load_config(fake_env))
    assert error.value.safe_message == "Modello wake word non disponibile"
