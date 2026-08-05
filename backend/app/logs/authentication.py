"""CloudWatch-compatible authentication evidence adapters."""

from __future__ import annotations

import logging
from datetime import datetime

from app.middleware.request_context import get_correlation_id

_auth_logger = logging.getLogger("forgesight.authentication")
_security_logger = logging.getLogger("forgesight.security")


class LoggingAuthenticationEventSink:
    """Emit bounded authentication/security events without credentials or identity PII."""

    async def emit(
        self,
        event_type: str,
        outcome: str,
        *,
        user_id: str | None = None,
        session_id: str | None = None,
        reason: str | None = None,
    ) -> None:
        logger = _security_logger if outcome == "denied" else _auth_logger
        logger.info(
            "authentication_event",
            extra={
                "context": {
                    "eventType": event_type,
                    "outcome": outcome,
                    "userId": user_id,
                    "sessionId": session_id,
                    "reason": reason,
                    "correlationId": get_correlation_id(),
                }
            },
        )


class LoggingPasswordResetNotifier:
    """Safe Phase 2 delivery boundary; Phase 6 replaces it with a notification adapter."""

    async def deliver(
        self,
        *,
        user_id: str,
        email: str,
        token: str,
        expires_at: datetime,
    ) -> None:
        del email, token
        _auth_logger.info(
            "password_reset_delivery_pending",
            extra={
                "context": {
                    "userId": user_id,
                    "expiresAt": expires_at.isoformat(),
                    "correlationId": get_correlation_id(),
                }
            },
        )
