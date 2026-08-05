"""FastAPI application factory and infrastructure composition boundary."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config.settings import Settings, get_settings
from app.core.exception_handlers import install_exception_handlers
from app.logs.configure import configure_logging
from app.middleware.cors import CorsPreflightGuardMiddleware
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.trusted_host import TrustedHostProblemMiddleware


def create_app(settings: Settings | None = None) -> FastAPI:
    """Compose one stateless API process from validated infrastructure adapters."""

    runtime_settings = settings or get_settings()
    configure_logging(runtime_settings)

    docs_url = "/docs" if runtime_settings.docs_enabled else None
    redoc_url = "/redoc" if runtime_settings.docs_enabled else None
    openapi_url = "/openapi.json" if runtime_settings.docs_enabled else None
    app = FastAPI(
        title=runtime_settings.app_name,
        summary="Secure industrial IoT device management and predictive monitoring API.",
        description=(
            "Versioned control-plane API for human identity, industrial asset governance, "
            "operational monitoring, analytics, alerts, reports, and auditable administration."
        ),
        version=runtime_settings.version,
        debug=runtime_settings.debug,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        contact={"name": "ForgeSight Platform Operations"},
        license_info={"name": "Proprietary"},
    )
    app.state.settings = runtime_settings

    install_exception_handlers(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=runtime_settings.cors_allowed_origins,
        allow_credentials=runtime_settings.cors_allow_credentials,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Idempotency-Key",
            "If-Match",
            "X-Correlation-ID",
        ],
        expose_headers=["ETag", "X-Correlation-ID"],
        max_age=600,
    )
    app.add_middleware(
        CorsPreflightGuardMiddleware,
        allowed_origins=runtime_settings.cors_allowed_origins,
    )
    app.add_middleware(
        TrustedHostProblemMiddleware,
        allowed_hosts=runtime_settings.allowed_hosts,
    )
    app.add_middleware(SecurityHeadersMiddleware, enable_hsts=runtime_settings.is_production)
    app.add_middleware(RequestContextMiddleware)
    app.include_router(api_router, prefix=runtime_settings.api_v1_prefix)
    return app
