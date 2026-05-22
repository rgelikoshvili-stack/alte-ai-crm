from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_or_404
from app.core.database import get_db
from app.models import AuditLog, Conversation, Customer, Department, Lead, LeadStageHistory, PipelineStage, Task, User
from app.schemas.crm import LeadCreate, LeadRead, LeadStageChange, LeadUpdate
from app.schemas.operator import LeadDetail, LeadListItem
from app.services.lead_service import change_lead_stage, create_lead, update_lead
from app.services.operator_service import build_lead_items

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadRead)
async def create_lead_route(payload: LeadCreate, db: AsyncSession = Depends(get_db)):
    return await create_lead(db, payload)


@router.get("", response_model=list[LeadListItem])
async def list_leads(
    limit: int = 20,
    offset: int = 0,
    status: str | None = None,
    priority: str | None = None,
    department_id: str | None = None,
    stage_id: str | None = None,
    source_channel: str | None = None,
    source_domain: str | None = None,
    is_international_priority: bool | None = None,
    medical_track: bool | None = None,
    q: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await build_lead_items(
        db,
        limit=limit,
        offset=offset,
        status=status,
        priority=priority,
        department_id=department_id,
        stage_id=stage_id,
        source_channel=source_channel,
        source_domain=source_domain,
        is_international_priority=is_international_priority,
        medical_track=medical_track,
        q=q,
    )


@router.get("/{lead_id}", response_model=LeadRead)
async def get_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    return await get_or_404(db, Lead, lead_id, "Lead")


@router.get("/{lead_id}/detail", response_model=LeadDetail)
async def get_lead_detail(lead_id: str, db: AsyncSession = Depends(get_db)):
    lead = await get_or_404(db, Lead, lead_id, "Lead")
    customer = await db.get(Customer, lead.customer_id)
    department = await db.get(Department, lead.department_id) if lead.department_id else None
    assigned_user = await db.get(User, lead.assigned_user_id) if lead.assigned_user_id else None
    stage = await db.get(PipelineStage, lead.stage_id) if lead.stage_id else None
    conversations = (await db.scalars(select(Conversation).where(Conversation.lead_id == lead_id))).all()
    tasks = (await db.scalars(select(Task).where(Task.lead_id == lead_id).order_by(Task.created_at.desc()))).all()
    stage_history = (
        await db.scalars(
            select(LeadStageHistory).where(LeadStageHistory.lead_id == lead_id).order_by(LeadStageHistory.changed_at.desc())
        )
    ).all()
    audit_events = (
        await db.scalars(
            select(AuditLog)
            .where(AuditLog.entity_type == "lead", AuditLog.entity_id == lead_id)
            .order_by(AuditLog.created_at.desc())
            .limit(20)
        )
    ).all()
    return LeadDetail(
        lead=lead,
        customer=customer,
        department=department,
        assigned_user={
            "id": assigned_user.id,
            "name": assigned_user.name,
            "email": assigned_user.email,
            "role": assigned_user.role,
        }
        if assigned_user
        else None,
        stage=stage,
        conversations=conversations,
        tasks=tasks,
        stage_history=stage_history,
        audit_events=audit_events,
    )


@router.patch("/{lead_id}", response_model=LeadRead)
async def update_lead_route(lead_id: str, payload: LeadUpdate, db: AsyncSession = Depends(get_db)):
    lead = await get_or_404(db, Lead, lead_id, "Lead")
    return await update_lead(db, lead, payload)


@router.patch("/{lead_id}/stage", response_model=LeadRead)
async def change_lead_stage_route(lead_id: str, payload: LeadStageChange, db: AsyncSession = Depends(get_db)):
    lead = await get_or_404(db, Lead, lead_id, "Lead")
    return await change_lead_stage(db, lead, payload)
