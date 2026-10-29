"""Text-to-speech adapter with temporary-file cleanup."""

from __future__ import annotations

import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path

from .errors import ExternalServiceError


class GoogleTTS:
    def __init__(self, config, player: str = "mpg123"):
        self.config = config
        self.player = player

    @contextmanager
    def synthesize(self, text: str, language: str | None = None):
        path = None
        try:
            from gtts import gTTS
            with tempfile.NamedTemporaryFile(prefix="leolm-", suffix=".mp3", delete=False) as output:
                path = Path(output.name)
            gTTS(text=text, lang=(language or self.config.language).split("-")[0]).save(str(path))
            yield str(path)
        except Exception as exc:
            raise ExternalServiceError("Text-to-speech failed", "Sintesi vocale non riuscita") from exc
        finally:
            if path:
                path.unlink(missing_ok=True)

    def play(self, path: str, selector: str | None = None) -> None:
        command = [self.player]
        if selector:
            command.extend(["-a", selector])
        command.append(path)
        try:
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=self.config.network_timeout)
        except Exception as exc:
            raise ExternalServiceError("Audio playback failed", "Riproduzione audio non riuscita") from exc
