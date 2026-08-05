"""Authentication, rotating sessions, password reset, and principal resolution use cases."""

from __future__ import annotations

import asyncio
import unicodedata
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Protocol
from uuid import uuid4

from app.config.settings import Settings
from app.core.errors import ApplicationError, authentication_error
from app.models.auth import (
    AuthenticatedPrincipal,
    AuthenticationResult,
    ClientContext,
    PasswordResetRecord,
    RefreshCredentialRecord,
    SessionRecord,
    TokenPair,
    UserAccount,
    UserStatus,
)
from app.repositories.auth import AuthRepository, RefreshRotationStatus
from app.security.passwords import PasswordManager
from app.security.tokens import AccessTokenCodec, OpaqueTokenManager, utc_now


class AuthenticationEventSink(Protocol):
    """Port for durable-safe authentication and security evidence."""

    async def emit(
        self,
        event_type: str,
        outcome: str,
        *,
        user_id: str | None = None,
        session_id: str | None = None,
        reason: str | None = None,
    ) -> None: ...


class PasswordResetNotifier(Protocol):
    """Port for delivering a one-time reset token outside the API response."""

    async def deliver(
        self,
        *,
        user_id: str,
        email: str,
        token: str,
        expires_at: datetime,
    ) -> None: ...


Clock = Callable[[], datetime]


def normalize_email(value: str) -> str:
    """Apply the canonical identity lookup normalization."""

    return unicodedata.normalize("NFKC", value).strip().casefold()


