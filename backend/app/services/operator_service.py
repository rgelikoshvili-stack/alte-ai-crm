from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    AuditLog,
    Conversation,
    Customer,
    Department,
    Lead,
    LeadStageHistory,
    Message,
    Pipeline,
    PipelineStage,
    Task,
    User,
)
from app.schemas.operator import (
    CountItem,
    DashboardOverview,
    InboxListItem,
    LeadListItem,
    PipelineBoard,
    PipelineBoardLead,
    PipelineBoardStage,
    TaskListItem,
)


async def build_inbox_items(
    db: AsyncSession,
    *,
    limit: int = 20,
    offset: int = 0,
    channel: str | None = None,
    status: str | None = None,
    human_handover: bool | None = None,
    q: str | None = None,
) -> list[InboxListItem]:
    conversations = (await db.scalars(select(Conversation).order_by(Conversation.created_at.desc()))).all()
    items = [await build_inbox_item(db, conversation) for conversation in conversations]
    if channel:
        items = [item for item in items if item.channel == channel]
    if status:
        items = [item for item in items if item.status == status]
    if human_handover is not None:
        items = [item for item in items if item.human_handover is human_handover]
    if q:
        needle = q.lower()
        filtered = []
        for item in items:
            messages = (
                await db.scalars(
                    select(Message).where(Message.conversation_id == item.conversation_id).order_by(Message.created_at.desc())
                )
            ).all()
            haystack = " ".join(
                [
                    item.customer_name or "",
                    item.customer_email or "",
                    item.customer_phone or "",
                    item.last_message_text or "",
                    " ".join(message.text for message in messages),
                ]
            ).lower()
            if needle in haystack:
                filtered.append(item)
        items = filtered
    return items[offset : offset + limit]


async def build_inbox_item(db: AsyncSession, conversation: Conversation) -> InboxListItem:
    customer = await db.get(Customer, conversation.customer_id) if conversation.customer_id else None
    lead = await db.get(Lead, conversation.lead_id) if conversation.lead_id else None
    last_message = await db.scalar(
        select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at.desc()).limit(1)
    )
    return InboxListItem(
        conversation_id=conversation.id,
        channel=conversation.channel,
        status=conversation.status,
        language=conversation.language,
        human_handover=conversation.human_handover,
        ai_handled=conversation.ai_handled,
        customer_id=customer.id if customer else None,
        customer_name=customer_name(customer),
        customer_phone=customer.phone if customer else None,
        customer_email=customer.email if customer else None,
        lead_id=lead.id if lead else None,
        lead_status=lead.status if lead else None,
        lead_priority=lead.priority if lead else None,
        last_message_text=last_message.text if last_message else None,
        last_message_sender_type=last_message.sender_type if last_message else None,
        last_message_at=last_message.created_at if last_message else None,
        created_at=conversation.created_at,
    )


async def build_task_items(
    db: AsyncSession,
    *,
    limit: int = 20,
    offset: int = 0,
    status: str | None = None,
    priority: str | None = None,
    department_id: str | None = None,
    assigned_user_id: str | None = None,
    overdue: bool | None = None,
    lead_id: str | None = None,
    customer_id: str | None = None,
) -> list[TaskListItem]:
    query = select(Task).order_by(Task.created_at.desc())
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    if department_id:
        query = query.where(Task.department_id == department_id)
    if assigned_user_id:
        query = query.where(Task.assigned_user_id == assigned_user_id)
    if lead_id:
        query = query.where(Task.lead_id == lead_id)
    if customer_id:
        query = query.where(Task.customer_id == customer_id)
    if overdue is True:
        query = query.where(Task.due_date < datetime.now(UTC), Task.status != "completed")
    elif overdue is False:
        query = query.where(or_(Task.due_date.is_(None), Task.due_date >= datetime.now(UTC), Task.status == "completed"))
    tasks = (await db.scalars(query.offset(offset).limit(limit))).all()
    return [await build_task_item(db, task) for task in tasks]


async def build_task_item(db: AsyncSession, task: Task) -> TaskListItem:
    customer = await db.get(Customer, task.customer_id) if task.customer_id else None
    return TaskListItem(
        task_id=task.id,
        title=task.title,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        completed_at=task.completed_at,
        lead_id=task.lead_id,
        customer_id=task.customer_id,
        customer_name=customer_name(customer),
        department_id=task.department_id,
        assigned_user_id=task.assigned_user_id,
        created_at=task.created_at,
    )


