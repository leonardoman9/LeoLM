"""Systemd installation helpers."""

from __future__ import annotations

from pathlib import Path
import os
import subprocess

from .errors import DeploymentError
from .profile import DeviceProfile
from .render import service_unit


def write_service_units(profile: DeviceProfile, root: Path) -> list[Path]:
    directory = root / "etc/systemd/system"
    directory.mkdir(parents=True, exist_ok=True)
    outputs = []
    for name, bootstrap in (("leolm.service", False), ("leolm-bootstrap.service", True)):
        target = directory / name
        target.write_text(service_unit(profile, bootstrap=bootstrap), encoding="utf-8")
        target.chmod(0o644)
        outputs.append(target)
    return outputs


def install_user(root: Path, user: str = "leolm") -> None:
    """Record the desired account for offline images; create it on live targets."""
    marker = root / "etc/leolm-service-user"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(user + "\n", encoding="utf-8")
    marker.chmod(0o644)


def systemctl(action: str, unit: str, *, runner=subprocess.run) -> None:
    try:
        runner(["systemctl", action, unit], check=True, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        raise DeploymentError("systemd operation failed", safe_message=f"Operazione systemd non riuscita: {action} {unit}") from exc
