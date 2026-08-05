"""Structured logging and redaction tests."""

import json
import logging

from app.logs.formatter import JsonLogFormatter
from app.logs.redaction import redact


def test_redaction_is_recursive_and_preserves_safe_context() -> None:
    result = redact(
        {
            "userId": "usr_123",
            "authorization": "Bearer secret",
            "nested": [{"refresh_token": "secret", "status": "active"}],
        }
    )

    assert result == {
        "userId": "usr_123",
        "authorization": "[REDACTED]",
        "nested": [{"refresh_token": "[REDACTED]", "status": "active"}],
    }


def test_json_formatter_emits_cloudwatch_query_fields() -> None:
    formatter = JsonLogFormatter(service="iot-platform-api", environment="test")
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request_completed",
        args=(),
        exc_info=None,
    )
    record.context = {"correlationId": "corr_12345678", "password": "never-log"}

    payload = json.loads(formatter.format(record))

    assert payload["event"] == "request_completed"
    assert payload["service"] == "iot-platform-api"
    assert payload["environment"] == "test"
    assert payload["correlationId"] == "corr_12345678"
    assert payload["password"] == "[REDACTED]"
