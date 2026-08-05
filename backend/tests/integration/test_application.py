"""Composed FastAPI application behavior tests."""

from fastapi import FastAPI, Query
from fastapi.testclient import TestClient


def test_liveness_uses_the_canonical_minimal_contract(client: TestClient) -> None:
    response = client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}
    assert response.headers["content-type"] == "application/json"
    assert response.headers["x-correlation-id"].startswith("corr_")


def test_valid_correlation_id_is_propagated(client: TestClient) -> None:
    response = client.get(
        "/api/v1/health/live",
        headers={"X-Correlation-ID": "corr_client-1234"},
    )

    assert response.headers["x-correlation-id"] == "corr_client-1234"


def test_invalid_correlation_id_is_replaced(client: TestClient) -> None:
    response = client.get(
        "/api/v1/health/live",
        headers={"X-Correlation-ID": "invalid value with spaces"},
    )

    assert response.headers["x-correlation-id"].startswith("corr_")
    assert response.headers["x-correlation-id"] != "invalid value with spaces"


def test_unknown_routes_return_a_safe_problem(client: TestClient) -> None:
    response = client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json() == {
        "type": "https://docs.forgesight.example/problems/resource-not-found",
        "title": "Resource not found",
        "status": 404,
        "code": "RESOURCE_NOT_FOUND",
        "detail": "The requested resource was not found.",
        "instance": "/api/v1/does-not-exist",
        "correlationId": response.headers["x-correlation-id"],
    }


def test_method_errors_do_not_expose_framework_details(client: TestClient) -> None:
    response = client.post("/api/v1/health/live")

    assert response.status_code == 405
    assert response.json()["code"] == "METHOD_NOT_ALLOWED"
    assert "allowed" in response.json()["detail"].lower()


def test_validation_errors_use_field_mappings(application: FastAPI) -> None:
    @application.get("/test/validated")
    async def validated(value: int = Query(ge=1)) -> dict[str, int]:
        return {"value": value}

    with TestClient(application) as client:
        response = client.get("/test/validated?value=invalid")

    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_FAILED"
    assert "value" in response.json()["fieldErrors"]


def test_unexpected_errors_return_safe_generic_details(application: FastAPI) -> None:
    @application.get("/test/failure")
    async def failure() -> None:
        raise RuntimeError("sensitive internal detail")

    with TestClient(application, raise_server_exceptions=False) as client:
        response = client.get("/test/failure")

    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"
    assert "sensitive internal detail" not in response.text
