"""HTTP boundary security regression tests."""

import pytest
from fastapi.testclient import TestClient

from app.config.settings import DeploymentEnvironment, Settings
from app.core.application import create_app
from app.repositories.auth import InMemoryAuthRepository
from app.security.tokens import development_signing_material


def test_security_headers_are_present_on_api_responses(client: TestClient) -> None:
    response = client.get("/api/v1/health/live")

    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert "camera=()" in response.headers["permissions-policy"]
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    assert "strict-transport-security" not in response.headers


def test_cors_allows_only_the_configured_origin(client: TestClient) -> None:
    allowed = client.options(
        "/api/v1/health/live",
        headers={
            "Origin": "https://console.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    denied = client.options(
        "/api/v1/health/live",
        headers={
            "Origin": "https://attacker.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "https://console.example.com"
    assert denied.status_code == 400
    assert denied.headers["content-type"].startswith("application/problem+json")
    assert denied.json()["code"] == "CORS_ORIGIN_DENIED"
    assert "access-control-allow-origin" not in denied.headers


def test_untrusted_host_is_rejected(client: TestClient) -> None:
    response = client.get("/api/v1/health/live", headers={"Host": "attacker.example"})

    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "INVALID_HOST"
    assert response.json()["correlationId"] == response.headers["x-correlation-id"]


def test_production_disables_docs_and_enables_hsts() -> None:
    settings = Settings(
        _env_file=None,
        environment=DeploymentEnvironment.PRODUCTION,
        docs_enabled=False,
        cors_allowed_origins=["https://console.example.com"],
        allowed_hosts=["api.example.com"],
        aws_resource_prefix="forgesight-prod",
        jwt_signing_key_secret_arn=(
            "arn:aws:secretsmanager:ap-south-1:123456789012:secret:forgesight/prod/jwt-AbCd12"
        ),
        refresh_cookie_secure=True,
    )
    application = create_app(
        settings,
        auth_repository=InMemoryAuthRepository(),
        signing_material=development_signing_material(),
    )

    with TestClient(application, base_url="https://api.example.com") as client:
        health = client.get("/api/v1/health/live")
        docs = client.get("/docs")

    assert health.headers["strict-transport-security"] == "max-age=31536000; includeSubDomains"
    assert docs.status_code == 404


def test_production_refuses_implicit_in_memory_authentication() -> None:
    settings = Settings(
        _env_file=None,
        environment=DeploymentEnvironment.PRODUCTION,
        docs_enabled=False,
        cors_allowed_origins=["https://console.example.com"],
        allowed_hosts=["api.example.com"],
        aws_resource_prefix="forgesight-prod",
        jwt_signing_key_secret_arn=(
            "arn:aws:secretsmanager:ap-south-1:123456789012:secret:forgesight/prod/jwt-AbCd12"
        ),
        refresh_cookie_secure=True,
    )

    with pytest.raises(ValueError, match="durable repository"):
        create_app(settings, signing_material=development_signing_material())
