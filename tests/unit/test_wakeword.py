from types import SimpleNamespace

import pytest

from leolm.audio import ResourceLease
from leolm.errors import AudioError
from leolm.wakeword import VoskWakeWord


def model_directory(tmp_path):
    root = tmp_path / "model"
    for relative in ("am/final.mdl", "conf/model.conf", "graph/HCLr.fst", "graph/Gr.fst"):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    return root


class FakeRecognizer:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.words_disabled = False

    def SetWords(self, value):
        self.words_disabled = value is False

    def AcceptWaveform(self, pcm):
        return False

    def PartialResult(self):
        return next(self.responses)

    def Result(self):
        return '{"text": ""}'


class FakeBackend:
    def __init__(self, responses):
        self.responses = responses
        self.grammar = None
        self.log_level = None

    def SetLogLevel(self, level):
        self.log_level = level

    def Model(self, path):
        return {"path": path}

    def KaldiRecognizer(self, model, rate, grammar):
        self.grammar = grammar
        self.rate = rate
        return FakeRecognizer(self.responses)


class FakeStream:
    def __init__(self):
        self.closed = False
        self.last_frames = None

    def read(self, frames, exception_on_overflow=False):
        self.last_frames = frames
        assert exception_on_overflow is False
        # Return enough int16 samples for the requested frame count.
        import struct
        return struct.pack(f"<{frames}h", *([100] * frames))

    def close(self):
        self.closed = True


class FakeAudio:
    def __init__(self, hw_rate=16000):
        self.stream = FakeStream()
        self.opened = None
        self._hw_rate = hw_rate

    def resolve(self, selector, role):
        assert selector == "USB microphone"
        assert role == "input"
        return SimpleNamespace(index=0, name="fake", role=role, sample_rate=self._hw_rate, channels=1)

    def open_input(self, device, *, rate, frames):
        self.opened = (rate, frames)
        return ResourceLease(self.stream)


def config(tmp_path, **overrides):
    values = {
        "wake_word": "Panda",
        "vosk_model_path": model_directory(tmp_path),
        "wake_sample_rate": 16000,
        "input_selector": "USB microphone",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_wakeword_rejects_missing_model(tmp_path):
    wakeword = VoskWakeWord(config(tmp_path, vosk_model_path=tmp_path / "missing"), FakeAudio(), FakeBackend([]))
    with pytest.raises(AudioError) as error:
        wakeword.start()
    assert error.value.safe_message == "Modello wake word non disponibile"


def test_wakeword_preserves_unavailable_microphone_error(tmp_path):
    class UnavailableAudio:
        def resolve(self, selector, role):
            raise AudioError("input unavailable", "Microfono non disponibile")

    wakeword = VoskWakeWord(config(tmp_path), UnavailableAudio(), FakeBackend([]))
    with pytest.raises(AudioError) as error:
        wakeword.start()
    assert error.value.safe_message == "Microfono non disponibile"


def test_wakeword_reads_microphone_until_exact_panda(tmp_path):
    audio = FakeAudio()
    backend = FakeBackend(['{"partial": "rumore"}', '{"partial": "PANDA"}'])
    wakeword = VoskWakeWord(config(tmp_path), audio, backend)

    assert wakeword.wait_for_wake() is True
    assert audio.opened == (16000, 4000)
    assert backend.grammar == '["panda"]'
    assert audio.stream.closed is True


def test_wakeword_rejects_substring_and_releases_stream_on_error(tmp_path):
    audio = FakeAudio()
    backend = FakeBackend(['{"partial": "panda rosso"}', "not-json"])
    wakeword = VoskWakeWord(config(tmp_path), audio, backend)
    wakeword.start()
    with pytest.raises(AudioError) as error:
        wakeword.wait_for_wake()
    assert error.value.safe_message == "Ascolto wake word non riuscito"
    wakeword.close()
    wakeword.close()
    assert audio.stream.closed is True


def test_wakeword_decimates_when_hw_rate_not_divisible(tmp_path):
    """hw_rate=44100 is not a multiple of 16000, so code should pick 48000 and decimate by 3."""
    audio = FakeAudio(hw_rate=44100)
    backend = FakeBackend(['{"partial": "panda"}'])
    wakeword = VoskWakeWord(config(tmp_path), audio, backend)

    assert wakeword.wait_for_wake() is True
    assert audio.opened == (48000, 12000)
    assert wakeword._decimate_factor == 3


def test_wakeword_no_decimation_when_hw_matches_target(tmp_path):
    """hw_rate=16000 matches target, so no decimation needed."""
    audio = FakeAudio(hw_rate=16000)
    backend = FakeBackend(['{"partial": "panda"}'])
    wakeword = VoskWakeWord(config(tmp_path), audio, backend)

    assert wakeword.wait_for_wake() is True
    assert audio.opened == (16000, 4000)
