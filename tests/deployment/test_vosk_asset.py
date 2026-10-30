import importlib.util
from pathlib import Path
import zipfile

import pytest


def load_fetcher():
    path = Path("scripts/fetch-vosk-model.py")
    spec = importlib.util.spec_from_file_location("fetch_vosk_model", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_extracts_complete_model_from_safe_archive(tmp_path):
    fetcher = load_fetcher()
    archive = tmp_path / "model.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        for relative in fetcher.REQUIRED_FILES:
            bundle.writestr(f"vosk-model-small-it-0.22/{relative}", "fixture")
    output = tmp_path / "output"
    output.mkdir()

    model = fetcher.safe_extract(archive, output)

    assert (model / "am/final.mdl").is_file()
    assert model.name == "vosk-model-small-it-0.22"


def test_rejects_archive_path_traversal(tmp_path):
    fetcher = load_fetcher()
    archive = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("../escape", "bad")
    output = tmp_path / "output"
    output.mkdir()

    with pytest.raises(ValueError, match="unsafe"):
        fetcher.safe_extract(archive, output)


def test_download_writes_the_public_response_without_logging_its_url(tmp_path, monkeypatch, capsys):
    fetcher = load_fetcher()

    class Response:
        headers = {"Content-Length": "3"}

        def read(self, size):
            if getattr(self, "read_once", False):
                return b""
            self.read_once = True
            return b"abc"

        def __enter__(self):
            self.read_once = False
            return self

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(fetcher, "urlopen", lambda *args, **kwargs: Response())
    archive = tmp_path / "model.zip"
    fetcher.download("https://example.invalid/model.zip", archive, verbose=True)
    assert archive.read_bytes() == b"abc"
    assert "example.invalid" not in capsys.readouterr().out

