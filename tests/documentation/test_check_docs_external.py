from .test_configuration_contract import load_checker


def test_external_link_warning_does_not_fail(docs_root, monkeypatch):
    checker = load_checker()
    (docs_root / "readme.md").write_text("[external](https://example.invalid/nope)\n", encoding="utf-8")
    monkeypatch.setattr(checker, "urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("offline")))
    report = checker.validate(docs_root, check_external=True)
    assert not report.errors
    assert any(item.code == "EXTERNAL_LINK_UNREACHABLE" for item in report.warnings)
