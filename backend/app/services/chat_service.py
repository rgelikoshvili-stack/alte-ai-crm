from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.mock_ai_analyzer import analyze_message
from app.models import Conversation, Customer, Department, Lead, Message, Task
from app.schemas.chat import (
    AIAnalysisResult,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionStartRequest,
    ChatSessionStartResponse,
)
from app.schemas.crm import CustomerCreate, LeadCreate, TaskCreate
from app.services.audit_service import audit_event
from app.services.customer_service import create_or_update_customer
from app.services.lead_service import create_lead
from app.services.lead_service import update_lead
from app.services.qualification_service import apply_qualification_to_lead_create, build_qualification
from app.services.task_service import create_task


async def start_session(db: AsyncSession, payload: ChatSessionStartRequest) -> ChatSessionStartResponse:
    conversation = Conversation(channel="website_chat", language=payload.language, ai_handled=True)
    db.add(conversation)
    await db.flush()
    await audit_event(
        db,
        action="chat_session_started",
        entity_type="conversation",
        entity_id=conversation.id,
        metadata_json={"source_domain": payload.source_domain},
    )
    await db.commit()
    await db.refresh(conversation)
    return ChatSessionStartResponse(
        conversation_id=conversation.id,
        session_id=str(uuid4()),
        source_domain=payload.source_domain,
    )


async def handle_message(db: AsyncSession, payload: ChatMessageRequest) -> ChatMessageResponse:
    conversation = await db.get(Conversation, payload.conversation_id)
    if conversation is None:
        raise ValueError("Conversation not found")

    user_message = Message(
        conversation_id=conversation.id,
        sender_type="user",
        text=payload.message,
        metadata_json={"session_id": payload.session_id, "source_domain": payload.source_domain},
    )
    db.add(user_message)
    await db.flush()
    await audit_event(
        db,
        action="chat_message_received",
        entity_type="message",
        entity_id=user_message.id,
        metadata_json={"conversation_id": conversation.id},
    )

    analysis = analyze_message(payload.message, payload.source_domain)
    if not has_contact(analysis) and conversation.customer_id:
        customer = await db.get(Customer, conversation.customer_id)
        if customer:
            analysis.extracted_contact.first_name = analysis.extracted_contact.first_name or customer.first_name
            analysis.extracted_contact.last_name = analysis.extracted_contact.last_name or customer.last_name
            analysis.extracted_contact.phone = analysis.extracted_contact.phone or customer.phone
            analysis.extracted_contact.email = analysis.extracted_contact.email or customer.email
            analysis.extracted_contact.country = analysis.extracted_contact.country or customer.country
            analysis.extracted_contact.city = analysis.extracted_contact.city or customer.city
    analysis.qualification = build_qualification(payload.message, analysis)
    if analysis.qualification.handover_required:
        analysis.should_handover = True
    await audit_event(
        db,
        action="ai_mock_analysis_created",
        entity_type="conversation",
        entity_id=conversation.id,
        metadata_json=analysis.model_dump(),
    )
    await db.commit()

    created_lead_id = None
    created_task_id = None

    if analysis.intent == "general_info":
        pass
    elif analysis.intent in {"admission_interest", "consultation_request"}:
        if analysis.should_create_lead or conversation.lead_id:
            created_lead_id, created_task_id = await create_admissions_flow(db, conversation, analysis)
    elif analysis.intent == "international_admission":
        if analysis.should_create_lead or conversation.lead_id:
            created_lead_id, created_task_id = await create_international_flow(db, conversation, analysis)
    elif analysis.intent == "human_request":
        conversation.human_handover = True
        if has_contact(analysis):
            created_task_id = await create_handover_task(db, conversation, analysis)
    elif analysis.intent == "finance_question":
        if has_contact(analysis):
            created_task_id = await create_department_task(db, conversation, analysis, "Finance")
    elif analysis.intent == "student_service":
        if analysis.should_handover and has_contact(analysis):
            created_task_id = await create_department_task(db, conversation, analysis, "Student Services")

    ai_reply = Message(
        conversation_id=conversation.id,
        sender_type="ai",
        text=analysis.reply,
        metadata_json={
            "intent": analysis.intent,
            "confidence": analysis.confidence,
            "missing_fields": analysis.missing_fields,
            "risk_flags": analysis.risk_flags,
            "qualification": analysis.qualification.model_dump(),
        },
    )
    db.add(ai_reply)
    conversation.summary = analysis.conversation_summary
    await db.flush()
    await audit_event(
        db,
        action="ai_reply_saved",
        entity_type="message",
        entity_id=ai_reply.id,
        metadata_json={"conversation_id": conversation.id, "intent": analysis.intent},
    )
    await db.commit()

    return ChatMessageResponse(
        conversation_id=conversation.id,
        reply=analysis.reply,
        intent=analysis.intent,
        confidence=analysis.confidence,
        should_create_lead=analysis.should_create_lead,
        should_handover=analysis.should_handover,
        created_lead_id=created_lead_id,
        created_task_id=created_task_id,
        missing_fields=analysis.missing_fields,
        lead_score=analysis.qualification.lead_score,
        qualification_status=analysis.qualification.qualification_status,
        handover_reason=analysis.qualification.handover_reason,
        recommended_next_action=analysis.qualification.recommended_next_action,
    )


