"""Sanitized deployment reports."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any


def redact(value: str) -> str:
    """Remove common credential-shaped values from arbitrary diagnostics."""
    import re
    value = re.sub(r"(?i)(api[_-]?key|password|token|access[_-]?key)(\s*[:=]\s*)\S+", r"\1\2<redacted>", value)
    return value


@dataclass
class Check:
    name: str
    status: str
    detail: str = ""


@dataclass
class DeploymentReport:
    device_id: str
    hostname: str
    transport: str
    state: str = "unvalidated"
    checks: list[Check] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_check(self, name: str, status: str, detail: str = "") -> None:
        self.checks.append(Check(name, status, redact(detail)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "hostname": self.hostname,
            "transport": self.transport,
            "state": self.state,
            "checks": [check.__dict__ for check in self.checks],
            "errors": [redact(item) for item in self.errors],
            "warnings": [redact(item) for item in self.warnings],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
