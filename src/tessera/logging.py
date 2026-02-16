"""Logging configuration for Tessera.

Supports two output formats controlled by the LOG_FORMAT setting:
- 'text': Human-readable format for development (default)
- 'json': Structured JSON for production log aggregators (CloudWatch, Datadog, etc.)

Usage:
    Called once at application startup in main.py lifespan.

    from tessera.logging import configure_logging
    configure_logging()
"""

import json
import logging
import sys
from datetime import UTC, datetime


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects.

    Output fields:
        timestamp: ISO 8601 UTC timestamp
        level: Log level name (INFO, WARNING, ERROR, etc.)
        logger: Logger name (dotted module path)
        message: Formatted log message
        exc_info: Exception traceback (only if present)
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, str | int | float] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info and record.exc_info[1] is not None:
            log_entry["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


def configure_logging(level: str = "INFO", fmt: str = "text") -> None:
    """Configure root logger with the specified format and level.

    Args:
        level: Log level name (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        fmt: Output format — 'text' for human-readable, 'json' for structured.
    """
    root = logging.getLogger()

    # Clear existing handlers to prevent duplicate output
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stderr)

    if fmt == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)-8s %(name)s  %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root.addHandler(handler)
    root.setLevel(level.upper())

    # Quiet noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
