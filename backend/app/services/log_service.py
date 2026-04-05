"""Colored structured logging for the workshop backend.

Provides colored terminal output so the instructor and students can
easily distinguish log levels at a glance during the live demo:

    Green   → INFO    (normal flow)
    Cyan    → DEBUG   (verbose detail)
    Yellow  → WARNING (non-critical issues)
    Red     → ERROR   (failures)
    Magenta → CRITICAL
"""

from __future__ import annotations

import logging
import sys

from app.services.config import LOG_LEVEL


class _Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    DEBUG = "\033[36m"       # Cyan
    INFO = "\033[32m"        # Green
    WARNING = "\033[33m"     # Yellow
    ERROR = "\033[31m"       # Red
    CRITICAL = "\033[35m"    # Magenta

    TIMESTAMP = "\033[90m"   # Dark gray
    NAME = "\033[94m"        # Light blue
    EMOJI = "\033[0m"        # Reset (emojis have their own color)


_LEVEL_COLOR = {
    logging.DEBUG: _Colors.DEBUG,
    logging.INFO: _Colors.INFO,
    logging.WARNING: _Colors.WARNING,
    logging.ERROR: _Colors.ERROR,
    logging.CRITICAL: _Colors.CRITICAL,
}


class ColoredFormatter(logging.Formatter):
    """Log formatter that colors the level name and dims the timestamp/logger name."""

    def format(self, record: logging.LogRecord) -> str:
        color = _LEVEL_COLOR.get(record.levelno, "")
        ts = _Colors.TIMESTAMP
        name = _Colors.NAME
        rst = _Colors.RESET

        fmt = (
            f"{ts}%(asctime)s{rst} "
            f"{name}%(name)s{rst} "
            f"{color}%(levelname)-8s{rst} "
            f"%(message)s"
        )
        formatter = logging.Formatter(fmt, datefmt="%H:%M:%S")
        return formatter.format(record)


def setup_logging() -> None:
    """Replace the root logger's handlers with a single colored console handler."""
    level = getattr(logging, LOG_LEVEL, logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColoredFormatter())

    root = logging.getLogger()
    root.setLevel(level)

    # Remove any existing handlers (e.g. from basicConfig)
    for h in root.handlers[:]:
        root.removeHandler(h)

    root.addHandler(handler)

    # Quieten noisy third-party loggers
    for noisy in ("httpcore", "urllib3", "httpx", "openai", "watchfiles"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Keep uvicorn access logs visible but not overwhelming
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
