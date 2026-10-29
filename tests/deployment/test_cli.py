import subprocess
import sys
from pathlib import Path


def test_validate_cli_rejects_placeholder_without_printing_it(tmp_path):
    profile = tmp_path / "profile.env"
    profile.write_text(Path("deploy/profiles/example.env").read_text(encoding="utf-8"), encoding="utf-8")
    result = subprocess.run([sys.executable, "scripts/leolm-deploy.py", "validate", "--profile", str(profile)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "replace-on-device" not in result.stderr
