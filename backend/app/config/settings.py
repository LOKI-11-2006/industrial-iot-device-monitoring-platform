"""Validated application settings sourced exclusively from the runtime environment."""

from __future__ import annotations

import json
import re
from enum import StrEnum
from functools import lru_cache
from typing import Any, Literal, Self

from pydantic import AnyHttpUrl, Field, TypeAdapter, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_RESOURCE_PREFIX_PATTERN = re.compile(r"^[a-z][a-z0-9-]{2,39}$")
_SECRETS_MANAGER_ARN_PATTERN = re.compile(
    r"^arn:(aws|aws-us-gov|aws-cn):secretsmanager:[a-z0-9-]+:\d{12}:secret:[A-Za-z0-9/_+=.@-]+$"
)


class DeploymentEnvironment(StrEnum):
    """Supported isolated deployment environments."""

    LOCAL = "local"
    TEST = "test"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


def _parse_string_list(value: Any) -> Any:
    """Accept deployment-friendly JSON arrays and convenient local comma-separated values."""

    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if not stripped:
        return []
    if stripped.startswith("["):
        return json.loads(stripped)
    return [item.strip() for item in stripped.split(",") if item.strip()]


class Settings(BaseSettings):
    """Single validated configuration boundary for the API process."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="IOT_API_",
        case_sensitive=False,
        extra="forbid",
        validate_default=True,
    )

    app_name: str = Field(default="ForgeSight Industrial IoT API", min_length=3, max_length=100)
    service_name: str = Field(default="iot-platform-api", pattern=r"^[a-z][a-z0-9-]{2,63}$")
    version: str = Field(default="0.1.0", pattern=r"^\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?$")
    environment: DeploymentEnvironment = DeploymentEnvironment.LOCAL
    debug: bool = False
    docs_enabled: bool = True
    api_v1_prefix: str = Field(default="/api/v1", pattern=r"^/[a-z0-9/_-]*[a-z0-9]$")

    cors_allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:4173"])
    cors_allow_credentials: bool = True
    allowed_hosts: list[str] = Field(
        default_factory=lambda: ["localhost", "127.0.0.1", "testserver"]
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    aws_region: str = Field(default="ap-south-1", pattern=r"^[a-z]{2}(?:-gov)?-[a-z]+-\d$")
    aws_resource_prefix: str = "forgesight-local"
    aws_endpoint_url: str | None = None
    jwt_signing_key_secret_arn: str | None = None

    @field_validator("cors_allowed_origins", "allowed_hosts", mode="before")
    @classmethod
    def parse_list_settings(cls, value: Any) -> Any:
        """Normalize list settings before field validation."""

        return _parse_string_list(value)

    @field_validator("cors_allowed_origins")
    @classmethod
    def validate_cors_origins(cls, origins: list[str]) -> list[str]:
        """Reject wildcard and malformed origins before middleware composition."""

        if not origins:
            raise ValueError("At least one explicit CORS origin is required.")

        normalized: list[str] = []
        url_adapter = TypeAdapter(AnyHttpUrl)
        for origin in origins:
            if origin == "*":
                raise ValueError("Wildcard CORS origins are not permitted.")
            parsed = url_adapter.validate_python(origin)
            if parsed.path not in {None, "/"} or parsed.query or parsed.fragment:
                raise ValueError("CORS origins must not contain a path, query, or fragment.")
            normalized.append(str(parsed).rstrip("/"))
        return normalized

    @field_validator("allowed_hosts")
    @classmethod
    def validate_allowed_hosts(cls, hosts: list[str]) -> list[str]:
        """Require bounded host names and prohibit trust-all configuration."""

        if not hosts:
            raise ValueError("At least one allowed host is required.")
        if "*" in hosts:
            raise ValueError("Wildcard trusted hosts are not permitted.")
        if any("/" in host or "://" in host for host in hosts):
            raise ValueError("Allowed hosts must be host names without a scheme or path.")
        return [host.lower() for host in hosts]

    @field_validator("aws_resource_prefix")
    @classmethod
    def validate_resource_prefix(cls, value: str) -> str:
        """Keep generated AWS resource names predictable and environment-scoped."""

        if not _RESOURCE_PREFIX_PATTERN.fullmatch(value):
            raise ValueError(
                "AWS resource prefix must be 3-40 lowercase letters, digits, or hyphens."
            )
        return value

    @field_validator("aws_endpoint_url", mode="before")
    @classmethod
    def normalize_optional_url(cls, value: Any) -> Any:
        """Treat empty environment values as absent."""

        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("aws_endpoint_url")
    @classmethod
    def validate_endpoint_url(cls, value: str | None) -> str | None:
        """Validate a local AWS-compatible endpoint without accepting arbitrary strings."""

        if value is None:
            return None
        return str(TypeAdapter(AnyHttpUrl).validate_python(value)).rstrip("/")

    @field_validator("jwt_signing_key_secret_arn", mode="before")
    @classmethod
    def normalize_optional_arn(cls, value: Any) -> Any:
        """Normalize empty local placeholders without ever loading key material."""

        if isinstance(value, str) and not value.strip():
            return None
        return value

    @model_validator(mode="after")
    def enforce_environment_invariants(self) -> Self:
        """Fail startup when production configuration weakens the approved security posture."""

        if self.environment is not DeploymentEnvironment.PRODUCTION:
            return self

        violations: list[str] = []
        if self.debug:
            violations.append("debug must be disabled")
        if self.docs_enabled:
            violations.append("public API documentation must be disabled")
        if self.aws_endpoint_url is not None:
            violations.append("custom AWS endpoints are not permitted")
        if not self.jwt_signing_key_secret_arn or not _SECRETS_MANAGER_ARN_PATTERN.fullmatch(
            self.jwt_signing_key_secret_arn
        ):
            violations.append("a valid Secrets Manager JWT signing-key ARN is required")
        if any(not origin.startswith("https://") for origin in self.cors_allowed_origins):
            violations.append("all CORS origins must use HTTPS")

        if violations:
            raise ValueError("Invalid production configuration: " + "; ".join(violations) + ".")
        return self

    @property
    def is_production(self) -> bool:
        """Return whether strict production-only controls should be enabled."""

        return self.environment is DeploymentEnvironment.PRODUCTION


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load and cache one immutable-by-convention settings object per process."""

    return Settings()
