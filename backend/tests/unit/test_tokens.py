"""JWT key rotation, claim validation, and opaque-token security tests."""

from __future__ import annotations

import base64
import json
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
import pytest

from app.config.settings import DeploymentEnvironment, Settings
from app.core.errors import ApplicationError
from app.models.auth import UserAccount, UserRole
from app.security.tokens import (
    AccessTokenCodec,
    OpaqueTokenManager,
    development_signing_material,
    load_signing_material,
    parse_signing_secret,
)


def _settings(**changes: object) -> Settings:
    return Settings(
        _env_file=None,
        environment=DeploymentEnvironment.TEST,
        cors_allowed_origins=["https://console.example.com"],
        allowed_hosts=["testserver"],
        aws_resource_prefix="forgesight-test",
        **changes,
    )


def _user() -> UserAccount:
    return UserAccount(
        id="usr_token1",
        email="token@example.com",
        display_name="Token User",
        password_hash="unused",
        role=UserRole.FACTORY_MANAGER,
        factory_ids=("fac_alpha",),
        token_version=3,
        scope_version=4,
    )


def test_access_token_contains_and_validates_minimal_identity_claims() -> None:
    settings = _settings()
    material = development_signing_material("ES256")
    codec = AccessTokenCodec(settings, material)
    now = datetime.now(UTC)

    token = codec.issue(_user(), "ses_token", now)
    claims = codec.decode(token)

    assert claims.subject == "usr_token1"
    assert claims.session_id == "ses_token"
    assert claims.role == "FACTORY_MANAGER"
    assert claims.token_version == 3
    assert claims.scope_version == 4
    assert claims.token_id.startswith("jti_")
    assert codec.expires_in == 900
    assert "token@example.com" not in token


def test_expired_or_tampered_access_tokens_are_rejected() -> None:
    settings = _settings(jwt_clock_skew_seconds=0)
    material = development_signing_material("ES256")
    codec = AccessTokenCodec(settings, material)
    expired = codec.issue(_user(), "ses_expired", datetime.now(UTC) - timedelta(hours=1))
    valid = codec.issue(_user(), "ses_valid", datetime.now(UTC))
    head, payload, signature = valid.split(".")
    tampered_signature = ("A" if signature[0] != "A" else "B") + signature[1:]

    with pytest.raises(ApplicationError) as expired_error:
        codec.decode(expired)
    with pytest.raises(ApplicationError) as tampered_error:
        codec.decode(".".join((head, payload, tampered_signature)))

    assert expired_error.value.code == "TOKEN_EXPIRED"
    assert tampered_error.value.code == "AUTHENTICATION_REQUIRED"


def test_unknown_key_id_is_rejected() -> None:
    settings = _settings()
    material = development_signing_material("ES256")
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
            "sub": "usr_token1",
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(minutes=5),
            "jti": "jti_test",
            "sid": "ses_test",
            "role": "VIEWER",
            "ver": 1,
            "sv": 1,
            "typ": "access",
        },
        material.private_key_pem,
        algorithm="ES256",
        headers={"kid": "retired-key"},
    )

    with pytest.raises(ApplicationError) as caught:
        AccessTokenCodec(settings, material).decode(token)

    assert caught.value.code == "AUTHENTICATION_REQUIRED"


def test_signing_secret_parser_supports_rotation_aware_public_keys() -> None:
    material = development_signing_material("ES256")
    pepper = base64.urlsafe_b64encode(material.token_hash_pepper).decode().rstrip("=")
    parsed = parse_signing_secret(
        json.dumps(
            {
                "activeKid": material.active_key_id,
                "algorithm": material.algorithm,
                "privateKeyPem": material.private_key_pem,
                "publicKeys": dict(material.public_keys),
                "tokenHashPepper": pepper,
            }
        )
    )

    assert parsed.active_key_id == material.active_key_id
    assert parsed.public_keys == material.public_keys
    assert parsed.token_hash_pepper == material.token_hash_pepper


def test_signing_secret_rejects_mismatched_active_key_pair() -> None:
    material = development_signing_material("ES256")
    development_signing_material.cache_clear()
    replacement = development_signing_material("ES256")
    pepper = base64.urlsafe_b64encode(material.token_hash_pepper).decode().rstrip("=")

    with pytest.raises(ValueError, match="do not match"):
        parse_signing_secret(
            json.dumps(
                {
                    "activeKid": material.active_key_id,
                    "algorithm": material.algorithm,
                    "privateKeyPem": material.private_key_pem,
                    "publicKeys": {
                        material.active_key_id: replacement.public_keys[replacement.active_key_id]
                    },
                    "tokenHashPepper": pepper,
                }
            )
        )


@pytest.mark.parametrize(
    "payload",
    [
        "[]",
        "{}",
        '{"activeKid":"key","algorithm":"HS256"}',
        (
            '{"activeKid":"key","algorithm":"ES256","privateKeyPem":"x",'
            '"publicKeys":[],"tokenHashPepper":"eA"}'
        ),
    ],
)
def test_invalid_signing_secret_documents_fail_closed(payload: str) -> None:
    with pytest.raises(ValueError, match="Signing secret"):
        parse_signing_secret(payload)


class FakeSecretsManager:
    def __init__(self, secret_string: str) -> None:
        self.secret_string = secret_string
        self.requested_secret_id: str | None = None

    def get_secret_value(self, *, SecretId: str) -> dict[str, Any]:  # noqa: N803
        self.requested_secret_id = SecretId
        return {"SecretString": self.secret_string}


def test_signing_material_loads_from_the_configured_secret_reference() -> None:
    material = development_signing_material("ES256")
    secret_string = json.dumps(
        {
            "activeKid": material.active_key_id,
            "algorithm": material.algorithm,
            "privateKeyPem": material.private_key_pem,
            "publicKeys": dict(material.public_keys),
            "tokenHashPepper": base64.urlsafe_b64encode(material.token_hash_pepper)
            .decode()
            .rstrip("="),
        }
    )
    client = FakeSecretsManager(secret_string)
    secret_arn = "arn:aws:secretsmanager:ap-south-1:123456789012:secret:forgesight/test/jwt-AbCd12"

    loaded = load_signing_material(_settings(jwt_signing_key_secret_arn=secret_arn), client=client)

    assert loaded.active_key_id == material.active_key_id
    assert client.requested_secret_id == secret_arn


def test_opaque_tokens_are_random_and_only_keyed_digests_are_stable() -> None:
    manager = OpaqueTokenManager(b"x" * 32)
    first = manager.generate("rt")
    second = manager.generate("rt")

    assert first.startswith("rt_")
    assert first != second
    assert manager.digest(first) == manager.digest(first)
    assert manager.digest(first) != manager.digest(second)
    assert len(manager.fingerprint("192.0.2.1")) == 32


def test_opaque_token_manager_rejects_short_pepper() -> None:
    with pytest.raises(ValueError, match="at least 32"):
        OpaqueTokenManager(b"short")


def test_development_material_supports_rsa_for_configuration_parity() -> None:
    assert development_signing_material("RS256").algorithm == "RS256"
