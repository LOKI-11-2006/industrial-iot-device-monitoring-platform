"""Adaptive password hashing tests."""

import pytest

from app.core.errors import ApplicationError
from app.security.passwords import PasswordManager


def test_password_hash_is_adaptive_and_verifiable() -> None:
    manager = PasswordManager()
    password_hash = manager.hash_password("A sufficiently long password")

    valid, replacement = manager.verify_password("A sufficiently long password", password_hash)
    invalid, _ = manager.verify_password("An incorrect long password", password_hash)

    assert password_hash.startswith("$argon2id$")
    assert valid is True
    assert replacement is None
    assert invalid is False


@pytest.mark.parametrize("password", ["too short", "            "])
def test_new_password_policy_rejects_unsafe_values(password: str) -> None:
    with pytest.raises(ApplicationError, match="new password") as caught:
        PasswordManager.validate_new_password(password)

    assert caught.value.code == "PASSWORD_POLICY_FAILED"


def test_unknown_user_verification_performs_dummy_hash_work() -> None:
    PasswordManager().verify_unknown_user("A candidate password")
