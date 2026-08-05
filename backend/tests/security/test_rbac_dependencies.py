"""Protected-route integration tests for reusable RBAC dependencies."""

from __future__ import annotations

from typing import Annotated

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient

from app.api.dependencies import require_factory_permission, require_permission
from app.config.settings import DeploymentEnvironment, Settings
from app.core.application import create_app
from app.models.auth import AuthenticatedPrincipal, UserAccount, UserRole
from app.repositories.auth import InMemoryAuthRepository
from app.security.passwords import PasswordManager
from app.security.permissions import Permission
from app.security.tokens import development_signing_material

_PASSWORD = "Protected route password 1!"


@pytest.fixture
def rbac_client() -> TestClient:
    passwords = PasswordManager()
    repository = InMemoryAuthRepository(
        [
            UserAccount(
                id="usr_rbacviewer",
                email="rbac.viewer@example.com",
                display_name="RBAC Viewer",
                password_hash=passwords.hash_password(_PASSWORD),
                role=UserRole.VIEWER,
                factory_ids=("fac_allowed",),
            ),
            UserAccount(
                id="usr_rbacadmin",
                email="rbac.admin@example.com",
                display_name="RBAC Admin",
                password_hash=passwords.hash_password(_PASSWORD),
                role=UserRole.SUPER_ADMINISTRATOR,
            ),
        ]
    )
    settings = Settings(
        _env_file=None,
        environment=DeploymentEnvironment.TEST,
        cors_allowed_origins=["https://console.example.com"],
        allowed_hosts=["testserver"],
        aws_resource_prefix="forgesight-test",
    )
    application = create_app(
        settings,
        auth_repository=repository,
        signing_material=development_signing_material(),
    )

    @application.get("/api/v1/test/security-manage")
    async def security_manage(
        principal: Annotated[
            AuthenticatedPrincipal,
            Depends(require_permission(Permission.SECURITY_MANAGE)),
        ],
    ) -> dict[str, str]:
        return {"userId": principal.user_id}

    @application.get("/api/v1/test/factories/{factory_id}")
    async def factory_read(
        principal: Annotated[
            AuthenticatedPrincipal,
            Depends(require_factory_permission(Permission.FACTORIES_READ)),
        ],
    ) -> dict[str, str]:
        return {"userId": principal.user_id}

    with TestClient(application) as client:
        yield client


def _access_token(client: TestClient, email: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": _PASSWORD, "rememberDevice": False},
    )
    return str(response.json()["accessToken"])


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_permission_dependency_defaults_to_deny(rbac_client: TestClient) -> None:
    missing = rbac_client.get("/api/v1/test/security-manage")
    viewer = _access_token(rbac_client, "rbac.viewer@example.com")
    denied = rbac_client.get("/api/v1/test/security-manage", headers=_headers(viewer))
    admin = _access_token(rbac_client, "rbac.admin@example.com")
    allowed = rbac_client.get("/api/v1/test/security-manage", headers=_headers(admin))

    assert missing.status_code == 401
    assert missing.headers["www-authenticate"] == "Bearer"
    assert denied.status_code == 403
    assert denied.json()["code"] == "PERMISSION_DENIED"
    assert allowed.json() == {"userId": "usr_rbacadmin"}


def test_factory_dependency_uses_server_trusted_assignments(rbac_client: TestClient) -> None:
    viewer = _access_token(rbac_client, "rbac.viewer@example.com")

    allowed = rbac_client.get("/api/v1/test/factories/fac_allowed", headers=_headers(viewer))
    denied = rbac_client.get("/api/v1/test/factories/fac_other", headers=_headers(viewer))

    assert allowed.status_code == 200
    assert denied.status_code == 403
    assert denied.json()["code"] == "FACTORY_SCOPE_DENIED"
