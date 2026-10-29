import subprocess
import sys


def test_cli_success_on_repository():
    result = subprocess.run([sys.executable, "scripts/check_docs.py", "--root", ".", "--json"], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_cli_invalid_option_returns_two():
    result = subprocess.run([sys.executable, "scripts/check_docs.py", "--not-a-real-option"], capture_output=True, text=True)
    assert result.returncode == 2
