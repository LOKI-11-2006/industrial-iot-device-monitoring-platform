"""Public OpenAPI bootstrap contract tests."""

from fastapi.testclient import TestClient


def test_openapi_registers_only_the_phase_one_api_route(client: TestClient) -> None:
    document = client.get("/openapi.json").json()

    assert document["info"]["title"] == "ForgeSight Industrial IoT API"
    assert document["info"]["version"] == "0.1.0"
    assert set(document["paths"]) == {"/api/v1/health/live"}
    assert document["paths"]["/api/v1/health/live"]["get"]["tags"] == ["Health"]


def test_swagger_and_redoc_are_available_in_non_production(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
