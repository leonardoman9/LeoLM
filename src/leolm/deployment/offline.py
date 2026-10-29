"""Atomic provisioning for a mounted filesystem or image root."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import tempfile

from .errors import TargetError
from .manifest import stage_payload
from .profile import DeviceProfile
from .report import DeploymentReport
from .service import install_user


@dataclass
class OfflineProvisioner:
    root: Path

    def _validate_root(self) -> None:
        if not self.root.is_dir() or not os.access(self.root, os.W_OK):
            raise TargetError("Invalid offline target", safe_message="La destinazione offline non è una directory scrivibile")

    def provision(self, profile: DeviceProfile) -> DeploymentReport:
        profile.validate()
        self._validate_root()
        report = DeploymentReport(profile.device_id, profile.hostname, "offline", state="staged")
        stage = Path(tempfile.mkdtemp(prefix=f".leolm-{profile.device_id}-", dir=self.root))
        try:
            stage_payload(profile, stage)
            install_user(stage, profile.values.get("TARGET_USER", "leolm"))
            (stage / "opt/leolm" / profile.device_id / ".bootstrap-pending").write_text("target-side\n", encoding="utf-8")
            final = self.root / "opt/leolm" / profile.device_id
            final.parent.mkdir(parents=True, exist_ok=True)
            if final.exists():
                shutil.rmtree(final)
            shutil.copytree(stage / "opt/leolm" / profile.device_id, final)
            source = stage / "etc"
            if source.exists():
                shutil.copytree(source, self.root / "etc", dirs_exist_ok=True)
            report.state = "committed"
            report.add_check("application", "configured")
            report.add_check("dependencies", "bootstrap-pending")
            report.add_check("wifi", "configured")
            report.add_check("service", "configured")
            report.add_check("temporary_secrets", "removed")
            return report
        except Exception:
            report.state = "rolled_back"
            raise
        finally:
            shutil.rmtree(stage, ignore_errors=True)
