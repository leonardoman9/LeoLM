from __future__ import annotations

import pytest


@pytest.fixture
def fake_env(tmp_path):
    model = tmp_path / "vosk-model"
    for relative in ("am/final.mdl", "conf/model.conf", "graph/HCLr.fst", "graph/Gr.fst"):
        path = model / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    return {
        "LEOLM_CONVERSATION_API_KEY": "test-only-api-key",
        "LEOLM_VOSK_MODEL_PATH": str(model),
        "LEOLM_WAKE_SAMPLE_RATE": "16000",
        "LEOLM_INPUT_DEVICE": "fake-input",
        "LEOLM_OUTPUT_DEVICE": "fake-output",
    }
