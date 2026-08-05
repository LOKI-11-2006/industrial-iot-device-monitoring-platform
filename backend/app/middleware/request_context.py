"""Correlation propagation and bounded API request logging."""

from __future__ import annotations

import logging
import re
import time
from contextvars import ContextVar, Token
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

CORRELATION_HEADER = "X-Correlation-ID"
_CORRELATION_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{7,127}$")
_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="unavailable")
_logger = logging.getLogger(__name__)


def get_correlation_id() -> str:
    """Return the request correlation identifier for handlers and adapters."""

    return _correlation_id.get()


def _select_correlation_id(candidate: str | None) -> str:
    if candidate and _CORRELATION_PATTERN.fullmatch(candidate):
        return candidate
    return f"corr_{uuid4().hex}"


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Propagate a safe correlation ID and emit low-cardinality request completion events."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        correlation_id = _select_correlation_id(request.headers.get(CORRELATION_HEADER))
        token: Token[str] = _correlation_id.set(correlation_id)
        started = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers[CORRELATION_HEADER] = correlation_id
            return response
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            _logger.info(
                "api_request_completed",
                extra={
                    "context": {
                        "correlationId": correlation_id,
                        "method": request.method,
                        "path": request.url.path,
                        "statusCode": status_code,
                        "durationMs": duration_ms,
                    }
                },
            )
            _correlation_id.reset(token)
