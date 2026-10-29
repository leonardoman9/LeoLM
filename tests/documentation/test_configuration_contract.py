import importlib.util
from pathlib import Path
import sys


def load_checker():
    spec = importlib.util.spec_from_file_location("check_docs", Path("scripts/check_docs.py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_contract_has_two_scopes(docs_root):
    checker = load_checker()
    report = checker.Report()
    contract = checker.parse_contract(docs_root / "docs/configuration.md", report)
    assert contract["LEOLM_MODEL"]["scope"] == "runtime"
    assert contract["DEVICE_ID"]["scope"] == "deployment"
    assert not report.errors
