from types import SimpleNamespace

from leolm.application import VoiceApplication
from leolm.session import VoiceSession
from tests.fakes.adapters import FakeConversation


class FakeWake:
    def __init__(self):
        self.closed = False

    def wait_for_wake(self):
        return True

    def close(self):
        self.closed = True


class FakeAudio:
    def __init__(self):
        self.closed = False

    def resolve(self, selector, role):
        return (selector, role)

    def close(self):
        self.closed = True


class FakeSpeech:
    def listen(self, device, timeout, phrase_limit):
        return "audio"

    def transcribe(self, audio, language):
        return "ciao"


class FakeTTS:
    def __init__(self):
        self.played = []

    def synthesize(self, text, language):
        class Output:
            def __enter__(self):
                return "/tmp/response.mp3"

            def __exit__(self, *args):
                return False
        return Output()

    def play(self, path, selector):
        self.played.append((path, selector))


def test_application_runs_one_complete_voice_turn():
    config = SimpleNamespace(input_selector="in", output_selector="out", language="it-IT")
    wake, audio, tts = FakeWake(), FakeAudio(), FakeTTS()
    app = VoiceApplication(config, audio, wake, FakeSpeech(), VoiceSession(FakeConversation(["salve"])), tts)
    assert app.run_once() == "salve"
    assert tts.played == [("/tmp/response.mp3", "out")]
