from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Lead, LeadStageHistory
from app.schemas.crm import LeadCreate, LeadStageChange, LeadUpdate
from app.services.audit_service import audit_event


async def create_lead(db: AsyncSession, payload: LeadCreate) -> Lead:
    lead = Lead(**payload.model_dump())
    db.add(lead)
    await db.flush()
    await audit_event(
        db,
        action="lead_created",
        entity_type="lead",
        entity_id=lead.id,
        metadata_json={
            "source_domain": lead.source_domain,
            "is_international_priority": lead.is_international_priority,
            "medical_track": lead.medical_track,
        },
    )
    await db.commit()
    await db.refresh(lead)
    return lead


async def update_lead(db: AsyncSession, lead: Lead, payload: LeadUpdate) -> Lead:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    await db.flush()
    await audit_event(db, action="lead_updated", entity_type="lead", entity_id=lead.id)
    await db.commit()
    await db.refresh(lead)
    return lead


async def change_lead_stage(db: AsyncSession, lead: Lead, payload: LeadStageChange) -> Lead:
    previous_stage_id = lead.stage_id
    lead.stage_id = payload.stage_id
    history = LeadStageHistory(
        lead_id=lead.id,
        from_stage_id=previous_stage_id,
        to_stage_id=payload.stage_id,
        changed_by=payload.changed_by,
    )
    db.add(history)
    await db.flush()
    await audit_event(
        db,
        action="stage_changed",
        entity_type="lead",
        entity_id=lead.id,
        actor_id=payload.changed_by,
        metadata_json={"from_stage_id": previous_stage_id, "to_stage_id": payload.stage_id},
    )
    await db.commit()
    await db.refresh(lead)
    return lead
