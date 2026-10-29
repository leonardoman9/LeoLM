#!/usr/bin/env python3
"""Provision and verify LeoLM targets without exposing profile secrets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from leolm.deployment.errors import DeploymentError
from leolm.deployment.offline import OfflineProvisioner
from leolm.deployment.profile import load_profile
from leolm.deployment.ssh import SSHProvisioner
from leolm.deployment.manifest import redacted_plan
from leolm.deployment.verify import verify_offline, verify_ssh


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="leolm-deploy")
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("validate", "dry-run"):
        command = sub.add_parser(name)
        command.add_argument("--profile", required=True)
        command.add_argument("--target")
        command.add_argument("--json", action="store_true")
    offline = sub.add_parser("provision-offline")
    offline.add_argument("--profile", required=True)
    offline.add_argument("--root", required=True)
    offline.add_argument("--json", action="store_true")
    ssh = sub.add_parser("deploy-ssh")
    ssh.add_argument("--profile", required=True)
    ssh.add_argument("--host", required=True)
    ssh.add_argument("--user", default="pi")
    ssh.add_argument("--port", type=int, default=22)
    ssh.add_argument("--timeout", type=float, default=60.0)
    ssh.add_argument("--json", action="store_true")
    verify = sub.add_parser("verify")
    verify.add_argument("--profile", required=True)
    verify.add_argument("--target", required=True)
    verify.add_argument("--json", action="store_true")
    return p


def print_report(report, as_json: bool) -> None:
    if as_json:
        print(report.to_json())
        return
    print(f"device={report.device_id} host={report.hostname} transport={report.transport} state={report.state}")
    for check in report.checks:
        print(f"{check.name}: {check.status}")
    for error in report.errors:
        print(f"error: {error}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command in {"validate", "dry-run"}:
            profile = load_profile(args.profile, require_secrets=args.command == "validate")
            if args.command == "validate":
                print(json.dumps({"valid": True, "device_id": profile.device_id, "hostname": profile.hostname})) if args.json else print(f"valid: {profile.device_id} ({profile.hostname})")
                return 0
            plan = redacted_plan(profile, "ssh" if args.target else "offline")
            plan["dry_run"] = True
            if args.target:
                plan["target"] = args.target
            print(json.dumps(plan, ensure_ascii=False, indent=2) if args.json else "dry-run: no files changed")
            return 0
        profile = load_profile(args.profile)
        if args.command == "provision-offline":
            report = OfflineProvisioner(Path(args.root)).provision(profile)
        elif args.command == "deploy-ssh":
            report = SSHProvisioner(args.host, args.user, args.port, args.timeout).provision(profile)
        else:
            target = Path(args.target)
            if target.is_dir():
                report = verify_offline(profile, target)
            else:
                report = verify_ssh(profile, args.target)
        print_report(report, args.json)
        return 0 if not report.errors else 1
    except DeploymentError as exc:
        print(exc.safe_message, file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"operazione non riuscita: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
