"""Typed configuration validation tests."""

import pytest
from pydantic import ValidationError

from app.config.settings import DeploymentEnvironment, Settings, get_settings


def test_local_defaults_are_explicit_and_safe() -> None:
    settings = Settings(_env_file=None)

    assert settings.environment is DeploymentEnvironment.LOCAL
    assert settings.debug is False
    assert settings.aws_region == "ap-south-1"
    assert settings.cors_allowed_origins == ["http://localhost:4173"]
    assert settings.is_production is False


def test_list_settings_accept_json_and_comma_separated_values() -> None:
    settings = Settings(
        _env_file=None,
        cors_allowed_origins='["https://one.example.com","https://two.example.com"]',
        allowed_hosts="api.example.com,admin.example.com",
    )

    assert settings.cors_allowed_origins == [
        "https://one.example.com",
        "https://two.example.com",
    ]
    assert settings.allowed_hosts == ["api.example.com", "admin.example.com"]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("cors_allowed_origins", ["*"], "Wildcard CORS"),
        ("cors_allowed_origins", ["https://example.com/path"], "must not contain a path"),
        ("allowed_hosts", ["*"], "Wildcard trusted hosts"),
        ("allowed_hosts", ["https://api.example.com"], "without a scheme"),
        ("aws_resource_prefix", "INVALID_PREFIX", "AWS resource prefix"),
    ],
)
def test_unsafe_boundary_values_are_rejected(field: str, value: object, message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        Settings(_env_file=None, **{field: value})


def test_empty_optional_deployment_values_are_normalized() -> None:
    settings = Settings(
        _env_file=None,
        aws_endpoint_url="",
        jwt_signing_key_secret_arn="  ",
    )

    assert settings.aws_endpoint_url is None
    assert settings.jwt_signing_key_secret_arn is None


def test_production_requires_the_complete_security_posture() -> None:
    with pytest.raises(ValidationError, match="Invalid production configuration"):
        Settings(
            _env_file=None,
            environment=DeploymentEnvironment.PRODUCTION,
            debug=True,
            docs_enabled=True,
            cors_allowed_origins=["http://console.example.com"],
            aws_endpoint_url="http://localhost:4566",
        )


def test_valid_production_configuration_enables_production_controls() -> None:
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

    assert settings.is_production is True
    assert settings.docs_enabled is False
    assert settings.jwt_access_token_ttl_seconds == 900
    assert settings.refresh_cookie_secure is True


def test_cached_settings_loader_returns_one_process_instance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("IOT_API_ENVIRONMENT", "test")
    get_settings.cache_clear()
    try:
        assert get_settings() is get_settings()
        assert get_settings().environment is DeploymentEnvironment.TEST
    finally:
        get_settings.cache_clear()
