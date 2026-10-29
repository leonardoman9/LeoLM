from leolm.config import load_config


def test_configuration_contract_defaults(fake_env):
    config = load_config(fake_env)
    assert config.language == "it-IT"
    assert config.retry_count == 2
    assert config.context_idle_timeout == 600


def test_configuration_contract_accepts_device_selectors(fake_env):
    fake_env["LEOLM_INPUT_DEVICE"] = "USB microphone"
    fake_env["LEOLM_OUTPUT_DEVICE"] = "speaker-name"
    config = load_config(fake_env)
    assert config.input_selector == "USB microphone"
    assert config.output_selector == "speaker-name"
