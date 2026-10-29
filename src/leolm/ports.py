"""Small protocols used to keep hardware and services replaceable."""

from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Protocol, Sequence


class Closable(Protocol):
    def close(self) -> None: ...


class AudioPort(Protocol):
    def resolve(self, selector: str | None, role: str) -> object: ...
    def listen(self, device: object, timeout: float, phrase_limit: float) -> object: ...
    def play(self, device: object, audio_path: str) -> None: ...


class WakeWordPort(Protocol):
    def listen(self) -> None: ...
    def close(self) -> None: ...


class SpeechPort(Protocol):
    def transcribe(self, audio: object, language: str) -> str: ...


class ConversationPort(Protocol):
    def complete(self, turns: Sequence[dict[str, str]]) -> str: ...


class TTSport(Protocol):
    def synthesize(self, text: str, language: str) -> AbstractContextManager[str]: ...
