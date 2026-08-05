"""Validate startup configuration and print only non-sensitive runtime identity."""

from __future__ import annotations

import json

from app.config.settings import get_settings


def main() -> None:
    """Fail fast on invalid configuration without printing secret references or values."""

    settings = get_settings()
    print(
        json.dumps(
            {
                "status": "valid",
                "service": settings.service_name,
                "environment": settings.environment.value,
                "region": settings.aws_region,
                "resourcePrefix": settings.aws_resource_prefix,
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
