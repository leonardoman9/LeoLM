"""Opt-in wake-word asset and credential check."""

import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.hardware


def test_wake_word_assets_are_configured():
    key = os.getenv("LEOLM_PORCUPINE_ACCESS_KEY") or os.getenv("PORCUPINE_ACCESS_KEY")
    path = Path(os.getenv("LEOLM_WAKE_WORD_PATH", "Panda_it_raspberry-pi_v3_0_0.ppn"))
    assert key, "Set a Porcupine key only for the opt-in hardware test"
    assert path.is_file(), f"Wake-word asset is missing: {path}"
