"""Run the API locally with safe development defaults."""

from __future__ import annotations

import uvicorn

from app.config.settings import DeploymentEnvironment, get_settings


def main() -> None:
    """Start Uvicorn and restrict auto-reload to non-production environments."""

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.environment
        in {DeploymentEnvironment.LOCAL, DeploymentEnvironment.DEVELOPMENT},
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
