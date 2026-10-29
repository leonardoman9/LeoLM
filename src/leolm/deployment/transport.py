"""Injectable command and file transport used by deployment backends."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Sequence

from .errors import TransportError


@dataclass
class LocalTransport:
    timeout: float = 30.0

    def run(self, command: Sequence[str], *, timeout: float | None = None) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(list(command), check=True, capture_output=True, text=True,
                                  timeout=timeout or self.timeout)
        except (OSError, subprocess.SubprocessError) as exc:
            raise TransportError("local command failed", safe_message="Comando locale non riuscito") from exc


@dataclass
class FakeTransport:
    """Small test transport; records operations and optionally fails a command."""

    fail_on: str | None = None
    calls: list[tuple[str, ...]] | None = None

    def __post_init__(self) -> None:
        if self.calls is None:
            self.calls = []

    def run(self, command: Sequence[str], *, timeout: float | None = None) -> subprocess.CompletedProcess[str]:
        assert self.calls is not None
        call = tuple(command)
        self.calls.append(call)
        if self.fail_on and self.fail_on in call:
            raise TransportError("fake command failed", safe_message="Comando target non riuscito")
        return subprocess.CompletedProcess(list(command), 0, "", "")

    def copy(self, source: Path, destination: str) -> None:
        assert self.calls is not None
        self.calls.append(("copy", str(source), destination))
