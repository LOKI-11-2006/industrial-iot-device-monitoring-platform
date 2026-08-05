"""Public and authenticated human-session endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Response, status

from app.api.dependencies import (
    get_authentication_controller,
    get_client_context,
    get_current_principal,
)
from app.controllers.authentication import AuthenticationController
from app.models.auth import AuthenticatedPrincipal, ClientContext
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutAllRequest,
    LogoutAllResponse,
    LogoutResponse,
    PasswordResetAccepted,
    PasswordResetCompleted,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshResponse,
)
from app.schemas.problem import ProblemDetail

router = APIRouter(prefix="/auth", tags=["Authentication"])

_AUTHENTICATION_PROBLEMS: dict[int | str, dict[str, Any]] = {
    400: {"model": ProblemDetail, "description": "Invalid reset token or password policy."},
    401: {"model": ProblemDetail, "description": "Invalid credentials, token, or session."},
    423: {"model": ProblemDetail, "description": "Temporary sign-in lockout."},
    429: {"model": ProblemDetail, "description": "Authentication rate limit exceeded."},
}


def _set_refresh_cookie(
    response: Response, request: Request, token: str, expires_at: datetime
) -> None:
    settings = request.app.state.settings
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=token,
        expires=expires_at,
        path=f"{settings.api_v1_prefix}/auth",
        secure=settings.refresh_cookie_secure,
        httponly=True,
        samesite=settings.refresh_cookie_same_site,
    )


def _clear_refresh_cookie(response: Response, request: Request) -> None:
    settings = request.app.state.settings
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        path=f"{settings.api_v1_prefix}/auth",
        secure=settings.refresh_cookie_secure,
        httponly=True,
        samesite=settings.refresh_cookie_same_site,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Create a human session",
    responses=_AUTHENTICATION_PROBLEMS,
)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    client: Annotated[ClientContext, Depends(get_client_context)],
    controller: Annotated[AuthenticationController, Depends(get_authentication_controller)],
) -> LoginResponse:
    """Verify credentials and issue short access plus rotating refresh credentials."""

    result = await controller.service.login(
        str(payload.email),
        payload.password.get_secret_value(),
        payload.remember_device,
        client,
    )
    _set_refresh_cookie(
        response,
        request,
        result.tokens.refresh_token,
        result.tokens.refresh_expires_at,
    )
    user = await controller.current_principal_user(result.principal)
    return LoginResponse(
        access_token=result.tokens.access_token,
        expires_in=result.tokens.access_expires_in,
        user=user,
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    summary="Rotate a refresh credential",
    responses={401: _AUTHENTICATION_PROBLEMS[401]},
)
async def refresh(
    request: Request,
    response: Response,
    controller: Annotated[AuthenticationController, Depends(get_authentication_controller)],
) -> RefreshResponse:
    """Rotate the HTTP-only refresh cookie and issue a new short access JWT."""

    cookie_name = request.app.state.settings.refresh_cookie_name
    tokens = await controller.service.refresh(request.cookies.get(cookie_name))
    _set_refresh_cookie(response, request, tokens.refresh_token, tokens.refresh_expires_at)
    return RefreshResponse(
        access_token=tokens.access_token,
        expires_in=tokens.access_expires_in,
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Revoke the current session",
    responses={401: _AUTHENTICATION_PROBLEMS[401]},
)
async def logout(
    request: Request,
    response: Response,
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
    controller: Annotated[AuthenticationController, Depends(get_authentication_controller)],
) -> LogoutResponse:
    """Revoke the current session family and remove its browser credential."""

    await controller.service.logout(principal)
    _clear_refresh_cookie(response, request)
    return LogoutResponse(revoked=True)


@router.post(
    "/logout-all",
    response_model=LogoutAllResponse,
    summary="Revoke all current-user sessions",
    responses={401: _AUTHENTICATION_PROBLEMS[401]},
)
async def logout_all(
    payload: LogoutAllRequest,
    request: Request,
    response: Response,
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
    controller: Annotated[AuthenticationController, Depends(get_authentication_controller)],
) -> LogoutAllResponse:
    """Revoke every session owned by the authenticated user."""

    count = await controller.service.logout_all(principal, payload.reason)
    _clear_refresh_cookie(response, request)
    return LogoutAllResponse(revoked_sessions=count)


@router.post(
    "/password-reset/request",
    response_model=PasswordResetAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Request a non-enumerating password reset",
    responses={429: _AUTHENTICATION_PROBLEMS[429]},
)
async def request_password_reset(
    payload: PasswordResetRequest,
    client: Annotated[ClientContext, Depends(get_client_context)],
    controller: Annotated[AuthenticationController, Depends(get_authentication_controller)],
) -> PasswordResetAccepted:
    """Always return the same accepted response for existing and unknown identities."""

    await controller.service.request_password_reset(str(payload.email), client)
    return PasswordResetAccepted()


@router.post(
    "/password-reset/confirm",
    response_model=PasswordResetCompleted,
    summary="Complete a single-use password reset",
    responses={400: _AUTHENTICATION_PROBLEMS[400]},
)
async def confirm_password_reset(
    payload: PasswordResetConfirm,
    controller: Annotated[AuthenticationController, Depends(get_authentication_controller)],
) -> PasswordResetCompleted:
    """Replace the password and revoke all sessions after consuming a valid reset token."""

    await controller.service.confirm_password_reset(
        payload.token.get_secret_value(),
        payload.new_password.get_secret_value(),
    )
    return PasswordResetCompleted()
