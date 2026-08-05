"""Minimal process liveness required by the canonical API contract."""

from fastapi import APIRouter, status

from app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/live",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check API process liveness",
    responses={
        200: {
            "description": "The API process is alive.",
            "content": {"application/json": {"example": {"status": "alive"}}},
        }
    },
)
async def get_liveness() -> HealthResponse:
    """Return only process liveness; no dependency or topology details are exposed."""

    return HealthResponse()
