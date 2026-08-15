"""MemeGPT — Structured JSON Logging & Privacy Compliance.
Implements logging specifications defined in Logging.md.
"""
import os
import json
import logging
import hashlib
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any


class StructuredFormatter(logging.Formatter):
    """Formats log records as JSON lines with standardized fields."""
    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Embed extra attributes if present
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_entry.update(record.extra_data)

        # Standard extra dict kwargs passed into logger.info(..., extra={...})
        standard_skip = {
            "name", "msg", "args", "levelname", "levelno", "pathname",
            "filename", "module", "exc_info", "exc_text", "stack_info",
            "lineno", "funcName", "created", "msecs", "relativeCreated",
            "thread", "threadName", "processName", "process", "extra_data"
        }
        for k, v in record.__dict__.items():
            if k not in standard_skip and not k.startswith("_"):
                log_entry[k] = v

        return json.dumps(log_entry)


def hash_pii(value: str, length: int = 12) -> str:
    """Hash PII (queries, IPs, user identifiers) into an irreversible digest."""
    if not value:
        return "anonymous"
    return hashlib.md5(value.strip().lower().encode("utf-8")).hexdigest()[:length]


def setup_logging(log_level: Optional[str] = None, log_dir: str = "logs") -> logging.Logger:
    """Configure structured JSON logging for console and rotating file output."""
    level_name = (log_level or os.getenv("LOG_LEVEL", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    formatter = StructuredFormatter()

    # Clear existing handlers to prevent duplicate lines
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Console Handler (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Rotating File Handler (10MB max, 5 backups)
    try:
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "memegpt.log")
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        # Fallback gracefully if directory/file is not writable
        logging.warning(f"Could not initialize rotating log file: {e}")

    app_logger = logging.getLogger("memegpt")
    app_logger.setLevel(level)
    return app_logger