class AuthenticationService:
    """Security use cases with no FastAPI, boto3, or persistence implementation coupling."""

    def __init__(
        self,
        settings: Settings,
        repository: AuthRepository,
        passwords: PasswordManager,
        access_tokens: AccessTokenCodec,
        opaque_tokens: OpaqueTokenManager,
        events: AuthenticationEventSink,
        reset_notifier: PasswordResetNotifier,
        clock: Clock = utc_now,
    ) -> None:
        self._settings = settings
        self._repository = repository
        self._passwords = passwords
        self._access_tokens = access_tokens
        self._opaque_tokens = opaque_tokens
        self._events = events
        self._reset_notifier = reset_notifier
        self._clock = clock

    async def login(
        self,
        email: str,
        password: str,
        remember_device: bool,
        client: ClientContext,
    ) -> AuthenticationResult:
        """Verify credentials, apply throttling/lockout, and create a token family."""

        now = self._clock()
        normalized_email = normalize_email(email)
        identity_key = f"identity:{self._opaque_tokens.fingerprint(normalized_email)}"
        client_key = f"login:{self._opaque_tokens.fingerprint(client.ip_address)}"
        await self._enforce_rate_limit(
            client_key,
            now,
            limit=self._settings.login_rate_limit,
            window_seconds=self._settings.login_rate_window_seconds,
        )

        locked_for = await self._repository.get_login_lockout(identity_key, now)
        if locked_for is not None:
            await self._events.emit("login_locked", "denied", reason="temporary_lockout")
            raise self._account_locked(locked_for)

        user = await self._repository.get_user_by_email(normalized_email)
        verified = False
        replacement_hash: str | None = None
        if user is None:
            await asyncio.to_thread(self._passwords.verify_unknown_user, password)
        else:
            verified, replacement_hash = await asyncio.to_thread(
                self._passwords.verify_password, password, user.password_hash
            )

        if user is None or not verified or user.status is not UserStatus.ACTIVE:
            lockout = await self._repository.record_login_failure(
                identity_key,
                now,
                failure_limit=self._settings.login_failure_limit,
                failure_window_seconds=self._settings.login_failure_window_seconds,
                lockout_seconds=self._settings.login_lockout_seconds,
            )
            await self._events.emit(
                "login_failed",
                "denied",
                user_id=user.id if user is not None else None,
                reason="invalid_credentials",
            )
            if lockout is not None:
                raise self._account_locked(lockout)
            raise authentication_error(
                code="INVALID_CREDENTIALS",
                detail="The email or password is incorrect.",
            )

        await self._repository.clear_login_failures(identity_key)
        if replacement_hash is not None:
            await self._repository.update_password_hash(
                user.id, user.password_hash, replacement_hash
            )
            user.password_hash = replacement_hash

        refresh_ttl = (
            self._settings.refresh_token_ttl_seconds
            if remember_device
            else self._settings.refresh_token_short_ttl_seconds
        )
        session = self._new_session(user, client, now, refresh_ttl)
        refresh_token = self._opaque_tokens.generate("rt")
        refresh_record = RefreshCredentialRecord(
            digest=self._opaque_tokens.digest(refresh_token),
            session_id=session.id,
            family_id=session.family_id,
            issued_at=now,
            expires_at=session.expires_at,
        )
        await self._repository.create_session(session, refresh_record)
        principal = self._principal(user, session)
        tokens = TokenPair(
            access_token=self._access_tokens.issue(user, session.id, now),
            refresh_token=refresh_token,
            access_expires_in=self._access_tokens.expires_in,
            refresh_expires_at=session.expires_at,
        )
        await self._events.emit(
            "login_succeeded", "succeeded", user_id=user.id, session_id=session.id
        )
        return AuthenticationResult(principal=principal, tokens=tokens)

    async def refresh(self, refresh_token: str | None) -> TokenPair:
        """Rotate one refresh credential and issue a new access token."""

        if not refresh_token:
            raise authentication_error(
                code="REFRESH_INVALID",
                detail="The refresh credential is invalid or expired.",
            )
        now = self._clock()
        replacement_token = self._opaque_tokens.generate("rt")
        replacement = RefreshCredentialRecord(
            digest=self._opaque_tokens.digest(replacement_token),
            session_id="pending",
            family_id="pending",
            issued_at=now,
            expires_at=now + timedelta(seconds=self._settings.refresh_token_ttl_seconds),
        )

        current_digest = self._opaque_tokens.digest(refresh_token)
        session_hint = await self._repository.get_session_for_refresh(current_digest)
        if session_hint is not None:
            replacement.session_id = session_hint.id
            replacement.family_id = session_hint.family_id
            replacement.expires_at = session_hint.expires_at
        status, session = await self._repository.rotate_refresh(current_digest, replacement, now)
        if status is RefreshRotationStatus.REUSED:
            await self._events.emit(
                "refresh_reuse_detected",
                "denied",
                user_id=session.user_id if session else None,
                session_id=session.id if session else None,
                reason="refresh_reuse",
            )
            raise authentication_error(
                code="REFRESH_REUSE_DETECTED",
                detail="Refresh credential reuse was detected; the session has been revoked.",
            )
        if status is not RefreshRotationStatus.ROTATED or session is None:
            await self._events.emit("refresh_failed", "denied", reason=status.value)
            raise authentication_error(
                code="REFRESH_INVALID",
                detail="The refresh credential is invalid or expired.",
            )

        user = await self._repository.get_user_by_id(session.user_id)
        if user is None or user.status is not UserStatus.ACTIVE or not session.is_active(now):
            await self._repository.revoke_session(session.id, now, "identity_unavailable")
            raise authentication_error(code="SESSION_REVOKED")
        await self._events.emit(
            "refresh_succeeded", "succeeded", user_id=user.id, session_id=session.id
        )
        return TokenPair(
            access_token=self._access_tokens.issue(user, session.id, now),
            refresh_token=replacement_token,
            access_expires_in=self._access_tokens.expires_in,
            refresh_expires_at=session.expires_at,
        )

    async def authenticate_access_token(self, token: str) -> AuthenticatedPrincipal:
        """Resolve a bearer JWT into live server-authoritative identity and scope."""

        claims = self._access_tokens.decode(token)
        now = self._clock()
        user = await self._repository.get_user_by_id(claims.subject)
        session = await self._repository.get_session(claims.session_id)
        if (
            user is None
            or session is None
            or session.user_id != claims.subject
            or not session.is_active(now)
            or user.status is not UserStatus.ACTIVE
            or user.token_version != claims.token_version
            or user.scope_version != claims.scope_version
            or user.role.value != claims.role
        ):
            raise authentication_error(code="SESSION_REVOKED")
        return self._principal(user, session)

    async def logout(self, principal: AuthenticatedPrincipal) -> bool:
        """Idempotently revoke the current token family."""

        now = self._clock()
        revoked = await self._repository.revoke_session(principal.session_id, now, "user_logout")
        await self._events.emit(
            "session_revoked",
            "succeeded",
            user_id=principal.user_id,
            session_id=principal.session_id,
            reason="user_logout",
        )
        return revoked

    async def logout_all(self, principal: AuthenticatedPrincipal, reason: str) -> int:
        """Revoke every active session for the current user."""

        count = await self._repository.revoke_user_sessions(
            principal.user_id, self._clock(), reason
        )
        await self._events.emit(
            "all_sessions_revoked",
            "succeeded",
            user_id=principal.user_id,
            session_id=principal.session_id,
            reason=reason,
        )
        return count

    async def list_sessions(self, principal: AuthenticatedPrincipal) -> list[SessionRecord]:
        """List the current user's active and recent sessions."""

        return await self._repository.list_user_sessions(principal.user_id)

    async def revoke_owned_session(
        self, principal: AuthenticatedPrincipal, session_id: str
    ) -> bool:
        """Revoke one owned session while concealing other users' session IDs."""

        session = await self._repository.get_session(session_id)
        if session is None or session.user_id != principal.user_id:
            raise ApplicationError(
                status_code=404,
                code="RESOURCE_NOT_FOUND",
                title="Resource not found",
                detail="The requested resource was not found.",
            )
        return await self._repository.revoke_session(session_id, self._clock(), "user_request")

    async def request_password_reset(self, email: str, client: ClientContext) -> None:
        """Start a non-enumerating reset flow with a single-use opaque token."""

        now = self._clock()
        client_key = f"reset:{self._opaque_tokens.fingerprint(client.ip_address)}"
        await self._enforce_rate_limit(
            client_key,
            now,
            limit=self._settings.password_reset_rate_limit,
            window_seconds=self._settings.password_reset_rate_window_seconds,
        )
        user = await self._repository.get_user_by_email(normalize_email(email))
        token = self._opaque_tokens.generate("pr")
        if user is not None and user.status is UserStatus.ACTIVE:
            expires_at = now + timedelta(seconds=self._settings.password_reset_token_ttl_seconds)
            await self._repository.store_password_reset(
                PasswordResetRecord(
                    digest=self._opaque_tokens.digest(token),
                    user_id=user.id,
                    issued_at=now,
                    expires_at=expires_at,
                )
            )
            await self._reset_notifier.deliver(
                user_id=user.id,
                email=user.email,
                token=token,
                expires_at=expires_at,
            )
            await self._events.emit("password_reset_requested", "accepted", user_id=user.id)
        else:
            await self._events.emit("password_reset_requested", "accepted")

    async def confirm_password_reset(self, token: str, new_password: str) -> None:
        """Consume a reset token, update the adaptive hash, and revoke all sessions."""

        self._passwords.validate_new_password(new_password)
        now = self._clock()
        user_id = await self._repository.consume_password_reset(
            self._opaque_tokens.digest(token), now
        )
        if user_id is None:
            raise ApplicationError(
                status_code=400,
                code="RESET_TOKEN_INVALID",
                title="Password reset failed",
                detail="The password reset token is invalid or expired.",
            )
        replacement_hash = await asyncio.to_thread(self._passwords.hash_password, new_password)
        updated = await self._repository.replace_password_and_revoke_sessions(
            user_id, replacement_hash, now
        )
        if not updated:
            raise ApplicationError(
                status_code=400,
                code="RESET_TOKEN_INVALID",
                title="Password reset failed",
                detail="The password reset token is invalid or expired.",
            )
        await self._events.emit(
            "password_reset_completed", "succeeded", user_id=user_id, reason="password_reset"
        )

    async def get_user(self, principal: AuthenticatedPrincipal) -> UserAccount:
        """Load the live current-user identity projection."""

        user = await self._repository.get_user_by_id(principal.user_id)
        if user is None or user.status is not UserStatus.ACTIVE:
            raise authentication_error(code="SESSION_REVOKED")
        return user

    async def _enforce_rate_limit(
        self,
        bucket: str,
        now: datetime,
        *,
        limit: int,
        window_seconds: int,
    ) -> None:
        retry_after = await self._repository.check_rate_limit(
            bucket,
            now,
            limit=limit,
            window_seconds=window_seconds,
        )
        if retry_after is not None:
            await self._events.emit("authentication_rate_limited", "denied", reason="rate_limit")
            raise ApplicationError(
                status_code=429,
                code="RATE_LIMITED",
                title="Too many requests",
                detail="Too many authentication requests were received. Try again later.",
                headers={"Retry-After": str(retry_after)},
                retry_after_seconds=retry_after,
            )

    def _new_session(
        self,
        user: UserAccount,
        client: ClientContext,
        now: datetime,
        refresh_ttl_seconds: int,
    ) -> SessionRecord:
        return SessionRecord(
            id=f"ses_{uuid4().hex}",
            family_id=f"fam_{uuid4().hex}",
            user_id=user.id,
            created_at=now,
            last_seen_at=now,
            expires_at=now + timedelta(seconds=refresh_ttl_seconds),
            user_agent=client.user_agent[:256] if client.user_agent else None,
            client_ip_hash=self._opaque_tokens.fingerprint(client.ip_address),
        )

    @staticmethod
    def _principal(user: UserAccount, session: SessionRecord) -> AuthenticatedPrincipal:
        return AuthenticatedPrincipal(
            user_id=user.id,
            session_id=session.id,
            email=user.email,
            display_name=user.display_name,
            role=user.role,
            factory_ids=user.factory_ids,
        )

    @staticmethod
    def _account_locked(retry_after: int) -> ApplicationError:
        return ApplicationError(
            status_code=423,
            code="ACCOUNT_LOCKED",
            title="Sign-in temporarily unavailable",
            detail="Sign-in is temporarily locked after repeated unsuccessful attempts.",
            headers={"Retry-After": str(retry_after)},
            retry_after_seconds=retry_after,
        )
