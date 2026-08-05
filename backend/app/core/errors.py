"""Typed application failures that cross into the HTTP presentation boundary."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ApplicationError(Exception):
    """Safe, stable failure raised by application and security services."""

    status_code: int
    code: str
    title: str
    detail: str
    headers: dict[str, str] = field(default_factory=dict)
    retry_after_seconds: int | None = None

    def __post_init__(self) -> None:
        Exception.__init__(self, self.detail)


def authentication_error(
    *,
    code: str = "AUTHENTICATION_REQUIRED",
    detail: str = "A valid authenticated session is required.",
) -> ApplicationError:
    """Create a canonical bearer-authentication failure."""

    return ApplicationError(
        status_code=401,
        code=code,
        title="Authentication required",
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def permission_denied() -> ApplicationError:
    """Create the default-deny authorization response."""

    return ApplicationError(
        status_code=403,
        code="PERMISSION_DENIED",
        title="Permission denied",
        detail="You do not have permission to perform this operation.",
    )


def factory_scope_denied() -> ApplicationError:
    """Create a safe factory-scope denial without revealing resource existence."""

    return ApplicationError(
        status_code=403,
        code="FACTORY_SCOPE_DENIED",
        title="Factory access denied",
        detail="You do not have access to the requested factory scope.",
    )
