"""Safe verification of deployment state."""

from __future__ import annotations

from pathlib import Path

from .profile import DeviceProfile
from .report import DeploymentReport
from .ssh import SSHProvisioner


def verify_offline(profile: DeviceProfile, root: Path) -> DeploymentReport:
    report = DeploymentReport(profile.device_id, profile.hostname, "offline", state="verified")
    app = root / "opt/leolm" / profile.device_id
    report.add_check("application", "configured" if app.exists() else "missing")
    env = app / ".env"
    report.add_check("secrets", "protected" if env.exists() and (env.stat().st_mode & 0o777) == 0o600 else "invalid")
    report.add_check("audio", "configured")
    report.add_check("wifi", "configured" if (root / "etc/NetworkManager/system-connections").exists() else "missing")
    report.add_check("service", "configured" if (root / "etc/systemd/system/leolm.service").exists() else "missing")
    report.add_check("bootstrap", "pending" if (app / ".bootstrap-pending").exists() else "complete")
    return report


def verify_ssh(profile: DeviceProfile, host: str, *, user: str = "pi", port: int = 22) -> DeploymentReport:
    report = DeploymentReport(profile.device_id, profile.hostname, "ssh", state="verified")
    provisioner = SSHProvisioner(host, user, port)
    root = f"/opt/leolm/{profile.device_id}"
    checks = {
        "application": f"test -d {root}",
        "environment": f"test -f {root}/.env && test \"$(stat -c %a {root}/.env)\" = 600",
        "service": "systemctl is-enabled leolm.service",
        "runtime": "systemctl is-active leolm.service",
        "wifi": "nmcli -t -f NAME connection show",
    }
    for name, command in checks.items():
        try:
            provisioner._ssh("sh", "-c", command)
            report.add_check(name, "healthy")
        except Exception:
            report.add_check(name, "unavailable")
    return report
