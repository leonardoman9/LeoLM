"""NetworkManager operations and safe Wi-Fi status checks."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

from .errors import DeploymentError
from .profile import DeviceProfile
from .render import wifi_keyfile


def write_wifi_keyfile(profile: DeviceProfile, root: Path) -> Path:
    destination = root / "etc/NetworkManager/system-connections" / f"LeoLM-{profile.device_id}.nmconnection"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(wifi_keyfile(profile), encoding="utf-8")
    destination.chmod(0o600)
    return destination


def nmcli_available() -> bool:
    return shutil.which("nmcli") is not None


def apply_wifi(profile: DeviceProfile, runner=None) -> None:
    if runner is None:
        runner = subprocess.run
    args = ["nmcli", "connection", "reload"]
    try:
        runner(args, check=True, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        raise DeploymentError("NetworkManager reload failed", safe_message="Impossibile ricaricare NetworkManager") from exc
