from pathlib import Path

import pytest

from leolm.config import load_config
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


@pytest.mark.parametrize("name,value", [("LEOLM_RETRY_COUNT", "3"), ("LEOLM_NETWORK_TIMEOUT_SECONDS", "0")])
def test_invalid_ranges_are_rejected(fake_env, name, value):
    fake_env[name] = value
    with pytest.raises(ConfigurationError):
        load_config(fake_env)