async def build_lead_items(
    db: AsyncSession,
    *,
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
) -> list[LeadListItem]:
    query = select(Lead).order_by(Lead.created_at.desc())
    if status:
        query = query.where(Lead.status == status)
    if priority:
        query = query.where(Lead.priority == priority)
    if department_id:
        query = query.where(Lead.department_id == department_id)
    if stage_id:
        query = query.where(Lead.stage_id == stage_id)
    if source_channel:
        query = query.where(Lead.source_channel == source_channel)
    if source_domain:
        query = query.where(Lead.source_domain == source_domain)
    if is_international_priority is not None:
        query = query.where(Lead.is_international_priority == is_international_priority)
    if medical_track is not None:
        query = query.where(Lead.medical_track == medical_track)
    leads = (await db.scalars(query)).all()
    items = [await build_lead_item(db, lead) for lead in leads]
    if q:
        needle = q.lower()
        items = [
            item
            for item in items
            if needle
            in " ".join(
                [
                    item.customer_name or "",
                    item.customer_email or "",
                    item.customer_phone or "",
                    item.program or "",
                    item.interest_area or "",
                ]
            ).lower()
        ]
    return items[offset : offset + limit]


async def build_lead_item(db: AsyncSession, lead: Lead) -> LeadListItem:
    customer = await db.get(Customer, lead.customer_id)
    return LeadListItem(
        lead_id=lead.id,
        customer_id=lead.customer_id,
        customer_name=customer_name(customer),
        customer_phone=customer.phone if customer else None,
        customer_email=customer.email if customer else None,
        interest_area=lead.interest_area,
        program=lead.program,
        status=lead.status,
        priority=lead.priority,
        source_channel=lead.source_channel,
        source_domain=lead.source_domain,
        is_international_priority=lead.is_international_priority,
        medical_track=lead.medical_track,
        department_id=lead.department_id,
        stage_id=lead.stage_id,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
    )


async def build_dashboard_overview(db: AsyncSession) -> DashboardOverview:
    return DashboardOverview(
        total_customers=await count_rows(db, Customer),
        total_leads=await count_rows(db, Lead),
        open_leads=await count_where(db, Lead, Lead.status.in_(["new", "open", "in_progress"])),
        won_leads=await count_where(db, Lead, Lead.status == "won"),
        lost_leads=await count_where(db, Lead, Lead.status == "lost"),
        total_conversations=await count_rows(db, Conversation),
        human_handover_count=await count_where(db, Conversation, Conversation.human_handover.is_(True)),
        open_tasks=await count_where(db, Task, Task.status.in_(["open", "in_progress"])),
        overdue_tasks=await count_where(db, Task, Task.due_date < datetime.now(UTC), Task.status != "completed"),
        leads_by_stage=await count_group(db, Lead.stage_id),
        leads_by_channel=await count_group(db, Lead.source_channel),
        leads_by_priority=await count_group(db, Lead.priority),
        latest_conversations=await build_inbox_items(db, limit=5),
        latest_tasks=await build_task_items(db, limit=5),
    )


async def build_pipeline_board(db: AsyncSession, pipeline_id: str, leads_per_stage: int = 20) -> PipelineBoard | None:
    pipeline = await db.get(Pipeline, pipeline_id)
    if not pipeline:
        return None
    stages = (
        await db.scalars(select(PipelineStage).where(PipelineStage.pipeline_id == pipeline_id).order_by(PipelineStage.order))
    ).all()
    board_stages = []
    for stage in stages:
        leads = (await db.scalars(select(Lead).where(Lead.stage_id == stage.id).order_by(Lead.created_at.desc()))).all()
        board_stages.append(
            PipelineBoardStage(
                stage_id=stage.id,
                name=stage.name,
                order=stage.order,
                lead_count=len(leads),
                leads=[
                    PipelineBoardLead(
                        lead_id=lead.id,
                        customer_name=customer_name(await db.get(Customer, lead.customer_id)),
                        priority=lead.priority,
                        program=lead.program,
                        created_at=lead.created_at,
                    )
                    for lead in leads[:leads_per_stage]
                ],
            )
        )
    return PipelineBoard(pipeline=pipeline, stages=board_stages)


async def count_rows(db: AsyncSession, model) -> int:
    return await db.scalar(select(func.count()).select_from(model)) or 0


async def count_where(db: AsyncSession, model, *conditions) -> int:
    return await db.scalar(select(func.count()).select_from(model).where(*conditions)) or 0


async def count_group(db: AsyncSession, column) -> list[CountItem]:
    rows = (await db.execute(select(column, func.count()).group_by(column))).all()
    return [CountItem(key=row[0], count=row[1]) for row in rows]


def customer_name(customer: Customer | None) -> str | None:
    if not customer:
        return None
    name = " ".join(part for part in [customer.first_name, customer.last_name] if part).strip()
    return name or None


__all__ = [
    "AuditLog",
    "Conversation",
    "Customer",
    "Department",
    "Lead",
    "LeadStageHistory",
    "Message",
    "Pipeline",
    "PipelineStage",
    "Task",
    "User",
]
