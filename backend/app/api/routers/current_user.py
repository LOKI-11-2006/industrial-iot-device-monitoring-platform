"""Authenticated current-user identity and session endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_authentication_controller, get_current_principal
from app.controllers.authentication import AuthenticationController
from app.models.auth import AuthenticatedPrincipal
from app.schemas.auth import (
    CurrentUserResponse,
    LogoutResponse,
    PageMetadata,
    SessionListResponse,
    SessionResponse,
)
from app.schemas.problem import ProblemDetail

router = APIRouter(prefix="/me", tags=["Current user"])


@router.get(
    "",
    response_model=CurrentUserResponse,
    summary="Get the current identity and effective access",
    responses={401: {"model": ProblemDetail, "description": "Session is not valid."}},
)
async def get_current_user(
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
    controller: Annotated[AuthenticationController, Depends(get_authentication_controller)],
) -> CurrentUserResponse:
    """Return live role, permission, and factory scope rather than JWT-cached values."""

    return await controller.current_principal_user(principal)


@router.get(
    "/sessions",
    response_model=SessionListResponse,
    summary="List current-user sessions",
    responses={401: {"model": ProblemDetail, "description": "Session is not valid."}},
)
async def list_sessions(
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
    controller: Annotated[AuthenticationController, Depends(get_authentication_controller)],
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
) -> SessionListResponse:
    """Return bounded active and recently revoked session metadata."""

    sessions = await controller.service.list_sessions(principal)
    items = [
        SessionResponse(
            id=session.id,
            current=session.id == principal.session_id,
            created_at=session.created_at,
            last_seen_at=session.last_seen_at,
            expires_at=session.expires_at,
            revoked_at=session.revoked_at,
            user_agent=session.user_agent,
        )
        for session in sessions[:limit]
    ]
    return SessionListResponse(items=items, page=PageMetadata(limit=limit))


@router.delete(
    "/sessions/{session_id}",
    response_model=LogoutResponse,
    summary="Revoke one owned session",
    responses={
        401: {"model": ProblemDetail, "description": "Session is not valid."},
        404: {"model": ProblemDetail, "description": "Owned session was not found."},
    },
)
async def revoke_session(
    session_id: str,
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
    controller: Annotated[AuthenticationController, Depends(get_authentication_controller)],
) -> LogoutResponse:
    """Revoke an owned session while concealing foreign session identifiers."""

    revoked = await controller.service.revoke_owned_session(principal, session_id)
    return LogoutResponse(revoked=revoked)
