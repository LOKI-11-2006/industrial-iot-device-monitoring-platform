"""End-to-end authentication, session rotation, reset, and current-user tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config.settings import DeploymentEnvironment, Settings
from app.core.application import create_app
from app.models.auth import UserAccount, UserRole, UserStatus
from app.repositories.auth import InMemoryAuthRepository
from app.security.passwords import PasswordManager
from app.security.tokens import development_signing_material

_PASSWORD = "Correct horse battery 1!"
_NEW_PASSWORD = "New correct horse battery 2!"


@dataclass(slots=True)
class MutableClock:
    value: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __call__(self) -> datetime:
        return self.value

    def advance(self, **delta: int) -> None:
        self.value += timedelta(**delta)


@dataclass(slots=True)
class CapturingEvents:
    items: list[dict[str, str | None]] = field(default_factory=list)

    async def emit(
        self,
        event_type: str,
        outcome: str,
        *,
        user_id: str | None = None,
        session_id: str | None = None,
        reason: str | None = None,
    ) -> None:
        self.items.append(
            {
                "eventType": event_type,
                "outcome": outcome,
                "userId": user_id,
                "sessionId": session_id,
                "reason": reason,
            }
        )


@dataclass(slots=True)
class CapturingResetNotifier:
    tokens: list[str] = field(default_factory=list)

    async def deliver(
        self,
        *,
        user_id: str,
        email: str,
        token: str,
        expires_at: datetime,
    ) -> None:
        del user_id, email, expires_at
        self.tokens.append(token)


@dataclass(slots=True)
class AuthHarness:
    application: FastAPI
    client: TestClient
    repository: InMemoryAuthRepository
    clock: MutableClock
    events: CapturingEvents
    reset_notifier: CapturingResetNotifier


@pytest.fixture
def auth_harness() -> AuthHarness:
    password_manager = PasswordManager()
    repository = InMemoryAuthRepository(
        [
            UserAccount(
                id="usr_viewer1",
                email="viewer@example.com",
                display_name="Viewer One",
                password_hash=password_manager.hash_password(_PASSWORD),
                role=UserRole.VIEWER,
                factory_ids=("fac_alpha",),
            ),
            UserAccount(
                id="usr_super1",
                email="admin@example.com",
                display_name="Admin One",
                password_hash=password_manager.hash_password(_PASSWORD),
                role=UserRole.SUPER_ADMINISTRATOR,
                factory_ids=(),
            ),
            UserAccount(
                id="usr_disabled1",
                email="disabled@example.com",
                display_name="Disabled One",
                password_hash=password_manager.hash_password(_PASSWORD),
                role=UserRole.OPERATOR,
                factory_ids=("fac_alpha",),
                status=UserStatus.DISABLED,
            ),
        ]
    )
    settings = Settings(
        _env_file=None,
        environment=DeploymentEnvironment.TEST,
        cors_allowed_origins=["https://console.example.com"],
        allowed_hosts=["testserver"],
        aws_resource_prefix="forgesight-test",
        login_rate_limit=100,
        login_failure_limit=3,
        password_reset_rate_limit=5,
    )
    clock = MutableClock()
    events = CapturingEvents()
    reset_notifier = CapturingResetNotifier()
    application = create_app(
        settings,
        auth_repository=repository,
        signing_material=development_signing_material(),
        authentication_events=events,
        password_reset_notifier=reset_notifier,
        clock=clock,
    )
    with TestClient(application) as client:
        yield AuthHarness(
            application=application,
            client=client,
            repository=repository,
            clock=clock,
            events=events,
            reset_notifier=reset_notifier,
        )


def _login(
    client: TestClient,
    *,
    email: str = "viewer@example.com",
    password: str = _PASSWORD,
    remember_device: bool = False,
) -> Any:
    return client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
            "rememberDevice": remember_device,
        },
    )


def _authorization(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def test_login_cookie_current_user_roles_and_sessions(auth_harness: AuthHarness) -> None:
    response = _login(auth_harness.client)

    assert response.status_code == 200
    body = response.json()
    assert body["expiresIn"] == 900
    assert body["user"] == {
        "id": "usr_viewer1",
        "displayName": "Viewer One",
        "email": "viewer@example.com",
        "role": "VIEWER",
        "factoryIds": ["fac_alpha"],
        "permissions": sorted(body["user"]["permissions"]),
    }
    assert "devices:read" in body["user"]["permissions"]
    assert "users:create" not in body["user"]["permissions"]
    assert "refreshToken" not in body
    assert "HttpOnly" in response.headers["set-cookie"]
    assert "SameSite=strict" in response.headers["set-cookie"]
    assert "Path=/api/v1/auth" in response.headers["set-cookie"]

    headers = _authorization(body["accessToken"])
    current_user = auth_harness.client.get("/api/v1/me", headers=headers)
    roles = auth_harness.client.get("/api/v1/roles", headers=headers)
    sessions = auth_harness.client.get("/api/v1/me/sessions", headers=headers)

    assert current_user.status_code == 200
    assert current_user.json()["role"] == "VIEWER"
    assert roles.status_code == 200
    assert {item["id"] for item in roles.json()["items"]} == set(UserRole)
    assert sessions.status_code == 200
    assert sessions.json()["items"][0]["current"] is True
    assert sessions.json()["page"] == {"nextCursor": None, "limit": 25}


@pytest.mark.parametrize("email", ["unknown@example.com", "disabled@example.com"])
def test_login_does_not_enumerate_unknown_or_disabled_accounts(
    auth_harness: AuthHarness, email: str
) -> None:
    response = _login(auth_harness.client, email=email)

    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_CREDENTIALS"
    assert response.json()["detail"] == "The email or password is incorrect."


def test_repeated_failures_temporarily_lock_sign_in(auth_harness: AuthHarness) -> None:
    first = _login(auth_harness.client, password="incorrect password")
    second = _login(auth_harness.client, password="incorrect password")
    locked = _login(auth_harness.client, password="incorrect password")
    still_locked = _login(auth_harness.client)

    assert first.status_code == second.status_code == 401
    assert locked.status_code == still_locked.status_code == 423
    assert locked.json()["code"] == "ACCOUNT_LOCKED"
    assert locked.json()["retryAfterSeconds"] == 900
    assert locked.headers["retry-after"] == "900"


def test_refresh_rotates_and_reuse_revokes_the_family(auth_harness: AuthHarness) -> None:
    login = _login(auth_harness.client, remember_device=True)
    original_access = login.json()["accessToken"]
    original_refresh = login.cookies["forgesight_refresh"]

    rotated = auth_harness.client.post("/api/v1/auth/refresh", json={})
    rotated_access = rotated.json()["accessToken"]

    assert rotated.status_code == 200
    assert rotated_access != original_access
    assert rotated.cookies["forgesight_refresh"] != original_refresh

    auth_harness.client.cookies.set("forgesight_refresh", original_refresh, path="/api/v1/auth")
    reused = auth_harness.client.post("/api/v1/auth/refresh", json={})
    revoked_access = auth_harness.client.get("/api/v1/me", headers=_authorization(rotated_access))

    assert reused.status_code == 401
    assert reused.json()["code"] == "REFRESH_REUSE_DETECTED"
    assert revoked_access.status_code == 401
    assert revoked_access.json()["code"] == "SESSION_REVOKED"
    assert any(item["eventType"] == "refresh_reuse_detected" for item in auth_harness.events.items)


def test_refresh_requires_cookie_and_expired_session_is_rejected(
    auth_harness: AuthHarness,
) -> None:
    missing = auth_harness.client.post("/api/v1/auth/refresh", json={})
    login = _login(auth_harness.client)
    auth_harness.clock.advance(days=2)
    expired = auth_harness.client.post("/api/v1/auth/refresh", json={})
    expired_access = auth_harness.client.get(
        "/api/v1/me", headers=_authorization(login.json()["accessToken"])
    )

    assert missing.status_code == 401
    assert missing.json()["code"] == "REFRESH_INVALID"
    assert expired.status_code == 401
    assert expired.json()["code"] == "REFRESH_INVALID"
    assert expired_access.status_code == 401
    assert expired_access.json()["code"] == "SESSION_REVOKED"


def test_logout_and_logout_all_revoke_live_access(auth_harness: AuthHarness) -> None:
    first = _login(auth_harness.client)
    second = _login(auth_harness.client)
    first_access = first.json()["accessToken"]
    second_access = second.json()["accessToken"]

    logout_all = auth_harness.client.post(
        "/api/v1/auth/logout-all",
        json={"reason": "security_concern"},
        headers=_authorization(second_access),
    )

    assert logout_all.status_code == 200
    assert logout_all.json() == {"revokedSessions": 2}
    assert (
        auth_harness.client.get("/api/v1/me", headers=_authorization(first_access)).status_code
        == 401
    )
    assert (
        auth_harness.client.get("/api/v1/me", headers=_authorization(second_access)).status_code
        == 401
    )

    third = _login(auth_harness.client)
    third_access = third.json()["accessToken"]
    logout = auth_harness.client.post(
        "/api/v1/auth/logout", json={}, headers=_authorization(third_access)
    )
    assert logout.json() == {"revoked": True}
    assert (
        auth_harness.client.get("/api/v1/me", headers=_authorization(third_access)).status_code
        == 401
    )


def test_owned_session_can_be_revoked_and_foreign_id_is_concealed(
    auth_harness: AuthHarness,
) -> None:
    first = _login(auth_harness.client)
    second = _login(auth_harness.client)
    first_access = first.json()["accessToken"]
    second_access = second.json()["accessToken"]
    sessions = auth_harness.client.get(
        "/api/v1/me/sessions", headers=_authorization(first_access)
    ).json()["items"]
    second_session = next(item for item in sessions if not item["current"])

    revoked = auth_harness.client.delete(
        f"/api/v1/me/sessions/{second_session['id']}",
        headers=_authorization(first_access),
    )
    missing = auth_harness.client.delete(
        "/api/v1/me/sessions/ses_00000000000000000000000000000000",
        headers=_authorization(first_access),
    )

    assert revoked.json() == {"revoked": True}
    assert (
        auth_harness.client.get("/api/v1/me", headers=_authorization(second_access)).status_code
        == 401
    )
    assert missing.status_code == 404
    assert missing.json()["code"] == "RESOURCE_NOT_FOUND"


def test_password_reset_is_non_enumerating_single_use_and_revokes_sessions(
    auth_harness: AuthHarness,
) -> None:
    active_session = _login(auth_harness.client)
    old_access = active_session.json()["accessToken"]
    unknown = auth_harness.client.post(
        "/api/v1/auth/password-reset/request", json={"email": "unknown@example.com"}
    )
    known = auth_harness.client.post(
        "/api/v1/auth/password-reset/request", json={"email": "viewer@example.com"}
    )

    assert unknown.status_code == known.status_code == 202
    assert unknown.json() == known.json() == {"accepted": True}
    assert len(auth_harness.reset_notifier.tokens) == 1

    reset_token = auth_harness.reset_notifier.tokens[0]
    completed = auth_harness.client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": reset_token, "newPassword": _NEW_PASSWORD},
    )
    reused = auth_harness.client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": reset_token, "newPassword": _NEW_PASSWORD},
    )

    assert completed.json() == {"reset": True}
    assert reused.status_code == 400
    assert reused.json()["code"] == "RESET_TOKEN_INVALID"
    assert (
        auth_harness.client.get("/api/v1/me", headers=_authorization(old_access)).status_code == 401
    )
    assert _login(auth_harness.client).status_code == 401
    assert _login(auth_harness.client, password=_NEW_PASSWORD).status_code == 200


def test_password_reset_endpoint_is_rate_limited(auth_harness: AuthHarness) -> None:
    responses = [
        auth_harness.client.post(
            "/api/v1/auth/password-reset/request", json={"email": "unknown@example.com"}
        )
        for _ in range(6)
    ]

    assert [response.status_code for response in responses] == [202, 202, 202, 202, 202, 429]
    assert responses[-1].json()["code"] == "RATE_LIMITED"


def test_invalid_auth_payloads_use_canonical_problem_shape(auth_harness: AuthHarness) -> None:
    invalid_login = auth_harness.client.post(
        "/api/v1/auth/login",
        json={"email": "not-an-email", "password": "short", "unexpected": True},
    )
    invalid_reset = auth_harness.client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": "too-short", "newPassword": "too-short"},
    )

    assert invalid_login.status_code == invalid_reset.status_code == 400
    assert invalid_login.headers["content-type"].startswith("application/problem+json")
    assert invalid_login.json()["code"] == "VALIDATION_FAILED"
    assert "unexpected" in invalid_login.json()["fieldErrors"]
    assert invalid_reset.json()["code"] == "VALIDATION_FAILED"