async def request_handover(db: AsyncSession, conversation_id: str) -> dict[str, str | None]:
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise ValueError("Conversation not found")
    conversation.human_handover = True
    task = Task(
        lead_id=conversation.lead_id,
        customer_id=conversation.customer_id,
        title="Human handover requested",
        description="Website chat user requested operator handover.",
        priority="high",
        due_date=datetime.now(UTC) + timedelta(hours=4),
    )
    db.add(task)
    await db.flush()
    await audit_event(
        db,
        action="handover_requested",
        entity_type="conversation",
        entity_id=conversation.id,
        metadata_json={"task_id": task.id},
    )
    await db.commit()
    return {"status": "handover_requested", "conversation_id": conversation.id, "task_id": task.id}


async def create_admissions_flow(
    db: AsyncSession,
    conversation: Conversation,
    analysis: AIAnalysisResult,
) -> tuple[str | None, str | None]:
    customer = await get_or_create_customer_for_conversation(db, conversation, analysis)
    lead_data = apply_qualification_to_lead_create(
        {
            "customer_id": customer.id,
            "interest_area": analysis.interest_area,
            "program": analysis.program,
            "priority": analysis.priority,
            "source_channel": "website_chat",
            "source_domain": analysis.source_domain if analysis.source_domain in {"alte.edu.ge", "join.alte.edu.ge"} else None,
            "is_international_priority": analysis.source_domain == "join.alte.edu.ge",
            "medical_track": is_medical(analysis),
        },
        analysis.qualification,
    )
    lead, created = await create_or_update_conversation_lead(db, conversation, lead_data)
    task = await create_task(
        db,
        TaskCreate(
            lead_id=lead.id,
            customer_id=customer.id,
            title="Follow up admissions lead",
            description=analysis.conversation_summary,
            due_date=datetime.now(UTC) + timedelta(hours=24),
            priority=analysis.priority,
        ),
    )
    conversation.customer_id = customer.id
    conversation.lead_id = lead.id
    await db.commit()
    return lead.id, task.id if created else None


