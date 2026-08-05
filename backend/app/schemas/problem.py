"""Canonical RFC 9457-style API problem contract."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProblemDetail(BaseModel):
    """Stable safe error payload shared by every API module."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    type: str
    title: str
    status: int = Field(ge=400, le=599)
    code: str = Field(pattern=r"^[A-Z][A-Z0-9_]{2,63}$")
    detail: str
    instance: str
    correlation_id: str = Field(alias="correlationId")
    field_errors: dict[str, list[str]] | None = Field(default=None, alias="fieldErrors")
    retry_after_seconds: int | None = Field(
        default=None,
        alias="retryAfterSeconds",
        ge=1,
    )
