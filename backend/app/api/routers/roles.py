"""Authenticated safe RBAC catalog."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_authentication_controller, get_current_principal
from app.controllers.authentication import AuthenticationController
from app.models.auth import AuthenticatedPrincipal
from app.schemas.auth import RoleListResponse
from app.schemas.problem import ProblemDetail

router = APIRouter(tags=["Roles"])


@router.get(
    "/roles",
    response_model=RoleListResponse,
    summary="List safe role definitions",
    responses={401: {"model": ProblemDetail, "description": "Session is not valid."}},
)
async def list_roles(
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
    controller: Annotated[AuthenticationController, Depends(get_authentication_controller)],
) -> RoleListResponse:
    """Return the approved role catalog to any authenticated user."""

    del principal
    return RoleListResponse(items=controller.role_definitions())
