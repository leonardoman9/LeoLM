from pathlib import Path


def test_automatic_suite_has_no_hardware_install_commands():
    root = Path(__file__).parents[2]
    for path in (root / "tests" / "unit").rglob("*.py"):
        text = path.read_text()
        assert "sudo apt-get" not in text
        assert "pyaudio.PyAudio" not in text
