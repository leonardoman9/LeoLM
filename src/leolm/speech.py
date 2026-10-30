"""Speech-recognition adapter."""

from __future__ import annotations

from .errors import ExternalServiceError


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
                raise ExternalServiceError("SpeechRecognition is not installed", "Riconoscimento vocale non disponibile") from exc
        try:
            import speech_recognition as sr
            text = self.recognizer.recognize_google(audio, language=language or self.config.language)
        except sr.UnknownValueError as exc:
            raise ExternalServiceError("Speech not understood", "Non ho capito, riprova") from exc
        except sr.RequestError as exc:
            raise ExternalServiceError("Google Speech API error", "Servizio di riconoscimento non raggiungibile") from exc
        except ExternalServiceError:
            raise
        except Exception as exc:
            raise ExternalServiceError("Speech recognition request failed", "Riconoscimento vocale non riuscito") from exc
        if not text or not text.strip():
            raise ExternalServiceError("Speech recognition returned empty text", "Non ho capito, riprova")
        return text.strip()

    def listen(self, device, timeout: float = 5, phrase_limit: float = 5):
        if self.recognizer is None:
            try:
                import speech_recognition as sr
                self.recognizer = sr.Recognizer()
            except ImportError as exc:
                raise ExternalServiceError("SpeechRecognition is not installed", "Riconoscimento vocale non disponibile") from exc
        try:
            import speech_recognition as sr
            source = sr.Microphone(device_index=device.index, sample_rate=device.sample_rate, chunk_size=1024)
            with source as microphone:
                return self.recognizer.listen(microphone, timeout=timeout, phrase_time_limit=phrase_limit)
        except Exception as exc:
            raise ExternalServiceError("Unable to capture speech", "Ascolto del comando non riuscito") from exc
