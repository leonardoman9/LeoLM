from .test_configuration_contract import load_checker


def test_unknown_variable_is_error(docs_root):
    (docs_root / "examples/.env.example").write_text("UNKNOWN_VALUE=x\n", encoding="utf-8")
    report = load_checker().validate(docs_root)
    assert any(item.code == "UNKNOWN_ENV" for item in report.errors)
