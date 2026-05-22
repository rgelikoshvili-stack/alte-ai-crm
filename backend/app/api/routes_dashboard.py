from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.operator import DashboardOverview
from app.services.operator_service import build_dashboard_overview

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverview)
async def dashboard_overview(db: AsyncSession = Depends(get_db)):
    return await build_dashboard_overview(db)
