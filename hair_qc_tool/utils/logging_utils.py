"""
Centralized logging utilities for Hair QC Tool.

- Uses Python's logging with a consistent format
- Streams to stdout, which appears in Maya's Script Editor
"""

import logging
import sys
from typing import Optional


_LOG_FORMAT = "[Hair QC] %(levelname)s - %(name)s: %(message)s"
_DEFAULT_LEVEL = logging.INFO


def _ensure_configured() -> None:
    """Ensure root logging is configured once with our preferred format."""
    if not logging.getLogger().handlers:
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        root = logging.getLogger()
        root.addHandler(handler)
        root.setLevel(_DEFAULT_LEVEL)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a configured logger instance."""
    _ensure_configured()
    return logging.getLogger(name if name else "hair_qc_tool")


def set_global_level(level: int) -> None:
    """Optionally adjust global logging level at runtime."""
    logging.getLogger().setLevel(level)


