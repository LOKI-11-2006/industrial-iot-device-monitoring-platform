"""FastAPI authentication and authorization dependencies."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.controllers.authentication import AuthenticationController
from app.core.errors import authentication_error
from app.models.auth import AuthenticatedPrincipal, ClientContext
from app.security.permissions import Permission

bearer_scheme = HTTPBearer(
    bearerFormat="JWT",
    scheme_name="BearerAuth",
    description="Short-lived ForgeSight access JWT.",
    auto_error=False,
)


def get_authentication_controller(request: Request) -> AuthenticationController:
    """Resolve the process-composed authentication module."""

    controller = getattr(request.app.state, "authentication", None)
    if not isinstance(controller, AuthenticationController):
        raise RuntimeError("Authentication module was not composed.")
    return controller


def get_client_context(request: Request) -> ClientContext:
    """Capture bounded direct-client context without trusting forwarding headers."""

    client_ip = request.client.host if request.client is not None else "unavailable"
    return ClientContext(
        ip_address=client_ip,
        user_agent=request.headers.get("user-agent"),
    )


async def get_current_principal(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(bearer_scheme)],
    controller: Annotated[AuthenticationController, Depends(get_authentication_controller)],
) -> AuthenticatedPrincipal:
    """Validate a bearer JWT and its live user/session state."""

    if credentials is None or credentials.scheme.casefold() != "bearer":
        raise authentication_error()
    return await controller.service.authenticate_access_token(credentials.credentials)


PrincipalDependency = Callable[..., Awaitable[AuthenticatedPrincipal]]


def require_permission(permission: Permission) -> PrincipalDependency:
    """Build a reusable default-deny permission dependency."""

    async def permission_dependency(
        principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
        controller: Annotated[AuthenticationController, Depends(get_authentication_controller)],
    ) -> AuthenticatedPrincipal:
        controller.authorization.authorize(principal, permission)
        return principal

    return permission_dependency


def require_factory_permission(permission: Permission) -> PrincipalDependency:
    """Build a permission dependency that also enforces a trusted factory path scope."""

    async def factory_permission_dependency(
        factory_id: str,
        principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
        controller: Annotated[AuthenticationController, Depends(get_authentication_controller)],
    ) -> AuthenticatedPrincipal:
        controller.authorization.authorize(principal, permission, factory_id=factory_id)
        return principal

    return factory_permission_dependency
