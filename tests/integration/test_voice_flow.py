from types import SimpleNamespace

import pytest

from leolm.application import VoiceApplication
from leolm.errors import AudioError
from leolm.session import VoiceSession
from tests.fakes.adapters import FakeConversation


class WakeNotActivated:
    def wait_for_wake(self):
        raise AudioError("wake word not detected", "Wake word offline non rilevata")


class RecordingSpeech:
    def __init__(self):
        self.listen_calls = 0
        self.transcribe_calls = 0

    def listen(self, device, timeout, phrase_limit):
        self.listen_calls += 1
        return "audio"

    def transcribe(self, audio, language):
        self.transcribe_calls += 1
        return "ciao"


class UnexpectedAudio:
    def resolve(self, selector, role):
        raise AssertionError("command capture must wait for local wake activation")


class UnexpectedTTS:
    def synthesize(self, text, language):
        raise AssertionError("TTS must not run before local wake activation")


def test_local_wake_activation_gates_command_model_and_tts():
    """A missed local wake result cannot invoke remote or downstream adapters."""
    conversation = FakeConversation(["salve"])
    speech = RecordingSpeech()
    config = SimpleNamespace(input_selector="in", output_selector="out", language="it-IT")
    app = VoiceApplication(
        config,
        UnexpectedAudio(),
        WakeNotActivated(),
        speech,
        VoiceSession(conversation),
        UnexpectedTTS(),
    )

    with pytest.raises(AudioError, match="wake word not detected"):
        app.run_once()

    assert speech.listen_calls == 0
    assert speech.transcribe_calls == 0
    assert conversation.calls == []
