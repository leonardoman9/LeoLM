from __future__ import annotations

from contextlib import contextmanager


class FakeConversation:
    def __init__(self, replies=None):
        self.replies = list(replies or ["risposta"])
        self.calls = []

    def complete(self, turns):
        self.calls.append(list(turns))
        return self.replies.pop(0) if self.replies else "risposta"


class FakeAudio:
    def __init__(self):
        self.resolved = []

    def resolve(self, selector, role):
        device = (role, selector or "default")
        self.resolved.append(device)
        return device


class FakeWakeWord:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class FakeSpeech:
    def __init__(self, text="ciao"):
        self.text = text

    def transcribe(self, audio, language):
        return self.text


class FakeTTS:
    @contextmanager
    def synthesize(self, text, language):
        yield "/tmp/fake-leolm.mp3"
