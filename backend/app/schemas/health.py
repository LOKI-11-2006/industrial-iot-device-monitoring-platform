"""Health endpoint response contracts."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    """Minimal public process-liveness response."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["alive"] = "alive"
