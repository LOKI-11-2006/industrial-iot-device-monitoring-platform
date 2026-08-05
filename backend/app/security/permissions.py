"""Central default-deny RBAC and factory-scope policy."""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Final

from app.core.errors import factory_scope_denied, permission_denied
from app.models.auth import AuthenticatedPrincipal, UserRole


class Permission(StrEnum):
    """Stable permission vocabulary from the approved authorization matrix."""

    FACTORIES_READ = "factories:read"
    FACTORIES_CREATE = "factories:create"
    FACTORIES_UPDATE = "factories:update"
    FACTORIES_ARCHIVE = "factories:archive"
    DEVICES_READ = "devices:read"
    DEVICES_CREATE = "devices:create"
    DEVICES_UPDATE = "devices:update"
    DEVICES_TRANSFER = "devices:transfer"
    DEVICES_QUARANTINE = "devices:quarantine"
    DEVICES_CONFIGURE = "devices:configure"
    DEVICES_PROVISION = "devices:provision"
    CERTIFICATES_ROTATE = "certificates:rotate"
    CERTIFICATES_REVOKE = "certificates:revoke"
    TELEMETRY_READ = "telemetry:read"
    ANALYTICS_READ = "analytics:read"
    ALERTS_READ = "alerts:read"
    ALERTS_ACKNOWLEDGE = "alerts:acknowledge"
    ALERTS_ASSIGN = "alerts:assign"
    ALERTS_RESOLVE = "alerts:resolve"
    ALERT_RULES_READ = "alert_rules:read"
    ALERT_RULES_MANAGE = "alert_rules:manage"
    REPORTS_READ = "reports:read"
    REPORTS_CREATE = "reports:create"
    REPORTS_SCHEDULE = "reports:schedule"
    USERS_READ = "users:read"
    USERS_CREATE = "users:create"
    USERS_UPDATE = "users:update"
    USERS_DISABLE = "users:disable"
    USERS_ASSIGN_SCOPE = "users:assign_scope"
    AUDIT_READ = "audit:read"
    SECURITY_READ = "security:read"
    SECURITY_MANAGE = "security:manage"
    SETTINGS_READ = "settings:read"
    SETTINGS_MANAGE_FACTORY = "settings:manage_factory"
    SETTINGS_MANAGE_PLATFORM = "settings:manage_platform"
    PLATFORM_HEALTH_READ = "platform_health:read"


_READ_BASE = frozenset(
    {
        Permission.FACTORIES_READ,
        Permission.DEVICES_READ,
        Permission.TELEMETRY_READ,
        Permission.ANALYTICS_READ,
        Permission.ALERTS_READ,
        Permission.REPORTS_READ,
    }
)

ROLE_PERMISSIONS: Final = MappingProxyType(
    {
        UserRole.SUPER_ADMINISTRATOR: frozenset(Permission),
        UserRole.FACTORY_ADMINISTRATOR: frozenset(
            {
                *_READ_BASE,
                Permission.FACTORIES_CREATE,
                Permission.FACTORIES_UPDATE,
                Permission.FACTORIES_ARCHIVE,
                Permission.DEVICES_CREATE,
                Permission.DEVICES_UPDATE,
                Permission.DEVICES_TRANSFER,
                Permission.DEVICES_QUARANTINE,
                Permission.DEVICES_CONFIGURE,
                Permission.DEVICES_PROVISION,
                Permission.CERTIFICATES_ROTATE,
                Permission.CERTIFICATES_REVOKE,
                Permission.ALERTS_ACKNOWLEDGE,
                Permission.ALERTS_ASSIGN,
                Permission.ALERTS_RESOLVE,
                Permission.ALERT_RULES_READ,
                Permission.ALERT_RULES_MANAGE,
                Permission.REPORTS_CREATE,
                Permission.REPORTS_SCHEDULE,
                Permission.USERS_READ,
                Permission.USERS_CREATE,
                Permission.USERS_UPDATE,
                Permission.USERS_DISABLE,
                Permission.USERS_ASSIGN_SCOPE,
                Permission.AUDIT_READ,
                Permission.SECURITY_READ,
                Permission.SETTINGS_READ,
                Permission.SETTINGS_MANAGE_FACTORY,
                Permission.PLATFORM_HEALTH_READ,
            }
        ),
        UserRole.FACTORY_MANAGER: frozenset(
            {
                *_READ_BASE,
                Permission.DEVICES_QUARANTINE,
                Permission.DEVICES_CONFIGURE,
                Permission.ALERTS_ACKNOWLEDGE,
                Permission.ALERTS_ASSIGN,
                Permission.ALERTS_RESOLVE,
                Permission.ALERT_RULES_READ,
                Permission.ALERT_RULES_MANAGE,
                Permission.REPORTS_CREATE,
                Permission.REPORTS_SCHEDULE,
                Permission.AUDIT_READ,
                Permission.SECURITY_READ,
                Permission.SETTINGS_READ,
                Permission.SETTINGS_MANAGE_FACTORY,
                Permission.PLATFORM_HEALTH_READ,
            }
        ),
        UserRole.MAINTENANCE_ENGINEER: frozenset(
            {
                *_READ_BASE,
                Permission.DEVICES_QUARANTINE,
                Permission.DEVICES_CONFIGURE,
                Permission.ALERTS_ACKNOWLEDGE,
                Permission.ALERTS_ASSIGN,
                Permission.ALERTS_RESOLVE,
                Permission.ALERT_RULES_READ,
                Permission.REPORTS_CREATE,
                Permission.PLATFORM_HEALTH_READ,
            }
        ),
        UserRole.OPERATOR: frozenset(
            {
                *_READ_BASE,
                Permission.ALERTS_ACKNOWLEDGE,
                Permission.REPORTS_CREATE,
                Permission.AUDIT_READ,
            }
        ),
        UserRole.VIEWER: frozenset({*_READ_BASE, Permission.AUDIT_READ}),
    }
)


def permissions_for_role(role: UserRole) -> frozenset[Permission]:
    """Return the immutable effective base permissions for a role."""

    return ROLE_PERMISSIONS.get(role, frozenset())


class AuthorizationPolicy:
    """Authoritative RBAC plus factory-scope evaluator."""

    def authorize(
        self,
        principal: AuthenticatedPrincipal,
        permission: Permission,
        *,
        factory_id: str | None = None,
    ) -> None:
        """Raise a safe denial unless permission and optional scope both pass."""

        if permission not in permissions_for_role(principal.role):
            raise permission_denied()

        if (
            factory_id is not None
            and principal.role is not UserRole.SUPER_ADMINISTRATOR
            and factory_id not in principal.factory_ids
        ):
            raise factory_scope_denied()
