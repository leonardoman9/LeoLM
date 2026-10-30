"""Offline Vosk wake-word adapter with lazy audio initialization."""

from __future__ import annotations

import json
import re
import struct

from .config import validate_vosk_model_path
from .errors import AudioError, ConfigurationError


def _decimate_pcm16(data: bytes, factor: int) -> bytes:
    """Downsample 16-bit PCM by keeping every *factor*-th sample."""
    if factor <= 1:
        return data
    samples = struct.unpack(f"<{len(data) // 2}h", data)
    decimated = samples[::factor]
    return struct.pack(f"<{len(decimated)}h", *decimated)


def _normalise(value: str) -> str:
    return " ".join(re.findall(r"[\w]+", value.casefold(), flags=re.UNICODE))


class VoskWakeWord:
    def __init__(self, config, audio_manager, backend=None):
        self.config = config
        self.audio_manager = audio_manager
        self._backend = backend
        self._model = None
        self._recognizer = None
        self._stream = None
        self._decimate_factor = 1

    def start(self):
        try:
            validate_vosk_model_path(self.config)
            if self._backend is None:
                import vosk
                self._backend = vosk
            if hasattr(self._backend, "SetLogLevel"):
                self._backend.SetLogLevel(-1)
            self._model = self._backend.Model(str(self.config.vosk_model_path))
            grammar = json.dumps([_normalise(self.config.wake_word)], ensure_ascii=False)
            self._recognizer = self._backend.KaldiRecognizer(self._model, self.config.wake_sample_rate, grammar)
            if hasattr(self._recognizer, "SetWords"):
                self._recognizer.SetWords(False)
            device = self.audio_manager.resolve(self.config.input_selector, "input")
            hw_rate = device.sample_rate
            target_rate = self.config.wake_sample_rate
            # Pick a stream rate that the hardware supports and is an
            # integer multiple of the Vosk target rate.  Preference order:
            # native rate (if divisible), then common multiples.
            candidates = [hw_rate, 48000, 32000, 16000]
            stream_rate = target_rate
            self._decimate_factor = 1
            for candidate in candidates:
                if candidate >= target_rate and candidate % target_rate == 0:
                    stream_rate = candidate
                    self._decimate_factor = candidate // target_rate
                    break
            frames = 4000 * self._decimate_factor
            self._stream = self.audio_manager.open_input(device, rate=stream_rate, frames=frames)
        except Exception as exc:
            self.close()
            if isinstance(exc, ConfigurationError):
                raise AudioError("Offline wake-word model is unavailable", "Modello wake word non disponibile") from exc
            if isinstance(exc, AudioError):
                raise
            raise AudioError("Unable to initialize offline wake word", "Wake word offline non disponibile") from exc
        return self

    def _matches(self, result: str) -> bool:
        try:
            payload = json.loads(result)
        except (TypeError, ValueError):
            return False
        text = payload.get("text") or payload.get("partial") or ""
        return _normalise(str(text)) == _normalise(self.config.wake_word)

    def wait_for_wake(self) -> bool:
        if self._recognizer is None:
            self.start()
        if self._stream is None:
            raise AudioError("Wake-word microphone is not available", "Microfono non disponibile")
        while True:
            try:
                pcm = self._stream.resource.read(4000 * self._decimate_factor, exception_on_overflow=False)
                if not pcm:
                    raise ValueError("empty PCM frame")
                pcm = _decimate_pcm16(pcm, self._decimate_factor)
                completed = self._recognizer.AcceptWaveform(pcm)
                result = self._recognizer.Result() if completed else self._recognizer.PartialResult()
                if self._matches(result):
                    self.close()
                    return True
            except AudioError:
                self.close()
                raise
            except Exception as exc:
                self.close()
                raise AudioError("Wake-word microphone read failed", "Ascolto wake word non riuscito") from exc

    def close(self) -> None:
        if self._stream is not None:
            try:
                self._stream.close()
            finally:
                self._stream = None
        self._recognizer = None
        self._model = None
