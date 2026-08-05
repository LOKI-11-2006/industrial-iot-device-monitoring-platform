"""Top-level versioned API router."""

from fastapi import APIRouter

from app.api.routers.authentication import router as authentication_router
from app.api.routers.current_user import router as current_user_router
from app.api.routers.health import router as health_router
from app.api.routers.roles import router as roles_router

api_router = APIRouter()
api_router.include_router(authentication_router)
api_router.include_router(current_user_router)
api_router.include_router(health_router)
api_router.include_router(roles_router)
