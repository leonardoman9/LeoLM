"""Safe logging helpers."""

from __future__ import annotations

import logging

from .errors import redact


def configure_logging() -> logging.Logger:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    return logging.getLogger("leolm")


def safe_error(logger: logging.Logger, message: object, secrets: tuple[str, ...] = ()) -> None:
    logger.error(redact(message, secrets))
