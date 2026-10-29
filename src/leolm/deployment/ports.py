"""Small interfaces used to isolate local filesystems and remote execution."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, Sequence


class TargetFileSystem(Protocol):
    root: Path

    def write_text(self, relative: str, content: str, mode: int = 0o644) -> None: ...


class CommandRunner(Protocol):
    def run(self, args: Sequence[str], *, timeout: float = 30.0, check: bool = True) -> str: ...


class Transport(Protocol):
    name: str

    def provision(self, profile: object) -> object: ...

    def verify(self, profile: object) -> object: ...
