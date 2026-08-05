"""Validated authentication, current-user, session, and RBAC API contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr

from app.models.auth import UserRole


class ApiModel(BaseModel):
    """Strict camelCase-compatible transport model."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class LoginRequest(ApiModel):
    """Human sign-in credential request."""

    email: EmailStr = Field(max_length=254)
    password: SecretStr = Field(min_length=8, max_length=128)
    remember_device: bool = Field(default=False, alias="rememberDevice")


class CurrentUserResponse(ApiModel):
    """Live backend-authoritative identity and authorization projection."""

    id: str = Field(pattern=r"^usr_[A-Za-z0-9]+$")
    display_name: str = Field(alias="displayName", min_length=1, max_length=100)
    email: EmailStr
    role: UserRole
    factory_ids: list[str] = Field(alias="factoryIds")
    permissions: list[str]


class LoginResponse(ApiModel):
    """Short access token plus user projection; refresh stays in an HTTP-only cookie."""

    access_token: str = Field(alias="accessToken")
    expires_in: int = Field(alias="expiresIn", ge=1)
    user: CurrentUserResponse


class RefreshResponse(ApiModel):
    """Rotated short access-token response."""

    access_token: str = Field(alias="accessToken")
    expires_in: int = Field(alias="expiresIn", ge=1)


class LogoutResponse(ApiModel):
    """Current-session revocation result."""

    revoked: bool


class LogoutAllRequest(ApiModel):
    """Explicit reason for revoking every owned session."""

    reason: Literal["user_request", "security_concern"] = "user_request"


class LogoutAllResponse(ApiModel):
    """All-session revocation count."""

    revoked_sessions: int = Field(alias="revokedSessions", ge=0)


class PasswordResetRequest(ApiModel):
    """Non-enumerating password-reset request."""

    email: EmailStr = Field(max_length=254)


class PasswordResetAccepted(ApiModel):
    """Uniform response regardless of whether the identity exists."""

    accepted: Literal[True] = True


class PasswordResetConfirm(ApiModel):
    """Single-use reset token and replacement password."""

    token: SecretStr = Field(min_length=32, max_length=256)
    new_password: SecretStr = Field(alias="newPassword", min_length=12, max_length=128)


class PasswordResetCompleted(ApiModel):
    """Password reset completion response."""

    reset: Literal[True] = True


class SessionResponse(ApiModel):
    """Safe current-user session metadata."""

    id: str = Field(pattern=r"^ses_[a-f0-9]{32}$")
    current: bool
    created_at: datetime = Field(alias="createdAt")
    last_seen_at: datetime = Field(alias="lastSeenAt")
    expires_at: datetime = Field(alias="expiresAt")
    revoked_at: datetime | None = Field(default=None, alias="revokedAt")
    user_agent: str | None = Field(default=None, alias="userAgent", max_length=256)


class PageMetadata(ApiModel):
    """Opaque-cursor pagination metadata."""

    next_cursor: str | None = Field(default=None, alias="nextCursor")
    limit: int = Field(ge=1, le=100)


class SessionListResponse(ApiModel):
    """Current user's active and recent sessions."""

    items: list[SessionResponse]
    page: PageMetadata


class RoleDefinitionResponse(ApiModel):
    """Safe role definition exposed to authenticated clients."""

    id: UserRole
    label: str
    permissions: list[str]


class RoleListResponse(ApiModel):
    """All approved role definitions."""

    items: list[RoleDefinitionResponse]
