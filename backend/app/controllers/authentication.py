"""Transport-to-authentication use-case coordination."""

from __future__ import annotations

from dataclasses import dataclass

from app.models.auth import AuthenticatedPrincipal, UserAccount, UserRole
from app.schemas.auth import CurrentUserResponse, RoleDefinitionResponse
from app.security.permissions import AuthorizationPolicy, permissions_for_role
from app.services.authentication import AuthenticationService

_ROLE_LABELS = {
    UserRole.SUPER_ADMINISTRATOR: "Super Administrator",
    UserRole.FACTORY_ADMINISTRATOR: "Factory Administrator",
    UserRole.FACTORY_MANAGER: "Factory Manager",
    UserRole.MAINTENANCE_ENGINEER: "Maintenance Engineer",
    UserRole.OPERATOR: "Operator",
    UserRole.VIEWER: "Viewer",
}


@dataclass(frozen=True, slots=True)
class AuthenticationController:
    """Authentication module entry point composed once per application process."""

    service: AuthenticationService
    authorization: AuthorizationPolicy

    @staticmethod
    def current_user_response(user: UserAccount) -> CurrentUserResponse:
        """Map a live identity projection to its safe API representation."""

        return CurrentUserResponse(
            id=user.id,
            display_name=user.display_name,
            email=user.email,
            role=user.role,
            factory_ids=list(user.factory_ids),
            permissions=sorted(permission.value for permission in permissions_for_role(user.role)),
        )

    @staticmethod
    def role_definitions() -> list[RoleDefinitionResponse]:
        """Return stable role labels and their base permission vocabulary."""

        return [
            RoleDefinitionResponse(
                id=role,
                label=_ROLE_LABELS[role],
                permissions=sorted(permission.value for permission in permissions_for_role(role)),
            )
            for role in UserRole
        ]

    async def current_principal_user(
        self, principal: AuthenticatedPrincipal
    ) -> CurrentUserResponse:
        """Load and map the current live user."""

        user = await self.service.get_user(principal)
        return self.current_user_response(user)
