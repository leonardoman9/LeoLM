"""Conversation context and voice-session coordination."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class ConversationContext:
    timeout: float = 600
    clock: callable = time.monotonic
    turns: list[dict[str, str]] = field(default_factory=list)
    last_activity: float | None = None

    def expire_if_idle(self, now: float | None = None, in_flight: bool = False) -> bool:
        if in_flight or self.last_activity is None:
            return False
        current = self.clock() if now is None else now
        if current - self.last_activity >= self.timeout:
            self.clear()
            return True
        return False

    def messages(self) -> list[dict[str, str]]:
        self.expire_if_idle()
        return list(self.turns)

    def add_turn(self, user: str, assistant: str, now: float | None = None) -> None:
        self.turns.extend(({"role": "user", "content": user}, {"role": "assistant", "content": assistant}))
        self.last_activity = self.clock() if now is None else now

    def clear(self) -> None:
        self.turns.clear()
        self.last_activity = None


class VoiceSession:
    def __init__(self, conversation, *, context=None):
        self.conversation = conversation
        self.context = context or ConversationContext()

    def process(self, text: str) -> str:
        self.context.expire_if_idle()
        turns = self.context.messages() + [{"role": "user", "content": text}]
        reply = self.conversation.complete(turns)
        self.context.add_turn(text, reply)
        return reply
