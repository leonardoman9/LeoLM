"""Render target files from a validated profile."""

from __future__ import annotations

from pathlib import Path
import re

from .profile import DeviceProfile


def runtime_env(profile: DeviceProfile) -> str:
    lines = []
    for key, value in sorted(profile.runtime_environment().items()):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + "\n"


def wifi_keyfile(profile: DeviceProfile) -> str:
    ssid = profile.values["WIFI_SSID"].replace("\\", "\\\\").replace('"', '\\"')
    password = profile.values["WIFI_PASSWORD"].replace("\\", "\\\\").replace('"', '\\"')
    hidden = profile.values.get("WIFI_HIDDEN", "false").lower()
    return "\n".join([
        "[connection]", f"id=LeoLM-{profile.device_id}", "type=wifi", "autoconnect=true", "",
        "[wifi]", f'ssid="{ssid}"', f"hidden={hidden}", "", "[wifi-security]",
        "key-mgmt=wpa-psk", f'psk="{password}"', "", "[ipv4]", "method=auto", "",
        "[ipv6]", "method=auto", "",
    ])


def service_unit(profile: DeviceProfile, *, bootstrap: bool = False) -> str:
    user = profile.values.get("TARGET_USER", "leolm")
    root = f"/opt/leolm/{profile.device_id}"
    if bootstrap:
        return f"""[Unit]
Description=LeoLM dependency bootstrap ({profile.device_id})
Wants=network-online.target
After=network-online.target
ConditionPathExists={root}/requirements.txt

[Service]
Type=oneshot
User=root
WorkingDirectory={root}
ExecStart=/usr/bin/python3 {root}/deploy/bootstrap.py
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
"""
    return f"""[Unit]
Description=LeoLM voice assistant ({profile.device_id})
Wants=network-online.target leolm-bootstrap.service
After=network-online.target leolm-bootstrap.service

[Service]
Type=simple
User={user}
Group={user}
WorkingDirectory={root}
EnvironmentFile={root}/.env
ExecStart={root}/.venv/bin/python {root}/openai_request.py
Restart=on-failure
RestartSec=10
StartLimitIntervalSec=300
StartLimitBurst=3
NoNewPrivileges=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
"""


def bootstrap_script(profile: DeviceProfile | None = None) -> str:
    user = profile.values.get("TARGET_USER", "leolm") if profile else "leolm"
    return f"""#!/usr/bin/env python3
from pathlib import Path
import platform
import subprocess
import sys

root = Path(__file__).resolve().parent.parent
venv = root / '.venv'
if (root / '.bootstrap-complete').exists():
    raise SystemExit(0)
subprocess.run(['apt-get', 'update'], check=True)
subprocess.run(['apt-get', 'install', '-y', 'python3', 'python3-venv', 'python3-pip', 'libportaudio2', 'portaudio19-dev', 'flac', 'alsa-utils', 'network-manager'], check=True)
subprocess.run(['id', '-u', '{user}'], check=False)
if subprocess.run(['id', '-u', '{user}'], check=False).returncode != 0:
    subprocess.run(['useradd', '--system', '--create-home', '--shell', '/usr/sbin/nologin', '{user}'], check=True)
subprocess.run([sys.executable, '-m', 'venv', str(venv)], check=True)
subprocess.run([str(venv / 'bin' / 'python'), '-m', 'pip', 'install', '--disable-pip-version-check', '-r', str(root / 'requirements.txt')], check=True)
(root / '.bootstrap-pending').unlink(missing_ok=True)
(root / '.bootstrap-complete').write_text(platform.machine() + '\\n', encoding='utf-8')
subprocess.run(['systemctl', 'disable', '--now', 'leolm-bootstrap.service'], check=False)
subprocess.run(['systemctl', 'enable', '--now', 'leolm.service'], check=False)
"""
