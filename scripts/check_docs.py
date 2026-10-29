#!/usr/bin/env python3
"""Offline documentation consistency checker for LeoLM."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse
from urllib.request import Request, urlopen

TABLE_COLUMNS = ("Name", "Required", "Default", "Format", "Secret", "Safe example", "Effect and error behavior")
REQUIRED_DOCS = (
    "readme.md", "docs/configuration.md", "docs/deployment.md", "docs/privacy.md",
    "docs/system-dependencies.md", "docs/troubleshooting.md", "docs/release-checklist.md",
)
ENV_FILES = ("examples/.env.example", "deploy/profiles/example.env")
APPROVED_PLACEHOLDER_FILES = {"docs/configuration.md", *ENV_FILES}
PLACEHOLDER_RE = re.compile(r"(?:replace-on-device|your-(?:api|key|token)-here|\b(?:TODO|TBD|TKTK)\b|<placeholder>)", re.I)
SECRET_RE = re.compile(r"(?:api[_ -]?key|access[_ -]?key|password|token)\s*[:=]\s*(?!<redacted>|replace-on-device|your-[^\s\x60]+|—|-)\S+", re.I)
FORBIDDEN_RE = re.compile(r"(?:\bsudo\b|\brm\s+-rf\b|(?:api[_ -]?key|password|token)\s*[:=]\s*(?!replace-on-device|<redacted>|your-)[^<\x60\s]+|\b(?:mcp|telnet|nc)\s+--?listen)", re.I)
LINK_RE = re.compile(r"!?[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
ENV_RE = re.compile(r"^\s*([A-Z][A-Z0-9_]*)\s*=")


@dataclass
class Finding:
    severity: str
    code: str
    file: str
    line: int
    message: str


class Report:
    def __init__(self) -> None:
        self.findings: list[Finding] = []
        self.files_scanned = 0

    def add(self, severity: str, code: str, file: str, line: int, message: str) -> None:
        self.findings.append(Finding(severity, code, file, line, message))

    @property
    def errors(self) -> list[Finding]:
        return [item for item in self.findings if item.severity == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [item for item in self.findings if item.severity == "warning"]

    def as_dict(self) -> dict[str, object]:
        return {
            "files_scanned": self.files_scanned,
            "passed": not self.errors,
            "errors": [asdict(item) for item in self.errors],
            "warnings": [asdict(item) for item in self.warnings],
        }


def parse_contract(path: Path, report: Report) -> dict[str, dict[str, str]]:
    contract: dict[str, dict[str, str]] = {}
    scope = ""
    lines = path.read_text(encoding="utf-8").splitlines()
    for number, line in enumerate(lines, 1):
        heading = re.match(r"^##\s+(Runtime variables|Deployment variables)\s*$", line)
        if heading:
            scope = "runtime" if heading.group(1).startswith("Runtime") else "deployment"
            continue
        if not scope or not line.startswith("|"):
            continue
        cells = [cell.strip().strip(chr(96)) for cell in line.strip().strip("|").split("|")]
        if cells[: len(TABLE_COLUMNS)] == list(TABLE_COLUMNS):
            continue
        if all(set(cell) <= {"-", ":", " "} for cell in cells):
            continue
        if len(cells) != len(TABLE_COLUMNS) or not re.fullmatch(r"[A-Z][A-Z0-9_]+", cells[0]):
            if line.count("|") >= 2:
                report.add("error", "INVALID_CONFIG_TABLE", str(path), number, "Riga della tabella di configurazione non valida")
            continue
        contract[cells[0]] = {"scope": scope, "required": cells[1], "default": cells[2], "secret": cells[4]}
    if not contract:
        report.add("error", "MISSING_CONFIG_TABLE", str(path), 1, "Nessuna tabella canonica di configurazione trovata")
    return contract


def iter_document_files(root: Path) -> list[Path]:
    result = [root / path for path in REQUIRED_DOCS]
    result.extend(sorted((root / "docs").glob("*.md")))
    result.extend(sorted((root / "deploy").rglob("*.md")))
    result.extend(root / path for path in ENV_FILES)
    return list(dict.fromkeys(path for path in result if path.is_file()))


def check_links(path: Path, text: str, root: Path, report: Report, external: bool) -> None:
    for number, line in enumerate(text.splitlines(), 1):
        for target in LINK_RE.findall(line):
            if target.startswith("#"):
                continue
            parsed = urlparse(target)
            if parsed.scheme in {"http", "https"}:
                if external:
                    try:
                        request = Request(target, method="HEAD", headers={"User-Agent": "LeoLM-doc-check"})
                        with urlopen(request, timeout=5):
                            pass
                    except Exception as exc:
                        report.add("warning", "EXTERNAL_LINK_UNREACHABLE", str(path.relative_to(root)), number, f"URL esterno non raggiungibile: {parsed.netloc} ({type(exc).__name__})")
                continue
            local = (path.parent / target.split("#", 1)[0]).resolve()
            if not local.exists():
                report.add("error", "BROKEN_LOCAL_LINK", str(path.relative_to(root)), number, f"Link locale non valido: {target}")


def check_file(path: Path, root: Path, contract: dict[str, dict[str, str]], report: Report) -> None:
    text = path.read_text(encoding="utf-8")
    relative = str(path.relative_to(root))
    report.files_scanned += 1
    for number, line in enumerate(text.splitlines(), 1):
        if relative not in APPROVED_PLACEHOLDER_FILES and PLACEHOLDER_RE.search(line):
            report.add("error", "PLACEHOLDER", relative, number, "Placeholder non sostituito")
        if SECRET_RE.search(line):
            report.add("error", "SECRET_PATTERN", relative, number, "Possibile valore sensibile nel documento")
        if FORBIDDEN_RE.search(line):
            report.add("error", "FORBIDDEN_COMMAND", relative, number, "Comando o procedura non consentita")
        match = ENV_RE.match(line)
        if match and (path.name.startswith(".env") or path.name.endswith(".env")):
            key = match.group(1)
            if key not in contract:
                report.add("error", "UNKNOWN_ENV", relative, number, f"Variabile non presente nel contratto: {key}")
            elif relative == "examples/.env.example" and contract[key]["scope"] != "runtime":
                report.add("error", "WRONG_ENV_SCOPE", relative, number, f"Variabile deployment nel template runtime: {key}")
    check_links(path, text, root, report, False)


def validate(root: Path, check_external: bool = False) -> Report:
    report = Report()
    contract_path = root / "docs/configuration.md"
    if not contract_path.is_file():
        report.add("error", "MISSING_DOCUMENT", "docs/configuration.md", 1, "Documento canonico mancante")
        return report
    contract = parse_contract(contract_path, report)
    for required in REQUIRED_DOCS:
        if not (root / required).is_file():
            report.add("error", "MISSING_DOCUMENT", required, 1, "Documento richiesto mancante")
    for path in iter_document_files(root):
        check_file(path, root, contract, report)
        if check_external and path.suffix == ".md":
            check_links(path, path.read_text(encoding="utf-8"), root, report, True)
    for key, entry in contract.items():
        if entry["required"] == "yes" and not any(
            re.search(rf"^\s*{re.escape(key)}\s*=", (root / env).read_text(encoding="utf-8"), re.M)
            for env in ENV_FILES if (root / env).is_file()
        ):
            report.add("error", "MISSING_REQUIRED_ENV", "docs/configuration.md", 1, f"Variabile obbligatoria senza template: {key}")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check-external-links", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = validate(args.root.resolve(), args.check_external_links)
        if args.json:
            print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2))
        else:
            for finding in report.findings:
                print(f"{finding.severity}: {finding.file}:{finding.line}: {finding.code}: {finding.message}")
            print(f"scanned={report.files_scanned} errors={len(report.errors)} warnings={len(report.warnings)}")
        return 1 if report.errors else 0
    except (OSError, UnicodeError, ValueError):
        if args.json:
            print(json.dumps({"error": "internal validator error"}))
        else:
            print("validator error", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
