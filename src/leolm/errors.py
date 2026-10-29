"""Domain errors and secret-safe user messages."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LeoLMError(Exception):
    message: str
    user_message: str | None = None
    retryable: bool = False

    def __str__(self) -> str:
        return self.message

    @property
    def safe_message(self) -> str:
        return self.user_message or self.message


class ConfigurationError(LeoLMError):
    pass


class AudioError(LeoLMError):
    pass


class ExternalServiceError(LeoLMError):
    pass


def redact(value: object, secrets: tuple[str, ...] = ()) -> str:
    text = str(value)
    for secret in secrets:
        if secret:
            text = text.replace(secret, "[REDACTED]")
    return text
