#!/usr/bin/env python3
"""Fetch and verify the public Italian Vosk model on the deployment PC."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import time
from urllib.request import urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "deploy/assets/vosk-model-small-it-0.22.lock.json"
REQUIRED_FILES = ("am/final.mdl", "conf/model.conf", "graph/HCLr.fst", "graph/Gr.fst")


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def safe_extract(archive: Path, destination: Path) -> Path:
    with zipfile.ZipFile(archive) as bundle:
        members = bundle.infolist()
        if any(member.is_dir() is False and Path(member.filename).is_absolute() for member in members):
            raise ValueError("archive contains an absolute path")
        target_root = destination.resolve()
        for member in members:
            member_path = (destination / member.filename).resolve()
            if target_root not in member_path.parents and member_path != target_root:
                raise ValueError("archive contains an unsafe path")
        bundle.extractall(destination)
    roots = [path for path in destination.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise ValueError("archive must contain exactly one model directory")
    return roots[0]


def download(url: str, archive: Path, *, verbose: bool) -> None:
    """Download the public archive while emitting bounded, non-sensitive progress."""
    with urlopen(url, timeout=120) as response, archive.open("wb") as output:
        size = int(response.headers.get("Content-Length", "0"))
        received = 0
        announced = 0
        last_report = time.monotonic()
        while block := response.read(1024 * 1024):
            output.write(block)
            received += len(block)
            if verbose and (received - announced >= 5 * 1024 * 1024 or time.monotonic() - last_report >= 5):
                total = f"/{size / 1024 / 1024:.1f} MiB" if size else ""
                print(f"[leolm-deploy] download Vosk: {received / 1024 / 1024:.1f} MiB{total}", flush=True)
                announced = received
                last_report = time.monotonic()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", required=True)
    parser.add_argument("--archive", type=Path, help="archivio Vosk locale da verificare ed estrarre")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    destination = Path(args.destination).resolve()
    if destination.exists():
        if all((destination / item).is_file() for item in REQUIRED_FILES):
            print("[leolm-deploy] modello Vosk locale già disponibile" if args.verbose else "Vosk model already verified")
            return 0
        raise SystemExit("Destination exists but is not a complete Vosk model")
    with tempfile.TemporaryDirectory(prefix="leolm-vosk-") as temporary:
        archive = args.archive.resolve() if args.archive else Path(temporary) / "model.zip"
        if args.archive:
            if not archive.is_file():
                raise SystemExit("Local Vosk model archive is unavailable")
            if args.verbose:
                print("[leolm-deploy] riuso l'archivio Vosk locale", flush=True)
        else:
            if args.verbose:
                print("[leolm-deploy] scarico il modello italiano Vosk", flush=True)
            download(lock["source_url"], archive, verbose=args.verbose)
        if args.verbose:
            print("[leolm-deploy] verifico l'integrità SHA-256 del modello", flush=True)
        if archive.stat().st_size > lock["max_archive_bytes"] or digest(archive) != lock["sha256"]:
            raise SystemExit("Vosk model integrity check failed")
        if args.verbose:
            print("[leolm-deploy] estraggo il modello Vosk", flush=True)
        extracted = safe_extract(archive, Path(temporary) / "extracted")
        if any(not (extracted / item).is_file() for item in REQUIRED_FILES):
            raise SystemExit("Vosk model archive is incomplete")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(extracted), destination)
    print("[leolm-deploy] modello Vosk verificato" if args.verbose else "Vosk model verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

