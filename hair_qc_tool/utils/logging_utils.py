import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide2 import QtCore

from ..config import config


_is_installed = False
_session_log_file: Optional[Path] = None


class _StreamTee:
    def __init__(self, original, logger: logging.Logger, level: int):
        self._original = original
        self._logger = logger
        self._level = level

    def write(self, message):
        try:
            if message and not message.isspace():
                self._logger.log(self._level, message.rstrip("\n"))
        except Exception:
            pass
        try:
            self._original.write(message)
        except Exception:
            pass

    def flush(self):
        try:
            self._original.flush()
        except Exception:
            pass


def _ensure_log_dir(log_dir: Path) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def _generate_log_file_name(prefix: str = "") -> str:
    # 5-digit session id + timestamp
    session_id = f"{os.getpid() % 100000:05d}"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"{session_id}_Log_{ts}.txt"
    if prefix:
        name = f"{prefix}_{name}"
    return name


def get_default_log_dir() -> Optional[Path]:
    if not config.usd_directory:
        return None
    return config.usd_directory / "logs" / "hair_qc_tool"


def install_file_logging(log_dir: Optional[Path] = None, rotate_keep: int = 10) -> Path:
    global _is_installed, _session_log_file

    if _is_installed and _session_log_file:
        return _session_log_file

    if log_dir is None:
        log_dir = get_default_log_dir()
    if log_dir is None:
        # Fallback to user home if USD dir not set yet
        log_dir = Path.home() / "hair_qc_tool_logs"

    _ensure_log_dir(log_dir)

    # Clean up old logs (rotation by count)
    try:
        existing = sorted(log_dir.glob("*_Log_*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
        for old in existing[rotate_keep:]:
            try:
                old.unlink()
            except Exception:
                pass
    except Exception:
        pass

    # Configure logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    log_file = log_dir / _generate_log_file_name()
    file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                                  datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)

    # Stream handler to Script Editor/console
    stream_handler = logging.StreamHandler(stream=sys.__stdout__)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    _is_installed = True
    _session_log_file = log_file
    logging.getLogger(__name__).info("File logging installed at %s", log_file)
    return log_file


def install_stdout_stderr_tee():
    # Tee stdout and stderr into logging
    stdout_logger = logging.getLogger("STDOUT")
    stderr_logger = logging.getLogger("STDERR")

    if not isinstance(sys.stdout, _StreamTee):
        sys.stdout = _StreamTee(sys.__stdout__, stdout_logger, logging.INFO)
    if not isinstance(sys.stderr, _StreamTee):
        sys.stderr = _StreamTee(sys.__stderr__, stderr_logger, logging.ERROR)


def install_qt_message_handler():
    def handler(mode, context, message):
        try:
            if mode == QtCore.QtInfoMsg:
                level = logging.INFO
            elif mode == QtCore.QtWarningMsg:
                level = logging.WARNING
            elif mode == QtCore.QtCriticalMsg:
                level = logging.ERROR
            elif mode == QtCore.QtFatalMsg:
                level = logging.CRITICAL
            else:
                level = logging.DEBUG

            logging.getLogger("Qt").log(level, message)
        except Exception:
            pass

    try:
        QtCore.qInstallMessageHandler(handler)
    except Exception:
        pass


def install_exception_hook():
    def excepthook(exc_type, exc_value, tb):
        logging.getLogger("Uncaught").exception("Uncaught exception", exc_info=(exc_type, exc_value, tb))
        # Call original excepthook if any
        try:
            if hasattr(sys, "__excepthook__") and sys.__excepthook__:
                sys.__excepthook__(exc_type, exc_value, tb)
        except Exception:
            pass

    sys.excepthook = excepthook


def install_all_logging(log_dir: Optional[Path] = None, rotate_keep: int = 10) -> Path:
    path = install_file_logging(log_dir=log_dir, rotate_keep=rotate_keep)
    install_stdout_stderr_tee()
    install_qt_message_handler()
    install_exception_hook()
    return path
