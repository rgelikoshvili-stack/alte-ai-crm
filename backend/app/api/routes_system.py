from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.models import (
    Conversation,
    Customer,
    Department,
    KnowledgeSnippet,
    KnowledgeSource,
    Lead,
    Message,
    PipelineStage,
    Task,
)

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


@router.get("/diagnostics/local-demo")
async def local_demo_diagnostics(db: AsyncSession = Depends(get_db)) -> dict:
    settings = get_settings()
    counts = {
        "departments": await count_rows(db, Department),
        "customers": await count_rows(db, Customer),
        "leads": await count_rows(db, Lead),
        "conversations": await count_rows(db, Conversation),
        "messages": await count_rows(db, Message),
        "tasks": await count_rows(db, Task),
        "knowledge_sources": await count_rows(db, KnowledgeSource),
        "knowledge_snippets": await count_rows(db, KnowledgeSnippet),
    }
    pipeline_stages = await count_rows(db, PipelineStage)
    warnings: list[str] = []
    if counts["knowledge_snippets"] == 0:
        warnings.append("no knowledge snippets")
    if pipeline_stages == 0:
        warnings.append("no pipeline stages")
    if settings.AUTH_REQUIRED:
        warnings.append("auth required true")
    if settings.AI_PROVIDER == "claude" and is_placeholder_key(settings.ANTHROPIC_API_KEY):
        warnings.append("AI_PROVIDER=claude but ANTHROPIC_API_KEY placeholder/missing")
    return {
        "status": "ok",
        "service": "alte-ai-crm",
        "environment": settings.ENVIRONMENT,
        "ai_provider": settings.AI_PROVIDER,
        "auth_required": settings.AUTH_REQUIRED,
        "database_type": database_type(settings.DATABASE_URL),
        "counts": counts,
        "warnings": warnings,
    }


async def count_rows(db: AsyncSession, model) -> int:
    return int(await db.scalar(select(func.count()).select_from(model)) or 0)


def database_type(database_url: str) -> str:
    lowered = database_url.lower()
    if lowered.startswith("sqlite"):
        return "sqlite"
    if lowered.startswith("postgresql"):
        return "postgresql"
    return "other"


def is_placeholder_key(value: str | None) -> bool:
    if not value:
        return True
    normalized = value.strip().lower()
    return normalized in {"your-anthropic-api-key", "local-placeholder", "test-anthropic-key", "change-me"}


@router.get("/diagnostics/ai")
async def ai_diagnostics() -> dict:
    settings = get_settings()
    provider = settings.AI_PROVIDER.lower().strip()
    has_key = bool(settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY.strip())
    placeholder = is_placeholder_key(settings.ANTHROPIC_API_KEY)
    warnings: list[str] = []
    if provider == "mock":
        warnings.append("mock mode active")
    if provider == "claude" and (not has_key or placeholder):
        warnings.append("AI_PROVIDER=claude but ANTHROPIC_API_KEY placeholder/missing")
    if provider not in {"mock", "claude"}:
        warnings.append("unknown AI_PROVIDER")
    return {
        "ai_provider": settings.AI_PROVIDER,
        "ai_model": settings.AI_MODEL,
        "confidence_threshold": settings.AI_CONFIDENCE_THRESHOLD,
        "has_anthropic_key": has_key,
        "anthropic_key_is_placeholder": placeholder,
        "mock_mode": provider == "mock",
        "claude_enabled": provider == "claude" and has_key and not placeholder,
        "warnings": warnings,
    }
