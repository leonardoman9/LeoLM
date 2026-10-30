"""Opt-in local Vosk model check; run only on the provisioned Raspberry Pi."""

import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.hardware


def test_vosk_model_is_configured_and_complete():
    model = Path(os.getenv("LEOLM_VOSK_MODEL_PATH", "models/vosk-model-small-it-0.22"))
    required = ("am/final.mdl", "conf/model.conf", "graph/HCLr.fst", "graph/Gr.fst")
    assert all((model / item).is_file() for item in required), "Install the verified local Vosk model first"


def test_vosk_runtime_is_importable():
    pytest.importorskip("vosk")

