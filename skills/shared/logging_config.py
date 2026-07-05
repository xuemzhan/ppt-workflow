"""Configured logging for the PPT workflow pipeline.

Provides consistent logging setup across all skills, with support for
verbose/quiet modes and structured output.
"""

from __future__ import annotations

import logging
import sys
from typing import TextIO

# Default format for log messages
_DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_VERBOSE_FORMAT = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
_DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Module-level logger cache
_configured: bool = False


def setup_logging(
    level: int = logging.INFO,
    verbose: bool = False,
    quiet: bool = False,
    stream: TextIO | None = None,
) -> None:
    """Configure logging for the pipeline.

    Args:
        level: Base logging level.
        verbose: Enable verbose (DEBUG) output.
        quiet: Suppress INFO messages (WARNING+ only).
        stream: Output stream (defaults to stderr).
    """
    global _configured  # noqa: PLW0603

    if verbose:
        level = logging.DEBUG
    elif quiet:
        level = logging.WARNING

    handler = logging.StreamHandler(stream if stream is not None else sys.stdout)
    formatter = logging.Formatter(
        _VERBOSE_FORMAT if verbose else _DEFAULT_FORMAT,
        datefmt=_DEFAULT_DATE_FORMAT,
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    # Clear existing handlers to avoid duplicates
    root.handlers.clear()
    root.addHandler(handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module.

    Args:
        name: Logger name (typically __name__).

    Returns:
        Configured logger instance.
    """
    if not _configured:
        setup_logging()
    return logging.getLogger(name)
