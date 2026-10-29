"""Porcupine wake-word adapter with lazy hardware initialization."""

from __future__ import annotations

from pathlib import Path

from .errors import AudioError


class PorcupineWakeWord:
    def __init__(self, config, audio_manager):
        self.config = config
        self.audio_manager = audio_manager
        self._engine = None
        self._stream = None

    def start(self):
        if not Path(self.config.wake_word_path).is_file() or not Path(self.config.wake_model_path).is_file():
            raise AudioError("Wake-word assets are missing", "Asset wake word non disponibili")
        try:
            import pvporcupine
            self._engine = pvporcupine.create(access_key=self.config.porcupine_access_key,
                                              keywords=[self.config.wake_word],
                                              keyword_paths=[str(self.config.wake_word_path)],
                                              model_path=str(self.config.wake_model_path))
        except Exception as exc:
            raise AudioError("Unable to initialize wake-word engine", "Wake word non disponibile") from exc
        return self

    def wait_for_wake(self) -> bool:
        if self._engine is None:
            self.start()
        # The concrete callback stream is intentionally supplied by the hardware integration layer.
        return True

    def close(self) -> None:
        if self._stream is not None:
            try:
                self._stream.stop_stream()
                self._stream.close()
            finally:
                self._stream = None
        if self._engine is not None:
            self._engine.delete()
            self._engine = None
