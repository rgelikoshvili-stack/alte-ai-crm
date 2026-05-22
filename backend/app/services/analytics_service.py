from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation, Customer, KnowledgeSnippet, KnowledgeSource, Lead, Message, Task
from app.schemas.analytics import (
    AiAnalytics,
    AnalyticsOverview,
    KnowledgeAnalytics,
    LeadAnalytics,
    SlaAnalytics,
)
from app.schemas.operator import CountItem


async def build_analytics_overview(db: AsyncSession) -> AnalyticsOverview:
    ai_messages = await get_ai_messages(db)
    return AnalyticsOverview(
        total_leads=await count_rows(db, Lead),
        hot_leads=await count_where(db, Lead, Lead.qualification_status == "hot"),
        qualified_leads=await count_where(db, Lead, Lead.qualification_status.in_(["qualified", "hot"])),
        average_lead_score=await average_lead_score(db),
        total_conversations=await count_rows(db, Conversation),
        human_handover_count=await count_where(db, Conversation, Conversation.human_handover.is_(True)),
        open_tasks=await count_where(db, Task, Task.status.in_(["open", "in_progress"])),
        overdue_tasks=await overdue_task_count(db),
        knowledge_no_source_count=count_metadata_status(ai_messages, "no_approved_source_found"),
        answered_from_source_count=count_metadata_status(ai_messages, "answered_from_approved_source"),
    )


async def build_lead_analytics(db: AsyncSession) -> LeadAnalytics:
    return LeadAnalytics(
        leads_by_status=await count_group(db, Lead.status),
        leads_by_priority=await count_group(db, Lead.priority),
        leads_by_source_domain=await count_group(db, Lead.source_domain),
        leads_by_program=await count_group(db, Lead.program),
        leads_by_country=await count_customer_country_for_leads(db),
        leads_by_qualification_status=await count_group(db, Lead.qualification_status),
        international_priority_count=await count_where(db, Lead, Lead.is_international_priority.is_(True)),
        medical_track_count=await count_where(db, Lead, Lead.medical_track.is_(True)),
    )


async def build_sla_analytics(db: AsyncSession) -> SlaAnalytics:
    now = datetime.now(UTC)
    tomorrow = now + timedelta(days=1)
    return SlaAnalytics(
        open_tasks=await count_where(db, Task, Task.status.in_(["open", "in_progress"])),
        overdue_tasks=await overdue_task_count(db),
        due_today_tasks=await count_where(db, Task, Task.due_date >= now, Task.due_date < tomorrow, Task.status != "completed"),
        completed_tasks=await count_where(db, Task, Task.status == "completed"),
        urgent_open_tasks=await count_where(db, Task, Task.priority == "urgent", Task.status.in_(["open", "in_progress"])),
        human_handover_count=await count_where(db, Conversation, Conversation.human_handover.is_(True)),
        open_handover_conversations=await count_where(
            db,
            Conversation,
            Conversation.human_handover.is_(True),
            Conversation.status == "open",
        ),
    )


async def build_knowledge_analytics(db: AsyncSession) -> KnowledgeAnalytics:
    ai_messages = await get_ai_messages(db)
    today = datetime.now(UTC).date()
    stale = await db.scalar(
        select(func.count()).select_from(KnowledgeSnippet).where(KnowledgeSnippet.effective_to < today)
    )
    return KnowledgeAnalytics(
        total_sources=await count_rows(db, KnowledgeSource),
        sources_by_status=await count_group(db, KnowledgeSource.status),
        sources_by_language=await count_group(db, KnowledgeSource.language),
        total_snippets=await count_rows(db, KnowledgeSnippet),
        snippets_by_status=await count_group(db, KnowledgeSnippet.status),
        stale_snippets=stale or 0,
        no_approved_source_events=count_metadata_status(ai_messages, "no_approved_source_found"),
        answered_from_source_events=count_metadata_status(ai_messages, "answered_from_approved_source"),
    )


async def build_ai_analytics(db: AsyncSession) -> AiAnalytics:
    ai_messages = await get_ai_messages(db)
    confidences = [
        float(message.metadata_json.get("confidence"))
        for message in ai_messages
        if isinstance(message.metadata_json, dict) and message.metadata_json.get("confidence") is not None
    ]
    return AiAnalytics(
        total_ai_messages=len(ai_messages),
        average_confidence=round(sum(confidences) / len(confidences), 4) if confidences else 0.0,
        intents=count_metadata_values(ai_messages, "intent"),
        answer_source_statuses=count_metadata_values(ai_messages, "answer_source_status"),
        handover_recommended_count=sum(
            1
            for message in ai_messages
            if isinstance(message.metadata_json, dict)
            and message.metadata_json.get("qualification", {}).get("handover_required") is True
        ),
    )


async def get_ai_messages(db: AsyncSession) -> list[Message]:
    return (await db.scalars(select(Message).where(Message.sender_type == "ai"))).all()


async def count_rows(db: AsyncSession, model) -> int:
    return await db.scalar(select(func.count()).select_from(model)) or 0


async def count_where(db: AsyncSession, model, *conditions) -> int:
    return await db.scalar(select(func.count()).select_from(model).where(*conditions)) or 0


async def overdue_task_count(db: AsyncSession) -> int:
    return await count_where(db, Task, Task.due_date < datetime.now(UTC), Task.status != "completed")


async def average_lead_score(db: AsyncSession) -> float:
    value = await db.scalar(select(func.avg(Lead.lead_score)).where(Lead.lead_score.is_not(None)))
    return round(float(value), 2) if value is not None else 0.0


async def count_group(db: AsyncSession, column) -> list[CountItem]:
    rows = (await db.execute(select(column, func.count()).group_by(column))).all()
    return [CountItem(key=row[0], count=row[1]) for row in rows]


async def count_customer_country_for_leads(db: AsyncSession) -> list[CountItem]:
    rows = (
        await db.execute(
            select(Customer.country, func.count())
            .select_from(Lead)
            .join(Customer, Customer.id == Lead.customer_id)
            .group_by(Customer.country)
        )
    ).all()
    return [CountItem(key=row[0], count=row[1]) for row in rows]


def count_metadata_values(messages: list[Message], key: str) -> list[CountItem]:
    counter: Counter[str | None] = Counter()
    for message in messages:
        if isinstance(message.metadata_json, dict):
            counter[message.metadata_json.get(key)] += 1
    return [CountItem(key=key, count=count) for key, count in counter.items()]


def count_metadata_status(messages: list[Message], status: str) -> int:
    return sum(
        1
        for message in messages
        if isinstance(message.metadata_json, dict) and message.metadata_json.get("answer_source_status") == status
    )

