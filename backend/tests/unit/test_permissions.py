"""Default-deny RBAC and trusted factory-scope policy tests."""

import pytest

from app.core.errors import ApplicationError
from app.models.auth import AuthenticatedPrincipal, UserRole
from app.security.permissions import (
    AuthorizationPolicy,
    Permission,
    permissions_for_role,
)


def _principal(role: UserRole) -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(
        user_id="usr_test",
        session_id="ses_test",
        email="test@example.com",
        display_name="Test User",
        role=role,
        factory_ids=("fac_allowed",),
    )


def test_super_administrator_has_every_base_permission() -> None:
    assert permissions_for_role(UserRole.SUPER_ADMINISTRATOR) == frozenset(Permission)


def test_viewer_is_read_only() -> None:
    permissions = permissions_for_role(UserRole.VIEWER)

    assert Permission.DEVICES_READ in permissions
    assert Permission.ALERTS_READ in permissions
    assert Permission.DEVICES_UPDATE not in permissions
    assert Permission.USERS_CREATE not in permissions


def test_policy_allows_permission_and_trusted_factory_scope() -> None:
    AuthorizationPolicy().authorize(
        _principal(UserRole.VIEWER),
        Permission.DEVICES_READ,
        factory_id="fac_allowed",
    )


def test_policy_denies_missing_permission_before_scope() -> None:
    with pytest.raises(ApplicationError) as caught:
        AuthorizationPolicy().authorize(
            _principal(UserRole.VIEWER),
            Permission.DEVICES_UPDATE,
            factory_id="fac_allowed",
        )

    assert caught.value.status_code == 403
    assert caught.value.code == "PERMISSION_DENIED"


def test_policy_denies_unassigned_factory() -> None:
    with pytest.raises(ApplicationError) as caught:
        AuthorizationPolicy().authorize(
            _principal(UserRole.OPERATOR),
            Permission.DEVICES_READ,
            factory_id="fac_other",
        )

    assert caught.value.code == "FACTORY_SCOPE_DENIED"


def test_super_administrator_is_platform_wide() -> None:
    AuthorizationPolicy().authorize(
        _principal(UserRole.SUPER_ADMINISTRATOR),
        Permission.SETTINGS_MANAGE_PLATFORM,
        factory_id="fac_any",
    )
