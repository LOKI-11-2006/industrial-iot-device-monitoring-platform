"""Validated HTTP request and response contracts."""

from app.schemas.health import HealthResponse
from app.schemas.problem import ProblemDetail

__all__ = ["HealthResponse", "ProblemDetail"]
