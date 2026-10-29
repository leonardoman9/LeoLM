from types import SimpleNamespace

from leolm.wakeword import PorcupineWakeWord


def test_wakeword_rejects_missing_assets(tmp_path):
    config = SimpleNamespace(wake_word_path=tmp_path / "missing.ppn", wake_model_path=tmp_path / "missing.pv")
    try:
        PorcupineWakeWord(config, None).start()
    except Exception as exc:
        assert "Asset wake word" in exc.safe_message
    else:
        raise AssertionError("missing assets should fail")
