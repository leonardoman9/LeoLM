"""Profile parsing and validation without leaking secret values."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
from typing import Mapping
from urllib.parse import urlparse

from ..config import load_config
from .errors import ProfileError

SECRET_KEYS = frozenset({"WIFI_PASSWORD", "LEOLM_CONVERSATION_API_KEY"})
REQUIRED_KEYS = frozenset({
    "DEVICE_ID", "DEVICE_HOSTNAME", "WIFI_SSID", "WIFI_PASSWORD", "WIFI_COUNTRY",
    "LEOLM_CONVERSATION_API_KEY", "LEOLM_MODEL", "LEOLM_LANGUAGE", "LEOLM_WAKE_WORD",
    "LEOLM_VOSK_MODEL_PATH", "LEOLM_WAKE_SAMPLE_RATE",
    "LEOLM_INPUT_DEVICE", "LEOLM_OUTPUT_DEVICE",
})
ALLOWED_KEYS = REQUIRED_KEYS | frozenset({
    "LEOLM_CONVERSATION_ENDPOINT", "LEOLM_NETWORK_TIMEOUT_SECONDS", "LEOLM_RETRY_COUNT",
    "LEOLM_RETRY_BACKOFF_SECONDS", "LEOLM_CONTEXT_IDLE_TIMEOUT_SECONDS", "TARGET_USER",
    "TARGET_ROOT", "SSH_USER", "SSH_PORT", "TARGET_ARCH", "WIFI_HIDDEN",
})
HOSTNAME_RE = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$")
PLACEHOLDERS = {"replace-on-device", "your-api-key-here", "change-me", "TODO"}


def _parse_env(path: Path) -> dict[str, str]:
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ProfileError("Cannot read profile", safe_message=f"Impossibile leggere il profilo: {path}") from exc
    values: dict[str, str] = {}
    for line_number, line in enumerate(raw.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            raise ProfileError("Invalid profile line", safe_message=f"Riga non valida nel profilo: {line_number}")
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not re.fullmatch(r"[A-Z][A-Z0-9_]+", key):
            raise ProfileError("Invalid profile key", safe_message=f"Nome variabile non valido alla riga {line_number}")
        values[key] = value
    return values


@dataclass(frozen=True)
class DeviceProfile:
    values: dict[str, str]
    source: Path

    @property
    def device_id(self) -> str: return self.values["DEVICE_ID"]
    @property
    def hostname(self) -> str: return self.values["DEVICE_HOSTNAME"]
    @property
    def target_arch(self) -> str: return self.values.get("TARGET_ARCH", "armhf")
    @property
    def secrets(self) -> dict[str, str]: return {key: self.values.get(key, "") for key in SECRET_KEYS}

    def runtime_environment(self) -> dict[str, str]:
        return {key: value for key, value in self.values.items() if key.startswith("LEOLM_") and value}

    def sanitized(self) -> dict[str, str]:
        return {key: ("<redacted>" if key in SECRET_KEYS else value) for key, value in self.values.items()}

    def validate(self, *, require_secrets: bool = True) -> None:
        unknown = set(self.values) - ALLOWED_KEYS
        if unknown:
            raise ProfileError("Unknown profile keys", safe_message=f"Variabili non supportate: {', '.join(sorted(unknown))}")
        missing = sorted(key for key in REQUIRED_KEYS if key not in self.values)
        if missing:
            raise ProfileError("Missing profile keys", safe_message=f"Variabili mancanti: {', '.join(missing)}")
        if not HOSTNAME_RE.fullmatch(self.hostname) or len(self.hostname) > 63:
            raise ProfileError("Invalid hostname", safe_message="DEVICE_HOSTNAME non è un hostname valido")
        if not self.values["DEVICE_ID"].replace("-", "").replace("_", "").isalnum():
            raise ProfileError("Invalid device id", safe_message="DEVICE_ID contiene caratteri non validi")
        if len(self.values["WIFI_COUNTRY"]) != 2 or not self.values["WIFI_COUNTRY"].isalpha():
            raise ProfileError("Invalid Wi-Fi country", safe_message="WIFI_COUNTRY deve essere un codice di due lettere")
        if require_secrets:
            for key in SECRET_KEYS:
                value = self.values.get(key, "")
                if not value or value in PLACEHOLDERS:
                    raise ProfileError("Missing secret", safe_message=f"Manca il valore per {key}")
        endpoint = self.values.get("LEOLM_CONVERSATION_ENDPOINT", "https://openrouter.ai/api/v1/chat/completions")
        parsed = urlparse(endpoint)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ProfileError("Invalid endpoint", safe_message="LEOLM_CONVERSATION_ENDPOINT non è valido")
        try:
            load_config(self.values, require_services=False)
        except Exception as exc:
            raise ProfileError("Invalid LeoLM configuration", safe_message="La configurazione LeoLM non è valida") from exc


def load_profile(path: str | Path, *, require_secrets: bool = True) -> DeviceProfile:
    source = Path(path)
    values = _parse_env(source)
    profile = DeviceProfile(values, source)
    profile.validate(require_secrets=require_secrets)
    return profile
