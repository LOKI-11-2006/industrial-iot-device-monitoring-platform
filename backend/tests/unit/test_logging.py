"""Structured logging and redaction tests."""

import json
import logging
from datetime import UTC, datetime

import pytest

from app.logs.authentication import LoggingPasswordResetNotifier
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


@pytest.mark.asyncio
async def test_password_reset_delivery_log_never_contains_the_token(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO, logger="forgesight.authentication"):
        await LoggingPasswordResetNotifier().deliver(
            user_id="usr_123",
            email="private@example.com",
            token="pr_super-secret-token",
            expires_at=datetime.now(UTC),
        )

    assert "pr_super-secret-token" not in caplog.text
    assert "private@example.com" not in caplog.text
    assert "password_reset_delivery_pending" in caplog.text
