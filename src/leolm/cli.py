"""Application lifecycle and compatibility-friendly CLI."""

from __future__ import annotations

import sys

from .config import load_config
from .application import VoiceApplication
from .audio import AudioManager
from .errors import LeoLMError
from .llm import OpenRouterConversation
from .logging import configure_logging, safe_error
from .session import VoiceSession
from .speech import WhisperLocalRecognizer
from .tts import GoogleTTS
from .sounds import SoundPlayer
from .wakeword import VoskWakeWord


def run() -> int:
    logger = configure_logging()
    try:
        config = load_config()
        audio = AudioManager()
        sounds = SoundPlayer(device=config.output_selector)
        application = VoiceApplication(
            config,
            audio,
            VoskWakeWord(config, audio),
            WhisperLocalRecognizer(config),
            VoiceSession(OpenRouterConversation(config), context=None),
            GoogleTTS(config),
            logger=logger,
            sounds=sounds,
        )
        logger.info("LeoLM listening with model %s and language %s", config.model, config.language)
        return application.run()
    except LeoLMError as exc:
        safe_error(logger, exc.safe_message)
        return 2
    except KeyboardInterrupt:
        return 130


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
