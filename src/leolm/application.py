"""Dependency-injected voice application lifecycle."""

from __future__ import annotations

from .errors import LeoLMError


class VoiceApplication:
    def __init__(self, config, audio, wakeword, speech, session, tts, *, logger=None):
        self.config = config
        self.audio = audio
        self.wakeword = wakeword
        self.speech = speech
        self.session = session
        self.tts = tts
        self.logger = logger
        self.running = True

    def run_once(self) -> str:
        self.wakeword.wait_for_wake()
        device = self.audio.resolve(self.config.input_selector, "input")
        audio = self.speech.listen(device, timeout=5, phrase_limit=5)
        text = self.speech.transcribe(audio, self.config.language)
        reply = self.session.process(text)
        with self.tts.synthesize(reply, self.config.language) as path:
            self.tts.play(path, self.config.output_selector)
        return reply

    def run(self) -> int:
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
