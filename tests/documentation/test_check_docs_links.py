from .test_configuration_contract import load_checker


def test_local_broken_link_is_error(docs_root):
    (docs_root / "readme.md").write_text("[missing](missing.md)\n", encoding="utf-8")
    report = load_checker().validate(docs_root)
    assert any(item.code == "BROKEN_LOCAL_LINK" and item.severity == "error" for item in report.findings)
