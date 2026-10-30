"""Shared deployment payload and redacted planning."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil

from .errors import DeploymentError
from .profile import DeviceProfile
from .render import bootstrap_script, runtime_env, service_unit, wifi_keyfile


@dataclass(frozen=True)
class ManagedFile:
    relative: str
    mode: int
    secret: bool = False


def app_root(profile: DeviceProfile) -> str:
    return f"/opt/leolm/{profile.device_id}"


def manifest(profile: DeviceProfile) -> tuple[ManagedFile, ...]:
    root = app_root(profile).lstrip("/")
    return (
        ManagedFile(f"{root}/.env", 0o600, True),
        ManagedFile(f"etc/NetworkManager/system-connections/LeoLM-{profile.device_id}.nmconnection", 0o600, True),
        ManagedFile("etc/systemd/system/leolm.service", 0o644),
        ManagedFile("etc/systemd/system/leolm-bootstrap.service", 0o644),
        ManagedFile(f"{root}/deploy/bootstrap.py", 0o700),
        ManagedFile(f"{root}/models/vosk-model-small-it-0.22", 0o755),
        ManagedFile(f"{root}/deploy/assets/vosk-model-small-it-0.22.lock.json", 0o644),
    )


def stage_payload(profile: DeviceProfile, destination: Path) -> Path:
    """Create a complete payload with source and generated target files."""
    source_root = Path(__file__).resolve().parents[3]
    app = destination / "opt/leolm" / profile.device_id
    app.mkdir(parents=True, exist_ok=True)
    for name in ("src", "requirements.txt", "requirements-dev.txt", "openai_request.py", "setup.py", "pyproject.toml"):
        source = source_root / name
        if source.is_dir():
            shutil.copytree(source, app / name, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".venv", ".git"))
        elif source.is_file():
            shutil.copy2(source, app / name)
    deployed_values = dict(profile.values)
    configured = Path(profile.values["LEOLM_VOSK_MODEL_PATH"])
    source_model = configured if configured.is_absolute() else source_root / configured
    if not source_model.is_dir():
        raise DeploymentError("Vosk model is missing", safe_message="Modello wake word non disponibile per il deploy")
    target_model = app / "models" / "vosk-model-small-it-0.22"
    shutil.copytree(source_model, target_model, dirs_exist_ok=True)
    lock_source = source_root / "deploy/assets/vosk-model-small-it-0.22.lock.json"
    lock_target = app / "deploy/assets/vosk-model-small-it-0.22.lock.json"
    lock_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(lock_source, lock_target)
    deployed_values["LEOLM_VOSK_MODEL_PATH"] = "models/vosk-model-small-it-0.22"
    deployed_profile = DeviceProfile(deployed_values, profile.source)
    (app / ".env").write_text(runtime_env(deployed_profile), encoding="utf-8")
    (app / ".env").chmod(0o600)
    deploy = app / "deploy"
    deploy.mkdir(exist_ok=True)
    bootstrap = deploy / "bootstrap.py"
    bootstrap.write_text(bootstrap_script(profile), encoding="utf-8")
    bootstrap.chmod(0o700)
    nm = destination / "etc/NetworkManager/system-connections" / f"LeoLM-{profile.device_id}.nmconnection"
    nm.parent.mkdir(parents=True, exist_ok=True)
    nm.write_text(wifi_keyfile(profile), encoding="utf-8")
    nm.chmod(0o600)
    units = destination / "etc/systemd/system"
    units.mkdir(parents=True, exist_ok=True)
    (units / "leolm.service").write_text(service_unit(profile), encoding="utf-8")
    (units / "leolm-bootstrap.service").write_text(service_unit(profile, bootstrap=True), encoding="utf-8")
    return destination


def redacted_plan(profile: DeviceProfile, transport: str) -> dict[str, object]:
    return {
        "device_id": profile.device_id,
        "hostname": profile.hostname,
        "transport": transport,
        "architecture": "target-side-install",
        "application_root": app_root(profile),
        "managed_files": [{"path": item.relative, "mode": oct(item.mode), "secret": item.secret} for item in manifest(profile)],
        "actions": ["preflight", "verify-vosk-model", "copy-payload", "install-target-dependencies", "configure-wifi", "enable-service", "verify"],
    }
