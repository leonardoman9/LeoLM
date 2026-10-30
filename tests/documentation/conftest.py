from pathlib import Path

import pytest


@pytest.fixture
def docs_root(tmp_path: Path) -> Path:
    (tmp_path / "docs").mkdir()
    (tmp_path / "examples").mkdir()
    (tmp_path / "deploy/profiles").mkdir(parents=True)
    config = """# Configuration
## Runtime variables
| Name | Required | Default | Format | Secret | Safe example | Effect and error behavior |
|---|---|---|---|---|---|---|
| `LEOLM_MODEL` | no | `model` | id | no | `test/model` | model |
| `LEOLM_VOSK_MODEL_PATH` | yes | `models/vosk-model-small-it-0.22` | directory | no | `models/vosk-model-small-it-0.22` | model |
## Deployment variables
| Name | Required | Default | Format | Secret | Safe example | Effect and error behavior |
|---|---|---|---|---|---|---|
| `DEVICE_ID` | yes | — | id | no | `test` | device |
"""
    (tmp_path / "docs/configuration.md").write_text(config, encoding="utf-8")
    for relative in ("readme.md", "docs/deployment.md", "docs/privacy.md", "docs/system-dependencies.md", "docs/troubleshooting.md", "docs/release-checklist.md"):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Document\n", encoding="utf-8")
    (tmp_path / "examples/.env.example").write_text("LEOLM_MODEL=model\nLEOLM_VOSK_MODEL_PATH=models/vosk-model-small-it-0.22\n", encoding="utf-8")
    (tmp_path / "deploy/profiles/example.env").write_text("LEOLM_MODEL=model\nLEOLM_VOSK_MODEL_PATH=models/vosk-model-small-it-0.22\nDEVICE_ID=test\n", encoding="utf-8")
    return tmp_path
