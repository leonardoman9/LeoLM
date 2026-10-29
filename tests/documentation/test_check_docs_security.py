from .test_configuration_contract import load_checker


def test_placeholder_and_secret_are_errors_in_normal_document(docs_root):
    (docs_root / "docs/deployment.md").write_text("token=real-token-value\nTODO replace this\n", encoding="utf-8")
    report = load_checker().validate(docs_root)
    codes = {item.code for item in report.errors}
    assert "SECRET_PATTERN" in codes
    assert "PLACEHOLDER" in codes


def test_json_report_contains_no_secret_value(docs_root):
    checker = load_checker()
    report = checker.validate(docs_root)
    assert "real-secret" not in report.as_dict().__repr__()
