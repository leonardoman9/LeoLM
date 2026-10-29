from __future__ import annotations

import pytest


@pytest.fixture
def fake_env(tmp_path):
    return {
        "LEOLM_CONVERSATION_API_KEY": "test-only-api-key",
        "LEOLM_PORCUPINE_ACCESS_KEY": "test-only-porcupine-key",
        "LEOLM_WAKE_WORD_PATH": str(tmp_path / "wake.ppn"),
        "LEOLM_WAKE_MODEL_PATH": str(tmp_path / "model.pv"),
        "LEOLM_INPUT_DEVICE": "fake-input",
        "LEOLM_OUTPUT_DEVICE": "fake-output",
    }
