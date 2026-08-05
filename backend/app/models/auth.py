"""Framework-independent identity, session, and credential domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class UserRole(StrEnum):
    """Approved human roles; values are stable API and audit identifiers."""

    SUPER_ADMINISTRATOR = "SUPER_ADMINISTRATOR"
    FACTORY_ADMINISTRATOR = "FACTORY_ADMINISTRATOR"
    FACTORY_MANAGER = "FACTORY_MANAGER"
    MAINTENANCE_ENGINEER = "MAINTENANCE_ENGINEER"
    OPERATOR = "OPERATOR"
    VIEWER = "VIEWER"


class UserStatus(StrEnum):
    """Authentication-relevant user lifecycle states."""

    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


@dataclass(slots=True)
class UserAccount:
    """Minimum identity projection needed by authentication and authorization."""

    id: str
    email: str
    display_name: str
    password_hash: str
    role: UserRole
    factory_ids: tuple[str, ...] = ()
    status: UserStatus = UserStatus.ACTIVE
    token_version: int = 1
    scope_version: int = 1


@dataclass(slots=True)
class SessionRecord:
    """Server-side session state used for immediate revocation."""

    id: str
    family_id: str
    user_id: str
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime
    user_agent: str | None = None
    client_ip_hash: str | None = None
    revoked_at: datetime | None = None
    revocation_reason: str | None = None

    def is_active(self, now: datetime) -> bool:
        """Return whether this session remains usable at the supplied time."""

        return self.revoked_at is None and now < self.expires_at


@dataclass(slots=True)
class RefreshCredentialRecord:
    """Hashed opaque refresh credential with rotation lineage."""

    digest: str
    session_id: str
    family_id: str
    issued_at: datetime
    expires_at: datetime
    used_at: datetime | None = None
    revoked_at: datetime | None = None


@dataclass(slots=True)
class PasswordResetRecord:
    """Single-use, expiration-controlled password reset credential."""

    digest: str
    user_id: str
    issued_at: datetime
    expires_at: datetime
    used_at: datetime | None = None


@dataclass(slots=True)
class LoginAttemptState:
    """Bounded failed-login and temporary-lockout state."""

    failures: list[datetime] = field(default_factory=list)
    locked_until: datetime | None = None


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    """Trusted identity projection constructed only by the backend."""

    user_id: str
    session_id: str
    email: str
    display_name: str
    role: UserRole
    factory_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ClientContext:
    """Bounded request metadata retained with a session and security events."""

    ip_address: str
    user_agent: str | None


@dataclass(frozen=True, slots=True)
class TokenPair:
    """New access token and rotating refresh credential returned by a use case."""

    access_token: str
    refresh_token: str
    access_expires_in: int
    refresh_expires_at: datetime


@dataclass(frozen=True, slots=True)
class AuthenticationResult:
    """Successful login result."""

    principal: AuthenticatedPrincipal
    tokens: TokenPair
