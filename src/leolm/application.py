"""Dependency-injected voice application lifecycle."""

from __future__ import annotations

import re

from .errors import LeoLMError


def _strip_markdown(text: str) -> str:
    """Remove common markdown formatting so TTS reads clean text."""
    text = re.sub(r"```[\s\S]*?```", "", text)       # code blocks
    text = re.sub(r"`[^`]+`", "", text)               # inline code
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.M)  # headings
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)  # bold/italic
    text = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", text)
    text = re.sub(r"~~([^~]+)~~", r"\1", text)        # strikethrough
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)  # bullet lists
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.M)  # numbered lists
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # links
    text = re.sub(r"\n{3,}", "\n\n", text)            # excess newlines
    return text.strip()


class VoiceApplication:
    def __init__(self, config, audio, wakeword, speech, session, tts, *, logger=None, sounds=None):
        self.config = config
        self.audio = audio
        self.wakeword = wakeword
        self.speech = speech
        self.session = session
        self.tts = tts
        self.logger = logger
        self.sounds = sounds
        self.running = True

    def _beep(self, name: str) -> None:
        if self.sounds:
            self.sounds.play(name)

    def _log(self, msg: str, *args) -> None:
        if self.logger:
            self.logger.info(msg, *args)

    def run_once(self) -> str:
        self._log("In attesa del wake word '%s'...", getattr(self.config, "wake_word", "?"))
        self.wakeword.wait_for_wake()
        self._log("Wake word rilevato!")
        self._beep("wake")
        device = self.audio.resolve(self.config.input_selector, "input")
        self._log("Ascolto comando (timeout=%ds)...", 5)
        audio = self.speech.listen(device, timeout=5, phrase_limit=5)
        self._log("Audio catturato, trascrivo...")
        self._beep("thinking")
        text = self.speech.transcribe(audio, self.config.language)
        self._log("Trascritto: '%s'", text)
        self._log("Invio a LLM (%s)...", getattr(self.config, "model", "?"))
        raw_reply = self.session.process(text)
        reply = _strip_markdown(raw_reply)
        self._log("Risposta LLM: '%s'", reply[:120])
        self._log("Genero audio TTS...")
        with self.tts.synthesize(reply, self.config.language) as path:
            self._log("Riproduco risposta...")
            self.tts.play(path, self.config.output_selector)
        self._log("Turno completato, torno in ascolto")
        return reply

    def run(self) -> int:
        self._beep("startup")
        try:
            while self.running:
                try:
                    self.run_once()
                except LeoLMError as exc:
                    if self.logger:
                        self.logger.error(exc.safe_message)
                    self._release_turn_resources()
        except KeyboardInterrupt:
            return 130
        finally:
            self.close()
        return 0

    def _release_turn_resources(self):
        # Individual adapters own their streams/files; closing all is idempotent.
        for resource in (self.wakeword, self.audio):
            close = getattr(resource, "close", None)
            if close:
                close()

    def close(self):
        self.running = False
        for resource in (self.wakeword, self.audio):
            close = getattr(resource, "close", None)
            if close:
                close()
