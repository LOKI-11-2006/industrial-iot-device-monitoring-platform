"""Authentication persistence port and Phase 2 in-memory adapter."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable
from dataclasses import replace
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Protocol

from app.models.auth import (
    LoginAttemptState,
    PasswordResetRecord,
    RefreshCredentialRecord,
    SessionRecord,
    UserAccount,
)


class RefreshRotationStatus(StrEnum):
    """Atomic refresh-credential consumption outcomes."""

    ROTATED = "ROTATED"
    INVALID = "INVALID"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    REUSED = "REUSED"


class AuthRepository(Protocol):
    """Persistence operations required by authentication independent of DynamoDB."""

    async def get_user_by_email(self, normalized_email: str) -> UserAccount | None: ...

    async def get_user_by_id(self, user_id: str) -> UserAccount | None: ...

    async def update_password_hash(
        self, user_id: str, current_hash: str, replacement_hash: str
    ) -> None: ...

    async def replace_password_and_revoke_sessions(
        self, user_id: str, replacement_hash: str, now: datetime
    ) -> bool: ...

    async def create_session(
        self, session: SessionRecord, refresh: RefreshCredentialRecord
    ) -> None: ...

    async def get_session(self, session_id: str) -> SessionRecord | None: ...

    async def get_session_for_refresh(self, digest: str) -> SessionRecord | None: ...

    async def rotate_refresh(
        self,
        current_digest: str,
        replacement: RefreshCredentialRecord,
        now: datetime,
    ) -> tuple[RefreshRotationStatus, SessionRecord | None]: ...

    async def revoke_session(self, session_id: str, now: datetime, reason: str) -> bool: ...

    async def revoke_user_sessions(self, user_id: str, now: datetime, reason: str) -> int: ...

    async def list_user_sessions(self, user_id: str) -> list[SessionRecord]: ...

    async def check_rate_limit(
        self,
        bucket: str,
        now: datetime,
        *,
        limit: int,
        window_seconds: int,
    ) -> int | None: ...

    async def get_login_lockout(self, identity_key: str, now: datetime) -> int | None: ...

    async def record_login_failure(
        self,
        identity_key: str,
        now: datetime,
        *,
        failure_limit: int,
        failure_window_seconds: int,
        lockout_seconds: int,
    ) -> int | None: ...

    async def clear_login_failures(self, identity_key: str) -> None: ...

    async def store_password_reset(self, record: PasswordResetRecord) -> None: ...

    async def consume_password_reset(self, digest: str, now: datetime) -> str | None: ...


class InMemoryAuthRepository:
    """Concurrency-safe adapter for local development and tests until Phase 3 DynamoDB."""

    def __init__(self, users: Iterable[UserAccount] = ()) -> None:
        seeded_users = [replace(user) for user in users]
        if len({user.id for user in seeded_users}) != len(seeded_users) or len(
            {user.email for user in seeded_users}
        ) != len(seeded_users):
            raise ValueError("Seeded user IDs and normalized emails must be unique.")
        self._users_by_id: dict[str, UserAccount] = {user.id: user for user in seeded_users}
        self._user_ids_by_email: dict[str, str] = {user.email: user.id for user in seeded_users}
        self._sessions: dict[str, SessionRecord] = {}
        self._refresh_credentials: dict[str, RefreshCredentialRecord] = {}
        self._login_attempts: dict[str, LoginAttemptState] = {}
        self._rate_buckets: dict[str, list[datetime]] = {}
        self._password_resets: dict[str, PasswordResetRecord] = {}
        self._lock = asyncio.Lock()

    async def add_user(self, user: UserAccount) -> None:
        """Seed one identity without embedding any credential in application code."""

        async with self._lock:
            if user.id in self._users_by_id or user.email in self._user_ids_by_email:
                raise ValueError("User ID and normalized email must be unique.")
            self._users_by_id[user.id] = replace(user)
            self._user_ids_by_email[user.email] = user.id

    async def get_user_by_email(self, normalized_email: str) -> UserAccount | None:
        async with self._lock:
            user_id = self._user_ids_by_email.get(normalized_email)
            user = self._users_by_id.get(user_id) if user_id is not None else None
            return replace(user) if user is not None else None

    async def get_user_by_id(self, user_id: str) -> UserAccount | None:
        async with self._lock:
            user = self._users_by_id.get(user_id)
            return replace(user) if user is not None else None

    async def update_password_hash(
        self, user_id: str, current_hash: str, replacement_hash: str
    ) -> None:
        async with self._lock:
            user = self._users_by_id.get(user_id)
            if user is not None and user.password_hash == current_hash:
                user.password_hash = replacement_hash

    async def replace_password_and_revoke_sessions(
        self, user_id: str, replacement_hash: str, now: datetime
    ) -> bool:
        async with self._lock:
            user = self._users_by_id.get(user_id)
            if user is None:
                return False
            user.password_hash = replacement_hash
            user.token_version += 1
            self._revoke_user_sessions_locked(user_id, now, "password_reset")
            for reset in self._password_resets.values():
                if reset.user_id == user_id and reset.used_at is None:
                    reset.used_at = now
            return True

    async def create_session(
        self, session: SessionRecord, refresh: RefreshCredentialRecord
    ) -> None:
        async with self._lock:
            if session.id in self._sessions or refresh.digest in self._refresh_credentials:
                raise ValueError("Session and refresh identifiers must be unique.")
            if session.id != refresh.session_id or session.family_id != refresh.family_id:
                raise ValueError("Refresh credential must belong to the supplied session family.")
            self._sessions[session.id] = replace(session)
            self._refresh_credentials[refresh.digest] = replace(refresh)

    async def get_session(self, session_id: str) -> SessionRecord | None:
        async with self._lock:
            session = self._sessions.get(session_id)
            return replace(session) if session is not None else None

    async def get_session_for_refresh(self, digest: str) -> SessionRecord | None:
        async with self._lock:
            credential = self._refresh_credentials.get(digest)
            session = self._sessions.get(credential.session_id) if credential is not None else None
            return replace(session) if session is not None else None

    async def rotate_refresh(
        self,
        current_digest: str,
        replacement: RefreshCredentialRecord,
        now: datetime,
    ) -> tuple[RefreshRotationStatus, SessionRecord | None]:
        async with self._lock:
            current = self._refresh_credentials.get(current_digest)
            if current is None:
                return RefreshRotationStatus.INVALID, None
            session = self._sessions.get(current.session_id)
            if session is None:
                return RefreshRotationStatus.INVALID, None
            if current.used_at is not None:
                self._revoke_family_locked(current.family_id, now, "refresh_reuse")
                return RefreshRotationStatus.REUSED, replace(session)
            if current.revoked_at is not None or session.revoked_at is not None:
                return RefreshRotationStatus.REVOKED, replace(session)
            if now >= current.expires_at or now >= session.expires_at:
                self._revoke_family_locked(current.family_id, now, "session_expired")
                return RefreshRotationStatus.EXPIRED, replace(session)
            if (
                replacement.session_id != current.session_id
                or replacement.family_id != current.family_id
                or replacement.digest in self._refresh_credentials
            ):
                raise ValueError("Replacement refresh credential has invalid lineage.")

            current.used_at = now
            session.last_seen_at = now
            self._refresh_credentials[replacement.digest] = replace(replacement)
            return RefreshRotationStatus.ROTATED, replace(session)

    async def revoke_session(self, session_id: str, now: datetime, reason: str) -> bool:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return False
            self._revoke_family_locked(session.family_id, now, reason)
            return True

    async def revoke_user_sessions(self, user_id: str, now: datetime, reason: str) -> int:
        async with self._lock:
            return self._revoke_user_sessions_locked(user_id, now, reason)

    async def list_user_sessions(self, user_id: str) -> list[SessionRecord]:
        async with self._lock:
            sessions = [
                replace(item) for item in self._sessions.values() if item.user_id == user_id
            ]
            return sorted(sessions, key=lambda item: item.created_at, reverse=True)

    async def check_rate_limit(
        self,
        bucket: str,
        now: datetime,
        *,
        limit: int,
        window_seconds: int,
    ) -> int | None:
        async with self._lock:
            cutoff = now - timedelta(seconds=window_seconds)
            recent = [
                timestamp for timestamp in self._rate_buckets.get(bucket, []) if timestamp > cutoff
            ]
            if len(recent) >= limit:
                retry_at = recent[0] + timedelta(seconds=window_seconds)
                return max(1, int((retry_at - now).total_seconds()) + 1)
            recent.append(now)
            self._rate_buckets[bucket] = recent
            return None

    async def get_login_lockout(self, identity_key: str, now: datetime) -> int | None:
        async with self._lock:
            state = self._login_attempts.get(identity_key)
            if state is None or state.locked_until is None or state.locked_until <= now:
                return None
            return max(1, int((state.locked_until - now).total_seconds()) + 1)

    async def record_login_failure(
        self,
        identity_key: str,
        now: datetime,
        *,
        failure_limit: int,
        failure_window_seconds: int,
        lockout_seconds: int,
    ) -> int | None:
        async with self._lock:
            state = self._login_attempts.setdefault(identity_key, LoginAttemptState())
            cutoff = now - timedelta(seconds=failure_window_seconds)
            state.failures = [timestamp for timestamp in state.failures if timestamp > cutoff]
            state.failures.append(now)
            if len(state.failures) < failure_limit:
                return None
            state.locked_until = now + timedelta(seconds=lockout_seconds)
            state.failures.clear()
            return lockout_seconds

    async def clear_login_failures(self, identity_key: str) -> None:
        async with self._lock:
            self._login_attempts.pop(identity_key, None)

    async def store_password_reset(self, record: PasswordResetRecord) -> None:
        async with self._lock:
            if record.digest in self._password_resets:
                raise ValueError("Password reset digest must be unique.")
            self._password_resets[record.digest] = replace(record)

    async def consume_password_reset(self, digest: str, now: datetime) -> str | None:
        async with self._lock:
            record = self._password_resets.get(digest)
            if record is None or record.used_at is not None or now >= record.expires_at:
                return None
            record.used_at = now
            return record.user_id

    def _revoke_user_sessions_locked(self, user_id: str, now: datetime, reason: str) -> int:
        count = 0
        for session in self._sessions.values():
            if session.user_id == user_id and session.revoked_at is None:
                self._revoke_family_locked(session.family_id, now, reason)
                count += 1
        return count

    def _revoke_family_locked(self, family_id: str, now: datetime, reason: str) -> None:
        for session in self._sessions.values():
            if session.family_id == family_id and session.revoked_at is None:
                session.revoked_at = now
                session.revocation_reason = reason
        for credential in self._refresh_credentials.values():
            if credential.family_id == family_id and credential.revoked_at is None:
                credential.revoked_at = now
