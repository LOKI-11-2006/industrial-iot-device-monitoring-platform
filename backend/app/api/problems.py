"""Canonical problem-response construction for HTTP presentation boundaries."""

from fastapi import Request
from fastapi.responses import JSONResponse

from app.middleware.request_context import get_correlation_id
from app.schemas.problem import ProblemDetail

_PROBLEM_BASE = "https://docs.forgesight.example/problems"


def create_problem_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    title: str,
    detail: str,
    field_errors: dict[str, list[str]] | None = None,
    retry_after_seconds: int | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Build one safe RFC 9457-style response without exposing internal exception details."""

    problem = ProblemDetail(
        type=f"{_PROBLEM_BASE}/{code.lower().replace('_', '-')}",
        title=title,
        status=status_code,
        code=code,
        detail=detail,
        instance=request.url.path,
        correlation_id=get_correlation_id(),
        field_errors=field_errors,
        retry_after_seconds=retry_after_seconds,
    )
    return JSONResponse(
        status_code=status_code,
        content=problem.model_dump(by_alias=True, exclude_none=True),
        media_type="application/problem+json",
        headers=headers,
    )
