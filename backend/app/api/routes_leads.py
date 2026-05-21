from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_or_404
from app.core.database import get_db
from app.models import Lead
from app.schemas.crm import LeadCreate, LeadRead, LeadStageChange, LeadUpdate
from app.services.lead_service import change_lead_stage, create_lead, update_lead

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadRead)
async def create_lead_route(payload: LeadCreate, db: AsyncSession = Depends(get_db)):
    return await create_lead(db, payload)


@router.get("", response_model=list[LeadRead])
async def list_leads(db: AsyncSession = Depends(get_db)):
    return (await db.scalars(select(Lead).order_by(Lead.created_at.desc()))).all()


@router.get("/{lead_id}", response_model=LeadRead)
async def get_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    return await get_or_404(db, Lead, lead_id, "Lead")


@router.patch("/{lead_id}", response_model=LeadRead)
async def update_lead_route(lead_id: str, payload: LeadUpdate, db: AsyncSession = Depends(get_db)):
    lead = await get_or_404(db, Lead, lead_id, "Lead")
    return await update_lead(db, lead, payload)


@router.patch("/{lead_id}/stage", response_model=LeadRead)
async def change_lead_stage_route(lead_id: str, payload: LeadStageChange, db: AsyncSession = Depends(get_db)):
    lead = await get_or_404(db, Lead, lead_id, "Lead")
    return await change_lead_stage(db, lead, payload)
