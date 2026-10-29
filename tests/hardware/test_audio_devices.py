"""Opt-in hardware test; run with pytest -m hardware tests/hardware."""

import pytest

pytestmark = pytest.mark.hardware


def test_real_audio_devices_are_available():
    pyaudio = pytest.importorskip("pyaudio")
    pa = pyaudio.PyAudio()
    try:
        assert pa.get_device_count() >= 1
    finally:
        pa.terminate()