async def create_international_flow(
    db: AsyncSession,
    conversation: Conversation,
    analysis: AIAnalysisResult,
) -> tuple[str | None, str | None]:
    customer = await get_or_create_customer_for_conversation(db, conversation, analysis)
    department = await find_department(db, "International Admissions")
    lead_data = apply_qualification_to_lead_create(
        {
            "customer_id": customer.id,
            "interest_area": analysis.interest_area or "International admission",
            "program": analysis.program,
            "department_id": department.id if department else None,
            "priority": "high",
            "source_channel": "website_chat",
            "source_domain": analysis.source_domain if analysis.source_domain in {"alte.edu.ge", "join.alte.edu.ge"} else None,
            "is_international_priority": True,
            "medical_track": is_medical(analysis),
            "relocation_needed": mentions_relocation(analysis),
        },
        analysis.qualification,
    )
    lead, created = await create_or_update_conversation_lead(db, conversation, lead_data)
    task = await create_task(
        db,
        TaskCreate(
            lead_id=lead.id,
            customer_id=customer.id,
            department_id=department.id if department else None,
            title="Follow up international admissions lead",
            description=analysis.conversation_summary,
            due_date=datetime.now(UTC) + timedelta(hours=24),
            priority="high",
        ),
    )
    conversation.customer_id = customer.id
    conversation.lead_id = lead.id
    await db.commit()
    return lead.id, task.id if created else None


async def create_handover_task(db: AsyncSession, conversation: Conversation, analysis: AIAnalysisResult) -> str | None:
    customer = await create_customer_from_analysis(db, analysis)
    conversation.customer_id = customer.id
    task_id = await create_department_task(db, conversation, analysis, analysis.department or "Admissions")
    await db.commit()
    return task_id


async def create_department_task(
    db: AsyncSession,
    conversation: Conversation,
    analysis: AIAnalysisResult,
    department_name: str,
) -> str | None:
    department = await find_department(db, department_name)
    task = await create_task(
        db,
        TaskCreate(
            lead_id=conversation.lead_id,
            customer_id=conversation.customer_id,
            department_id=department.id if department else None,
            title=f"{department_name} follow-up",
            description=analysis.conversation_summary,
            due_date=datetime.now(UTC) + timedelta(hours=4),
            priority=analysis.priority,
        ),
    )
    return task.id


async def create_customer_from_analysis(db: AsyncSession, analysis: AIAnalysisResult):
    contact = analysis.extracted_contact
    return await create_or_update_customer(
        db,
        CustomerCreate(
            first_name=contact.first_name,
            last_name=contact.last_name,
            phone=contact.phone,
            email=contact.email,
            country=contact.country,
            city=contact.city,
            source_channel="website_chat",
            consent_status="implicit_chat_request",
        ),
    )


async def get_or_create_customer_for_conversation(
    db: AsyncSession,
    conversation: Conversation,
    analysis: AIAnalysisResult,
) -> Customer:
    if has_contact(analysis):
        return await create_customer_from_analysis(db, analysis)
    if conversation.customer_id:
        customer = await db.get(Customer, conversation.customer_id)
        if customer:
            return customer
    return await create_customer_from_analysis(db, analysis)


async def find_department(db: AsyncSession, name: str) -> Department | None:
    return await db.scalar(select(Department).where(Department.name == name))


def has_contact(analysis: AIAnalysisResult) -> bool:
    contact = analysis.extracted_contact
    return bool(contact.phone or contact.email)


def is_medical(analysis: AIAnalysisResult) -> bool:
    haystack = f"{analysis.program or ''} {analysis.conversation_summary or ''}".lower()
    return "medicine" in haystack or "md" in haystack or "სამედიცინო" in haystack


def mentions_relocation(analysis: AIAnalysisResult) -> bool:
    haystack = f"{analysis.conversation_summary or ''}".lower()
    return "visa" in haystack or "relocation" in haystack


async def create_or_update_conversation_lead(
    db: AsyncSession,
    conversation: Conversation,
    lead_data: dict,
) -> tuple[Lead, bool]:
    if conversation.lead_id:
        lead = await db.get(Lead, conversation.lead_id)
        if lead:
            from app.schemas.crm import LeadUpdate

            await update_lead(db, lead, LeadUpdate(**{k: v for k, v in lead_data.items() if k != "customer_id"}))
            return lead, False
    lead = await create_lead(db, LeadCreate(**lead_data))
    return lead, True
