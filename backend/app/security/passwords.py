"""Adaptive password hashing and password policy enforcement."""

from __future__ import annotations

import secrets

from pwdlib import PasswordHash

from app.core.errors import ApplicationError


class PasswordManager:
    """Argon2id password boundary with timing-safe unknown-user verification."""

    def __init__(self) -> None:
        self._password_hash = PasswordHash.recommended()
        self._dummy_hash = self._password_hash.hash(secrets.token_urlsafe(32))

    def hash_password(self, password: str) -> str:
        """Hash a policy-compliant password using the current adaptive parameters."""

        self.validate_new_password(password)
        return self._password_hash.hash(password)

    def verify_password(self, password: str, password_hash: str) -> tuple[bool, str | None]:
        """Verify a password and return an upgraded hash when parameters changed."""

        return self._password_hash.verify_and_update(password, password_hash)

    def verify_unknown_user(self, password: str) -> None:
        """Perform equivalent adaptive work for an unknown identity."""

        self._password_hash.verify(password, self._dummy_hash)

    @staticmethod
    def validate_new_password(password: str) -> None:
        """Enforce a bounded, composition-independent password policy."""

        if len(password) < 12 or len(password) > 128:
            raise ApplicationError(
                status_code=400,
                code="PASSWORD_POLICY_FAILED",
                title="Password policy not met",
                detail="The new password must contain between 12 and 128 characters.",
            )
        if password.isspace():
            raise ApplicationError(
                status_code=400,
                code="PASSWORD_POLICY_FAILED",
                title="Password policy not met",
                detail="The new password cannot consist only of whitespace.",
            )
