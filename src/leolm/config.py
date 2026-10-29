"""Validated environment configuration for LeoLM."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from .errors import ConfigurationError


def _env(env: dict[str, str], name: str, default: str | None = None) -> str | None:
    value = env.get(name, default)
    return value.strip() if isinstance(value, str) else value


def _positive_float(env: dict[str, str], name: str, default: float) -> float:
    raw = _env(env, name, str(default))
    try:
        value = float(raw or "")
    except ValueError as exc:
        raise ConfigurationError(f"Invalid numeric value for {name}", f"Configurazione non valida: {name}") from exc
    if value <= 0:
        raise ConfigurationError(f"{name} must be positive", f"Configurazione non valida: {name}")
    return value


def _non_negative_float(env: dict[str, str], name: str, default: float) -> float:
    value = _positive_float(env, name, default) if default else float(_env(env, name, "0") or "0")
    if value < 0:
        raise ConfigurationError(f"{name} must not be negative", f"Configurazione non valida: {name}")
    return value


@dataclass(frozen=True)
class RuntimeConfig:
    conversation_api_key: str | None
    porcupine_access_key: str | None
    model: str
    conversation_endpoint: str
    language: str
    wake_word: str
    wake_word_path: Path
    wake_model_path: Path
    input_selector: str | None
    output_selector: str | None
    network_timeout: float
    retry_count: int
    retry_backoff: float
    context_idle_timeout: float

    def safe_summary(self) -> dict[str, object]:
        return {
            "model": self.model,
            "conversation_endpoint": self.conversation_endpoint,
            "language": self.language,
            "wake_word": self.wake_word,
            "input_selector": self.input_selector,
            "output_selector": self.output_selector,
            "network_timeout": self.network_timeout,
            "retry_count": self.retry_count,
            "context_idle_timeout": self.context_idle_timeout,
            "conversation_api_key_set": bool(self.conversation_api_key),
            "porcupine_access_key_set": bool(self.porcupine_access_key),
        }


def load_config(env: dict[str, str] | None = None, *, require_services: bool = True) -> RuntimeConfig:
    values = dict(os.environ if env is None else env)
    endpoint = _env(values, "LEOLM_CONVERSATION_ENDPOINT", "https://openrouter.ai/api/v1/chat/completions")
    parsed = urlparse(endpoint or "")
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ConfigurationError("Invalid conversation endpoint", "Configurazione non valida: LEOLM_CONVERSATION_ENDPOINT")

    api_key = _env(values, "LEOLM_CONVERSATION_API_KEY", _env(values, "OPENAI_API_KEY"))
    porcupine_key = _env(values, "LEOLM_PORCUPINE_ACCESS_KEY", _env(values, "PORCUPINE_ACCESS_KEY"))
    if require_services and not api_key:
        raise ConfigurationError("Missing LEOLM_CONVERSATION_API_KEY", "Manca LEOLM_CONVERSATION_API_KEY")
    if require_services and not porcupine_key:
        raise ConfigurationError("Missing LEOLM_PORCUPINE_ACCESS_KEY", "Manca LEOLM_PORCUPINE_ACCESS_KEY")

    wake_path = Path(_env(values, "LEOLM_WAKE_WORD_PATH", "Panda_it_raspberry-pi_v3_0_0.ppn") or "")
    model_path = Path(_env(values, "LEOLM_WAKE_MODEL_PATH", "porcupine_params_it.pv") or "")
    retry_count_raw = _env(values, "LEOLM_RETRY_COUNT", "2")
    try:
        retry_count = int(retry_count_raw or "")
    except ValueError as exc:
        raise ConfigurationError("Invalid retry count", "Configurazione non valida: LEOLM_RETRY_COUNT") from exc
    if not 0 <= retry_count <= 2:
        raise ConfigurationError("LEOLM_RETRY_COUNT must be between 0 and 2", "Configurazione non valida: LEOLM_RETRY_COUNT")

    return RuntimeConfig(
        conversation_api_key=api_key,
        porcupine_access_key=porcupine_key,
        model=_env(values, "LEOLM_MODEL", "google/gemini-2.0-flash-thinking-exp:free") or "",
        conversation_endpoint=endpoint or "",
        language=_env(values, "LEOLM_LANGUAGE", "it-IT") or "it-IT",
        wake_word=_env(values, "LEOLM_WAKE_WORD", "Panda") or "Panda",
        wake_word_path=wake_path,
        wake_model_path=model_path,
        input_selector=_env(values, "LEOLM_INPUT_DEVICE"),
        output_selector=_env(values, "LEOLM_OUTPUT_DEVICE"),
        network_timeout=_positive_float(values, "LEOLM_NETWORK_TIMEOUT_SECONDS", 30),
        retry_count=retry_count,
        retry_backoff=_non_negative_float(values, "LEOLM_RETRY_BACKOFF_SECONDS", 1),
        context_idle_timeout=_positive_float(values, "LEOLM_CONTEXT_IDLE_TIMEOUT_SECONDS", 600),
    )


def validate_asset_paths(config: RuntimeConfig) -> None:
    for name, path in (("LEOLM_WAKE_WORD_PATH", config.wake_word_path), ("LEOLM_WAKE_MODEL_PATH", config.wake_model_path)):
        if not path.is_file():
            raise ConfigurationError(f"{name} is not readable", f"File configurato non disponibile: {name}")
