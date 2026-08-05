"""Global conversion from framework failures to the canonical safe problem shape."""

from __future__ import annotations

import logging
from collections.abc import Mapping

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.problems import create_problem_response
from app.core.errors import ApplicationError
from app.middleware.request_context import get_correlation_id

_logger = logging.getLogger(__name__)


def _field_errors(error: RequestValidationError) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {}
    for item in error.errors():
        location = ".".join(
            str(part) for part in item["loc"] if part not in {"body", "query", "path"}
        )
        key = location or "request"
        errors.setdefault(key, []).append(str(item["msg"]))
    return errors


def _http_error_details(status_code: int) -> tuple[str, str, str]:
    details: Mapping[int, tuple[str, str, str]] = {
        404: ("RESOURCE_NOT_FOUND", "Resource not found", "The requested resource was not found."),
        405: (
            "METHOD_NOT_ALLOWED",
            "Method not allowed",
            "The requested method is not allowed for this resource.",
        ),
    }
    return details.get(
        status_code,
        ("HTTP_REQUEST_FAILED", "Request failed", "The request could not be completed."),
    )


def install_exception_handlers(app: FastAPI) -> None:
    """Register the only transport-level exception mapping entry points."""

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        return create_problem_response(
            request,
            status_code=400,
            code="VALIDATION_FAILED",
            title="Request validation failed",
            detail="One or more request fields are invalid.",
            field_errors=_field_errors(error),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, error: StarletteHTTPException
    ) -> JSONResponse:
        code, title, detail = _http_error_details(error.status_code)
        return create_problem_response(
            request,
            status_code=error.status_code,
            code=code,
            title=title,
            detail=detail,
        )

    @app.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, error: ApplicationError) -> JSONResponse:
        return create_problem_response(
            request,
            status_code=error.status_code,
            code=error.code,
            title=error.title,
            detail=error.detail,
            retry_after_seconds=error.retry_after_seconds,
            headers=error.headers or None,
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(request: Request, error: Exception) -> JSONResponse:
        _logger.exception(
            "unhandled_api_error",
            extra={
                "context": {
                    "correlationId": get_correlation_id(),
                    "path": request.url.path,
                    "exceptionType": type(error).__name__,
                }
            },
        )
        return create_problem_response(
            request,
            status_code=500,
            code="INTERNAL_ERROR",
            title="Unexpected service error",
            detail="The service could not complete the request.",
        )
