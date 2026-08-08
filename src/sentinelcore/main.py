from fastapi import FastAPI

from sentinelcore.api.errors.handlers import register_exception_handlers
from sentinelcore.api.health import router as health_router
from sentinelcore.core.config.settings import get_settings
from sentinelcore.modules.authentication.api.routers.auth_router import router as auth_router
from sentinelcore.modules.identity.api.routers.user_router import router as identity_router
from sentinelcore.modules.sessions.api.routers.session_router import router as sessions_router


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url=f"{settings.api_v1_prefix}/docs",
        redoc_url=f"{settings.api_v1_prefix}/redoc",
    )

    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(identity_router, prefix=settings.api_v1_prefix)
    app.include_router(auth_router, prefix=settings.api_v1_prefix)
    app.include_router(sessions_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
