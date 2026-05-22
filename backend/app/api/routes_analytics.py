from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.analytics import AiAnalytics, AnalyticsOverview, KnowledgeAnalytics, LeadAnalytics, SlaAnalytics
from app.services.analytics_service import (
    build_ai_analytics,
    build_analytics_overview,
    build_knowledge_analytics,
    build_lead_analytics,
    build_sla_analytics,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
async def analytics_overview(db: AsyncSession = Depends(get_db)):
    return await build_analytics_overview(db)


@router.get("/leads", response_model=LeadAnalytics)
async def lead_analytics(db: AsyncSession = Depends(get_db)):
    return await build_lead_analytics(db)


@router.get("/sla", response_model=SlaAnalytics)
async def sla_analytics(db: AsyncSession = Depends(get_db)):
    return await build_sla_analytics(db)


@router.get("/knowledge", response_model=KnowledgeAnalytics)
async def knowledge_analytics(db: AsyncSession = Depends(get_db)):
    return await build_knowledge_analytics(db)


@router.get("/ai", response_model=AiAnalytics)
async def ai_analytics(db: AsyncSession = Depends(get_db)):
    return await build_ai_analytics(db)

