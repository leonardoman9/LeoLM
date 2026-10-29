from pathlib import Path

import pytest

from leolm.deployment.errors import ProfileError
from leolm.deployment.profile import load_profile


def profile_text(**overrides):
    values = {
        "DEVICE_ID": "pi-one", "DEVICE_HOSTNAME": "leolm-one", "WIFI_SSID": "test-wifi",
        "WIFI_PASSWORD": "fake-wifi-password", "WIFI_COUNTRY": "IT",
        "LEOLM_CONVERSATION_API_KEY": "fake-api-key", "LEOLM_PORCUPINE_ACCESS_KEY": "fake-access-key",
        "LEOLM_MODEL": "test/model", "LEOLM_LANGUAGE": "it-IT", "LEOLM_WAKE_WORD": "Panda",
        "LEOLM_WAKE_WORD_PATH": "wake.ppn", "LEOLM_WAKE_MODEL_PATH": "model.pv",
        "LEOLM_INPUT_DEVICE": "input", "LEOLM_OUTPUT_DEVICE": "output",
    }
    values.update(overrides)
    return "\n".join(f"{key}={value}" for key, value in values.items()) + "\n"


def test_loads_two_independent_profiles(tmp_path):
    first = tmp_path / "one.env"
    second = tmp_path / "two.env"
    first.write_text(profile_text(DEVICE_ID="one", DEVICE_HOSTNAME="one"), encoding="utf-8")
    second.write_text(profile_text(DEVICE_ID="two", DEVICE_HOSTNAME="two"), encoding="utf-8")
    assert load_profile(first).device_id == "one"
    assert load_profile(second).device_id == "two"


@pytest.mark.parametrize("key", ["DEVICE_HOSTNAME", "WIFI_COUNTRY", "LEOLM_CONVERSATION_API_KEY"])
def test_invalid_profile_names_field_without_secret(tmp_path, key):
    path = tmp_path / "invalid.env"
    overrides = {key: "" if key != "DEVICE_HOSTNAME" else "bad host"}
    path.write_text(profile_text(**overrides), encoding="utf-8")
    with pytest.raises(ProfileError) as error:
        load_profile(path)
    assert key in error.value.safe_message
    assert "fake" not in error.value.safe_message


def test_template_can_be_inspected_without_accepting_placeholders():
    template = Path("deploy/profiles/example.env")
    with pytest.raises(ProfileError):
        load_profile(template)
