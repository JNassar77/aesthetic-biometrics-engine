"""
Structured JSON logging for the Aesthetic Biometrics Engine.

Provides a JSON formatter for consistent, machine-parseable logs
across all pipeline steps (preprocess, detect, calibrate, analyze, plan).
"""

from __future__ import annotations

import json
import logging
import time
from contextlib import contextmanager
from typing import Any, Generator


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include extra fields if present
        for key in ("step", "view", "duration_ms", "assessment_id", "zone_count",
                     "error", "warning", "patient_id"):
            val = getattr(record, key, None)
            if val is not None:
                log_entry[key] = val

        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger with JSON formatter for structured output."""
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    root = logging.getLogger()
    root.setLevel(level)

    # Avoid duplicate handlers on repeated calls
    if not any(isinstance(h, logging.StreamHandler) and
               isinstance(h.formatter, JSONFormatter) for h in root.handlers):
        root.addHandler(handler)


@contextmanager
def log_step(
    logger: logging.Logger,
    step: str,
    view: str | None = None,
    **extra: Any,
) -> Generator[dict[str, Any], None, None]:
    """Context manager that logs the start and duration of a pipeline step.

    Usage:
        with log_step(logger, "detect", view="frontal") as ctx:
            result = landmarker.detect(image)
            ctx["landmarks"] = 478

    Yields a dict where you can add extra fields to include in the log.
    """
    context: dict[str, Any] = {}
    start = time.monotonic()

    logger.info(
        "Starting %s",
        step,
        extra={"step": step, "view": view, **extra},
    )

    try:
        yield context
    except Exception as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.error(
            "%s failed after %dms: %s",
            step,
            duration_ms,
            exc,
            extra={"step": step, "view": view, "duration_ms": duration_ms,
                    "error": str(exc), **extra},
        )
        raise
    else:
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.info(
            "%s completed in %dms",
            step,
            duration_ms,
            extra={"step": step, "view": view, "duration_ms": duration_ms,
                    **context, **extra},
        )
