"""Speech-recognition adapters."""

from __future__ import annotations

import io
import struct
import wave

import numpy as np

from .errors import ExternalServiceError


def _pcm_to_wav16k(raw_data: bytes, sample_rate: int, sample_width: int = 2) -> str:
    """Convert raw PCM to a 16 kHz mono WAV temp file for Whisper."""
    import tempfile

    samples = np.frombuffer(raw_data, dtype=np.int16)
    if sample_rate != 16000:
        factor = sample_rate / 16000
        indices = np.arange(0, len(samples), factor).astype(int)
        indices = indices[indices < len(samples)]
        samples = samples[indices]

    path = tempfile.NamedTemporaryFile(prefix="leolm-stt-", suffix=".wav", delete=False).name
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(sample_width)
        wf.setframerate(16000)
        wf.writeframes(samples.tobytes())
    return path


class WhisperLocalRecognizer:
    """Offline speech-to-text using whisper.cpp via pywhispercpp."""

    def __init__(self, config, model=None):
        self.config = config
        self._model = model
        self._recognizer = None

    def _ensure_recognizer(self):
        if self._recognizer is None:
            try:
                import speech_recognition as sr
                self._recognizer = sr.Recognizer()
            except ImportError as exc:
                raise ExternalServiceError("SpeechRecognition is not installed",
                                           "Dipendenza audio non disponibile") from exc

    def _ensure_model(self):
        if self._model is None:
            try:
                from pywhispercpp.model import Model
                self._model = Model("tiny", print_realtime=False, print_progress=False)
            except Exception as exc:
                raise ExternalServiceError("Cannot load Whisper model",
                                           "Modello Whisper non disponibile") from exc

    def transcribe(self, audio, language: str | None = None) -> str:
        self._ensure_model()
        import os
        path = None
        try:
            raw = audio.get_raw_data()
            sample_rate = audio.sample_rate
            path = _pcm_to_wav16k(raw, sample_rate)
            lang = (language or self.config.language).split("-")[0]
            segments = self._model.transcribe(path, language=lang)
            text = " ".join(s.text.strip() for s in segments).strip()
        except ExternalServiceError:
            raise
        except Exception as exc:
            raise ExternalServiceError("Whisper transcription failed",
                                       "Trascrizione locale non riuscita") from exc
        finally:
            if path:
                try:
                    os.unlink(path)
                except OSError:
                    pass

        # Filter out whisper hallucinations on silence
        if not text or text in ("[Musica]", "(Musica)", "[Music]", "(Music)"):
            raise ExternalServiceError("Speech not understood", "Non ho capito, riprova")
        return text

    def listen(self, device, timeout: float = 5, phrase_limit: float = 5):
        self._ensure_recognizer()
        try:
            import speech_recognition as sr
            source = sr.Microphone(device_index=device.index, sample_rate=device.sample_rate, chunk_size=1024)
            with source as microphone:
                return self._recognizer.listen(microphone, timeout=timeout, phrase_time_limit=phrase_limit)
        except Exception as exc:
            raise ExternalServiceError("Unable to capture speech",
                                       "Ascolto del comando non riuscito") from exc


class GoogleSpeechRecognizer:
    def __init__(self, config, recognizer=None):
        self.config = config
        self.recognizer = recognizer

    def transcribe(self, audio, language: str | None = None) -> str:
        if self.recognizer is None:
            try:
                import speech_recognition as sr
                self.recognizer = sr.Recognizer()
            except ImportError as exc:
                raise ExternalServiceError("SpeechRecognition is not installed",
                                           "Riconoscimento vocale non disponibile") from exc
        try:
            import speech_recognition as sr
            text = self.recognizer.recognize_google(audio, language=language or self.config.language)
        except sr.UnknownValueError as exc:
            raise ExternalServiceError("Speech not understood", "Non ho capito, riprova") from exc
        except sr.RequestError as exc:
            raise ExternalServiceError("Google Speech API error",
                                       "Servizio di riconoscimento non raggiungibile") from exc
        except ExternalServiceError:
            raise
        except Exception as exc:
            raise ExternalServiceError("Speech recognition request failed",
                                       "Riconoscimento vocale non riuscito") from exc
        if not text or not text.strip():
            raise ExternalServiceError("Speech recognition returned empty text", "Non ho capito, riprova")
        return text.strip()

    def listen(self, device, timeout: float = 5, phrase_limit: float = 5):
        if self.recognizer is None:
            try:
                import speech_recognition as sr
                self.recognizer = sr.Recognizer()
            except ImportError as exc:
                raise ExternalServiceError("SpeechRecognition is not installed",
                                           "Riconoscimento vocale non disponibile") from exc
        try:
            import speech_recognition as sr
            source = sr.Microphone(device_index=device.index, sample_rate=device.sample_rate, chunk_size=1024)
            with source as microphone:
                return self.recognizer.listen(microphone, timeout=timeout, phrase_time_limit=phrase_limit)
        except Exception as exc:
            raise ExternalServiceError("Unable to capture speech",
                                       "Ascolto del comando non riuscito") from exc
