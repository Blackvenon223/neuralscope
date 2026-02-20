"""Structured logging for NeuralScope."""

from __future__ import annotations

import logging
import sys

from neuralscope.core.settings import get_settings


def setup_logging() -> logging.Logger:
    """Configure structured logging."""
    settings = get_settings()

    logger = logging.getLogger("neuralscope")
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a child logger."""
    return logging.getLogger(f"neuralscope.{name}")
