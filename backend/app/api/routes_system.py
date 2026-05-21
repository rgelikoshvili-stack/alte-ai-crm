from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": "alte-ai-crm",
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
    }


@router.get("/version")
async def version() -> dict[str, str]:
    settings = get_settings()
    return {
        "service": "alte-ai-crm",
        "version": settings.APP_VERSION,
    }
