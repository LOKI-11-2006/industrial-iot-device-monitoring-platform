"""Executable Phase 2 OpenAPI contract tests."""

from fastapi.testclient import TestClient


def test_openapi_registers_phase_two_authentication_routes(client: TestClient) -> None:
    document = client.get("/openapi.json").json()

    assert document["info"]["title"] == "ForgeSight Industrial IoT API"
    assert document["info"]["version"] == "0.2.0"
    assert set(document["paths"]) == {
        "/api/v1/auth/login",
        "/api/v1/auth/logout",
        "/api/v1/auth/logout-all",
        "/api/v1/auth/password-reset/confirm",
        "/api/v1/auth/password-reset/request",
        "/api/v1/auth/refresh",
        "/api/v1/health/live",
        "/api/v1/me",
        "/api/v1/me/sessions",
        "/api/v1/me/sessions/{session_id}",
        "/api/v1/roles",
    }
    assert document["paths"]["/api/v1/health/live"]["get"]["tags"] == ["Health"]
    assert document["components"]["securitySchemes"]["BearerAuth"] == {
        "type": "http",
        "description": "Short-lived ForgeSight access JWT.",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }


def test_sensitive_authentication_schemas_are_strict(client: TestClient) -> None:
    document = client.get("/openapi.json").json()
    schemas = document["components"]["schemas"]

    assert schemas["LoginRequest"]["additionalProperties"] is False
    assert schemas["LoginRequest"]["properties"]["password"]["format"] == "password"
    assert schemas["PasswordResetConfirm"]["properties"]["token"]["format"] == "password"
    assert document["paths"]["/api/v1/auth/password-reset/request"]["post"]["responses"]["202"]


def test_swagger_and_redoc_are_available_in_non_production(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
