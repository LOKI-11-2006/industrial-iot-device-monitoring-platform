"""Trusted-host enforcement with canonical problem responses."""

from collections.abc import Iterable

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.api.problems import create_problem_response


class TrustedHostProblemMiddleware(BaseHTTPMiddleware):
    """Reject host-header attacks without leaking framework-specific plain text."""

    def __init__(self, app: ASGIApp, *, allowed_hosts: Iterable[str]) -> None:
        super().__init__(app)
        self._allowed_hosts = frozenset(host.lower() for host in allowed_hosts)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        hostname = (request.url.hostname or "").lower()
        if hostname not in self._allowed_hosts:
            return create_problem_response(
                request,
                status_code=400,
                code="INVALID_HOST",
                title="Invalid request host",
                detail="The request host is not permitted.",
            )
        return await call_next(request)
