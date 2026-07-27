from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    app_name: str
    app_env: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    from sentinelcore.core.config.settings import get_settings

    settings = get_settings()
    return HealthResponse(status="ok", app_name=settings.app_name, app_env=settings.app_env)
