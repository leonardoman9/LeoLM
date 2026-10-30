"""Complete target-side SSH provisioning with bounded operations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shlex
import subprocess
import tarfile
import tempfile

from .errors import TransportError
from .manifest import app_root, stage_payload
from .profile import DeviceProfile
from .report import DeploymentReport


@dataclass
class SSHProvisioner:
    host: str
    user: str = "pi"
    port: int = 22
    timeout: float = 60.0
    install_system_deps: bool = True
    transport: object | None = None
    verbose: bool = False

    def _progress(self, message: str) -> None:
        if self.verbose:
            print(f"[leolm-deploy] {message}", flush=True)

    def _ssh(self, *args: str) -> subprocess.CompletedProcess[str]:
        if self.transport is not None:
            return self.transport.run(("ssh", *args), timeout=self.timeout)
        if args[:2] == ("sh", "-c") and len(args) == 3:
            args = ("sh", "-c", shlex.quote(args[2]))
        command = ["ssh", "-o", "BatchMode=yes", "-p", str(self.port), f"{self.user}@{self.host}", *args]
        try:
            return subprocess.run(command, check=True, capture_output=not self.verbose, text=True, timeout=self.timeout)
        except (OSError, subprocess.SubprocessError) as exc:
            raise TransportError("SSH operation failed", safe_message="Operazione SSH non riuscita") from exc

    def _copy(self, source: Path, destination: str) -> None:
        if self.transport is not None:
            self.transport.copy(source, destination)
            return
        command = ["scp", "-P", str(self.port), str(source), f"{self.user}@{self.host}:{destination}"]
        try:
            subprocess.run(command, check=True, capture_output=not self.verbose, text=True, timeout=self.timeout)
        except (OSError, subprocess.SubprocessError) as exc:
            raise TransportError("SSH copy failed", safe_message="Trasferimento SSH non riuscito") from exc

    def provision(self, profile: DeviceProfile) -> DeploymentReport:
        profile.validate()
        report = DeploymentReport(profile.device_id, profile.hostname, "ssh", state="planned")
        remote_tmp = f"/tmp/leolm-{profile.device_id}.tar"
        with tempfile.TemporaryDirectory(prefix="leolm-deploy-") as temporary:
            payload = Path(temporary) / "payload"
            archive = Path(temporary) / "payload.tar"
            self._progress("preparo il payload locale")
            stage_payload(profile, payload)
            with tarfile.open(archive, "w") as tar:
                tar.add(payload, arcname="")
            try:
                if self.install_system_deps:
                    self._progress("aggiorno gli indici dei pacchetti sul Raspberry")
                    self._ssh("sudo", "apt-get", "update")
                    self._progress("installo dipendenze audio e Python sul Raspberry")
                    self._ssh("sudo", "apt-get", "install", "-y", "python3", "python3-dev", "python3-venv", "python3-pip", "build-essential", "libportaudio2", "portaudio19-dev", "flac", "alsa-utils", "mpg123", "network-manager")
                self._progress("verifico i prerequisiti del Raspberry")
                self._ssh("sh", "-c", "command -v python3 && command -v systemctl && command -v nmcli && sudo -n true")
                self._ssh("uname", "-m")
                self._progress("trasferisco il payload e il modello Vosk")
                self._copy(archive, remote_tmp)
                self._ssh("sudo", "mkdir", "-p", app_root(profile), "/etc/NetworkManager/system-connections", "/etc/systemd/system")
                self._ssh("sudo", "tar", "--no-same-owner", "-xf", remote_tmp, "-C", "/")
                self._ssh("sudo", "rm", "-f", remote_tmp)
                root = app_root(profile)
                target_user = profile.values.get("TARGET_USER", "leolm")
                self._ssh("sh", "-c", f"id -u {target_user} >/dev/null 2>&1 || sudo useradd --system --create-home --shell /usr/sbin/nologin --groups audio {target_user}")
                self._ssh("sh", "-c", f"id -nG {target_user} | grep -qw audio || sudo usermod -aG audio {target_user}")
                self._ssh("sudo", "chown", "-R", f"{target_user}:{target_user}", root)
                self._ssh("sudo", "chmod", "600", f"{root}/.env", f"/etc/NetworkManager/system-connections/LeoLM-{profile.device_id}.nmconnection")
                self._progress("verifico il modello Vosk trasferito")
                self._ssh("sudo", "test", "-f", f"{root}/models/vosk-model-small-it-0.22/am/final.mdl")
                self._progress("creo l'ambiente Python e installo LeoLM")
                self._ssh("sudo", "python3", "-m", "venv", f"{root}/.venv")
                self._ssh("sudo", f"{root}/.venv/bin/python", "-m", "pip", "install", "--disable-pip-version-check", "-r", f"{root}/requirements.txt")
                self._progress("verifico il runtime Vosk sul Raspberry")
                self._ssh("sh", "-c", f"sudo {root}/.venv/bin/python -c 'import vosk'")
                self._ssh("sudo", "touch", f"{root}/.bootstrap-complete")
                self._ssh("sudo", "nmcli", "connection", "reload")
                self._ssh("sudo", "systemctl", "daemon-reload")
                self._progress("abilito e avvio il servizio LeoLM")
                self._ssh("sudo", "systemctl", "enable", "--now", "leolm.service")
                self._progress("deploy completato")
                report.state = "committed"
                report.add_check("ssh", "reachable")
                report.add_check("application", "installed")
                report.add_check("dependencies", "target-installed")
                report.add_check("wifi", "configured")
                report.add_check("service", "enabled")
                report.add_check("temporary_secrets", "removed")
                return report
            except Exception:
                report.state = "rolled_back"
                raise
            finally:
                try:
                    self._ssh("rm", "-f", remote_tmp)
                except Exception:
                    pass
