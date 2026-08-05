"""Shared fixtures for composed backend tests."""

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config.settings import DeploymentEnvironment, Settings
from app.core.application import create_app


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        _env_file=None,
        environment=DeploymentEnvironment.TEST,
        docs_enabled=True,
        cors_allowed_origins=["https://console.example.com"],
        allowed_hosts=["testserver"],
        aws_resource_prefix="forgesight-test",
    )


@pytest.fixture
def application(test_settings: Settings) -> FastAPI:
    return create_app(test_settings)


@pytest.fixture
def client(application: FastAPI) -> Iterator[TestClient]:
    with TestClient(application) as test_client:
        yield test_client
