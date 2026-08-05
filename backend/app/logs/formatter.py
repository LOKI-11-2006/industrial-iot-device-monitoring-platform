"""JSON log formatter suitable for CloudWatch Logs Insights."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.logs.redaction import redact


class JsonLogFormatter(logging.Formatter):
    """Serialize stable structured log fields without leaking exception internals to clients."""

    def __init__(self, *, service: str, environment: str) -> None:
        super().__init__()
        self._service = service
        self._environment = environment

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "service": self._service,
            "environment": self._environment,
            "logger": record.name,
            "event": record.getMessage(),
        }
        context = getattr(record, "context", None)
        if isinstance(context, dict):
            payload.update(redact(context))
        if record.exc_info and record.exc_info[0] is not None:
            payload["exceptionType"] = record.exc_info[0].__name__
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str)
