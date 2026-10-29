from pathlib import Path


def test_operational_docs_mention_context_and_provider_limits():
    text = "\n".join(Path(path).read_text(encoding="utf-8") for path in ("docs/privacy.md", "docs/troubleshooting.md"))
    assert "600" in text
    assert "provider" in text.lower()
    assert "retry" in text.lower()
