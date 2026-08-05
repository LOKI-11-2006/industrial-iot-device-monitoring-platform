"""Asymmetric JWT access tokens and opaque credential hashing."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from types import MappingProxyType
from typing import Any, Literal, Protocol, cast
from uuid import uuid4

import boto3  # type: ignore[import-untyped]
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa

from app.config.settings import Settings
from app.core.errors import ApplicationError, authentication_error
from app.models.auth import UserAccount

JwtAlgorithm = Literal["ES256", "RS256"]


@dataclass(frozen=True, slots=True)
class SigningMaterial:
    """Active signing key, rotation-aware public keys, and token-hash pepper."""

    active_key_id: str
    algorithm: JwtAlgorithm
    private_key_pem: str
    public_keys: Mapping[str, str]
    token_hash_pepper: bytes


class SecretsManagerClient(Protocol):
    """Small boto3-compatible port used to load signing material."""

    def get_secret_value(self, *, SecretId: str) -> dict[str, Any]:  # noqa: N803
        """Return one Secrets Manager value."""


def _urlsafe_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _required_string(payload: Mapping[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Signing secret field {key!r} must be a non-empty string.")
    return value


def _validate_key_set(
    algorithm: JwtAlgorithm,
    active_key_id: str,
    private_key_pem: str,
    public_keys: Mapping[str, str],
) -> None:
    private_key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
    if algorithm == "ES256":
        if not isinstance(private_key, ec.EllipticCurvePrivateKey) or not isinstance(
            private_key.curve, ec.SECP256R1
        ):
            raise ValueError("ES256 signing material requires a P-256 EC private key.")
    elif not isinstance(private_key, rsa.RSAPrivateKey) or private_key.key_size < 2048:
        raise ValueError(
            "RS256 signing material requires an RSA private key of at least 2048 bits."
        )

    loaded_public_keys: dict[str, ec.EllipticCurvePublicKey | rsa.RSAPublicKey] = {}
    for key_id, public_key_pem in public_keys.items():
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        if algorithm == "ES256":
            if not isinstance(public_key, ec.EllipticCurvePublicKey) or not isinstance(
                public_key.curve, ec.SECP256R1
            ):
                raise ValueError("Every ES256 verification key must be a P-256 EC public key.")
        elif not isinstance(public_key, rsa.RSAPublicKey) or public_key.key_size < 2048:
            raise ValueError(
                "Every RS256 verification key must be an RSA public key of at least 2048 bits."
            )
        loaded_public_keys[key_id] = public_key

    active_public = loaded_public_keys[active_key_id]
    derived_public = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    configured_public = active_public.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    if not hmac.compare_digest(derived_public, configured_public):
        raise ValueError("The active JWT private and public keys do not match.")


def parse_signing_secret(secret_string: str) -> SigningMaterial:
    """Validate the rotation-friendly JSON document stored in Secrets Manager."""

    parsed = json.loads(secret_string)
    if not isinstance(parsed, dict):
        raise ValueError("Signing secret must contain a JSON object.")
    payload = cast(dict[str, object], parsed)
    active_key_id = _required_string(payload, "activeKid")
    algorithm_value = _required_string(payload, "algorithm")
    if algorithm_value not in {"ES256", "RS256"}:
        raise ValueError("Signing secret algorithm must be ES256 or RS256.")
    algorithm = cast(JwtAlgorithm, algorithm_value)
    private_key_pem = _required_string(payload, "privateKeyPem")
    pepper = _urlsafe_decode(_required_string(payload, "tokenHashPepper"))
    if len(pepper) < 32:
        raise ValueError("Signing secret tokenHashPepper must decode to at least 32 bytes.")

    raw_public_keys = payload.get("publicKeys")
    if not isinstance(raw_public_keys, dict):
        raise ValueError("Signing secret publicKeys must be an object.")
    public_keys: dict[str, str] = {}
    for key_id, public_key in raw_public_keys.items():
        if not isinstance(key_id, str) or not isinstance(public_key, str) or not public_key:
            raise ValueError("Signing secret publicKeys entries must be non-empty strings.")
        public_keys[key_id] = public_key
    if active_key_id not in public_keys:
        raise ValueError("Signing secret publicKeys must include activeKid.")

    _validate_key_set(algorithm, active_key_id, private_key_pem, public_keys)

    return SigningMaterial(
        active_key_id=active_key_id,
        algorithm=algorithm,
        private_key_pem=private_key_pem,
        public_keys=MappingProxyType(public_keys),
        token_hash_pepper=pepper,
    )


def load_signing_material(
    settings: Settings,
    client: SecretsManagerClient | None = None,
) -> SigningMaterial:
    """Load and validate signing material or create one process-local development key."""

    if settings.jwt_signing_key_secret_arn is None:
        return development_signing_material(settings.jwt_algorithm)

    secrets_client = client
    if secrets_client is None:
        secrets_client = cast(
            SecretsManagerClient,
            boto3.client(
                "secretsmanager",
                region_name=settings.aws_region,
                endpoint_url=settings.aws_endpoint_url,
            ),
        )
    response = secrets_client.get_secret_value(SecretId=settings.jwt_signing_key_secret_arn)
    secret_string = response.get("SecretString")
    if not isinstance(secret_string, str):
        raise ValueError("JWT signing secret must use Secrets Manager SecretString JSON.")
    material = parse_signing_secret(secret_string)
    if material.algorithm != settings.jwt_algorithm:
        raise ValueError("Configured JWT algorithm does not match the signing secret.")
    return material


@lru_cache(maxsize=2)
def development_signing_material(algorithm: JwtAlgorithm = "ES256") -> SigningMaterial:
    """Create one ephemeral asymmetric key set for a non-production process."""

    private_key: ec.EllipticCurvePrivateKey | rsa.RSAPrivateKey
    if algorithm == "ES256":
        private_key = ec.generate_private_key(ec.SECP256R1())
    else:
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    key_id = f"ephemeral-{algorithm.lower()}"
    return SigningMaterial(
        active_key_id=key_id,
        algorithm=algorithm,
        private_key_pem=private_pem,
        public_keys=MappingProxyType({key_id: public_pem}),
        token_hash_pepper=secrets.token_bytes(32),
    )


@dataclass(frozen=True, slots=True)
class AccessTokenClaims:
    """Validated access-token claims used by the session service."""

    subject: str
    session_id: str
    role: str
    token_version: int
    scope_version: int
    token_id: str


class AccessTokenCodec:
    """Issue and strictly verify short-lived asymmetric access JWTs."""

    def __init__(self, settings: Settings, material: SigningMaterial) -> None:
        self._issuer = settings.jwt_issuer
        self._audience = settings.jwt_audience
        self._algorithm = settings.jwt_algorithm
        self._ttl_seconds = settings.jwt_access_token_ttl_seconds
        self._clock_skew_seconds = settings.jwt_clock_skew_seconds
        self._material = material

    @property
    def expires_in(self) -> int:
        """Return the configured access-token lifetime in seconds."""

        return self._ttl_seconds

    def issue(self, user: UserAccount, session_id: str, now: datetime) -> str:
        """Issue a minimal access token referencing live server-side authorization state."""

        payload: dict[str, object] = {
            "iss": self._issuer,
            "aud": self._audience,
            "sub": user.id,
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(seconds=self._ttl_seconds),
            "jti": f"jti_{uuid4().hex}",
            "sid": session_id,
            "role": user.role.value,
            "ver": user.token_version,
            "sv": user.scope_version,
            "typ": "access",
        }
        return jwt.encode(
            payload,
            self._material.private_key_pem,
            algorithm=self._algorithm,
            headers={"kid": self._material.active_key_id, "typ": "JWT"},
        )

    def decode(self, token: str) -> AccessTokenClaims:
        """Verify signature, key ID, algorithm, registered claims, and token type."""

        try:
            header = cast(dict[str, object], jwt.get_unverified_header(token))
            key_id = header.get("kid")
            algorithm = header.get("alg")
            if not isinstance(key_id, str) or algorithm != self._algorithm:
                raise authentication_error()
            public_key = self._material.public_keys.get(key_id)
            if public_key is None:
                raise authentication_error()
            payload = cast(
                dict[str, object],
                jwt.decode(
                    token,
                    public_key,
                    algorithms=[self._algorithm],
                    audience=self._audience,
                    issuer=self._issuer,
                    leeway=self._clock_skew_seconds,
                    options={
                        "require": [
                            "iss",
                            "aud",
                            "sub",
                            "iat",
                            "nbf",
                            "exp",
                            "jti",
                            "sid",
                            "role",
                            "ver",
                            "sv",
                            "typ",
                        ]
                    },
                ),
            )
            if payload.get("typ") != "access":
                raise authentication_error()
            subject = payload.get("sub")
            session_id = payload.get("sid")
            role = payload.get("role")
            token_id = payload.get("jti")
            token_version = payload.get("ver")
            scope_version = payload.get("sv")
            if not all(isinstance(value, str) for value in (subject, session_id, role, token_id)):
                raise authentication_error()
            if type(token_version) is not int or type(scope_version) is not int:
                raise authentication_error()
            return AccessTokenClaims(
                subject=cast(str, subject),
                session_id=cast(str, session_id),
                role=cast(str, role),
                token_version=token_version,
                scope_version=scope_version,
                token_id=cast(str, token_id),
            )
        except jwt.ExpiredSignatureError as error:
            raise authentication_error(
                code="TOKEN_EXPIRED",
                detail="The access token has expired.",
            ) from error
        except ApplicationError:
            raise
        except jwt.PyJWTError as error:
            raise authentication_error() from error


class OpaqueTokenManager:
    """Generate high-entropy opaque credentials and one-way HMAC digests."""

    def __init__(self, pepper: bytes) -> None:
        if len(pepper) < 32:
            raise ValueError("Opaque-token pepper must contain at least 32 bytes.")
        self._pepper = pepper

    @staticmethod
    def generate(prefix: str) -> str:
        """Create a URL-safe token with a non-secret type prefix."""

        return f"{prefix}_{secrets.token_urlsafe(48)}"

    def digest(self, token: str) -> str:
        """Return a keyed digest suitable for persistence and equality lookup."""

        return hmac.new(self._pepper, token.encode(), hashlib.sha256).hexdigest()

    def fingerprint(self, value: str) -> str:
        """Create a non-reversible bounded identifier for rate-limit and client context."""

        return self.digest(value)[:32]


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(UTC)
