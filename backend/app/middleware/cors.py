"""Problem-shaped rejection for disallowed browser preflight requests."""

from collections.abc import Iterable

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.api.problems import create_problem_response


class CorsPreflightGuardMiddleware(BaseHTTPMiddleware):
    """Reject untrusted CORS preflights before Starlette emits a plain-text boundary error."""

    def __init__(self, app: ASGIApp, *, allowed_origins: Iterable[str]) -> None:
        super().__init__(app)
        self._allowed_origins = frozenset(allowed_origins)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        origin = request.headers.get("Origin")
        is_preflight = request.method == "OPTIONS" and request.headers.get(
            "Access-Control-Request-Method"
        )
        if is_preflight and origin not in self._allowed_origins:
            return create_problem_response(
                request,
                status_code=400,
                code="CORS_ORIGIN_DENIED",
                title="Cross-origin request denied",
                detail="The requesting origin is not permitted.",
            )
        return await call_next(request)
