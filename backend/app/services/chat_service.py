from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AIInteraction, Conversation, Customer, Department, Lead, Message, Task
from app.schemas.chat import (
    AIAnalysisResult,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionStartRequest,
    ChatSessionStartResponse,
)
from app.schemas.crm import CustomerCreate, LeadCreate, TaskCreate
from app.services.audit_service import audit_event
from app.services.ai_service import analyze_with_ai
from app.services.customer_service import create_or_update_customer
from app.services.lead_service import create_lead
from app.services.lead_service import update_lead
from app.services.qualification_service import apply_qualification_to_lead_create, build_qualification
from app.services.task_service import create_task
from app.services.knowledge_service import search_knowledge_snippets


CONTACT_GATED_LEAD_INTENTS = {"admission_interest", "consultation_request", "international_admission", "medicine_admission"}
CONTACT_FIELD = "phone_or_email"
INFO_ONLY_NO_CONTACT_INTENTS = {"finance_question", "deadline_question"}
INFO_ONLY_NO_CONTACT_QUALIFICATION_INTENTS = {"tuition_fee", "scholarship", "schedule"}


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

    initial_knowledge_context = await retrieve_initial_knowledge_context(db, payload.message)
    history = await conversation_history(db, conversation.id)
    analysis, ai_meta = analyze_with_ai(
        payload.message,
        source_domain=payload.source_domain,
        language_hint=conversation.language,
        conversation_history=history,
        knowledge_context=initial_knowledge_context,
    )
    if not has_contact(analysis) and conversation.customer_id:
        customer = await db.get(Customer, conversation.customer_id)
        if customer:
            analysis.extracted_contact.first_name = analysis.extracted_contact.first_name or customer.first_name
            analysis.extracted_contact.last_name = analysis.extracted_contact.last_name or customer.last_name
            analysis.extracted_contact.phone = analysis.extracted_contact.phone or customer.phone
            analysis.extracted_contact.email = analysis.extracted_contact.email or customer.email
            analysis.extracted_contact.country = analysis.extracted_contact.country or customer.country
            analysis.extracted_contact.city = analysis.extracted_contact.city or customer.city
    if should_convert_contact_followup_to_admission(analysis, history, conversation):
        analysis.intent = "admission_interest"
        analysis.should_create_lead = True
        analysis.department = "Admissions"
        analysis.interest_area = analysis.interest_area or "Admissions"
        analysis.program = analysis.program or infer_program_from_history(history)
    analysis.qualification = build_qualification(payload.message, analysis)
    if analysis.qualification.handover_required:
        analysis.should_handover = True
    knowledge = await retrieve_chat_knowledge(db, payload.message, analysis)
    if knowledge["answer_source_status"] == "answered_from_approved_source":
        analysis.used_sources = knowledge["used_sources"]
        analysis.reply = build_source_backed_reply(analysis, knowledge["snippet_titles"])
    elif should_require_knowledge(analysis):
        analysis.risk_flags.append(knowledge["answer_source_status"])
        analysis.should_handover = True
        analysis.reply = build_no_source_reply(analysis)
    apply_no_contact_lead_guard(analysis)
    apply_info_only_no_contact_guard(analysis)
    await persist_ai_interaction(
        db,
        conversation_id=conversation.id,
        message_id=user_message.id,
        analysis=analysis,
        ai_meta=ai_meta,
    )
    await audit_event(
        db,
        action="ai_analysis_created",
        entity_type="conversation",
        entity_id=conversation.id,
        metadata_json={
            "provider": ai_meta["provider"],
            "intent": analysis.intent,
            "confidence": analysis.confidence,
            "risk_flags": analysis.risk_flags,
        },
    )
    await db.commit()

    created_lead_id = None
    created_task_id = None

    if analysis.intent == "general_info":
        pass
    elif analysis.intent in {"admission_interest", "consultation_request"}:
        if has_contact(analysis) and (analysis.should_create_lead or conversation.lead_id):
            created_lead_id, created_task_id = await create_admissions_flow(db, conversation, analysis)
    elif analysis.intent == "international_admission":
        if has_contact(analysis) and (analysis.should_create_lead or conversation.lead_id):
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
            "answer_source_status": knowledge["answer_source_status"],
            "used_sources": knowledge["used_sources"],
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
        answer_source_status=knowledge["answer_source_status"],
        used_sources=knowledge["used_sources"],
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
    if not has_contact(analysis):
        return None, None
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
    if not has_contact(analysis):
        return None, None
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


def apply_no_contact_lead_guard(analysis: AIAnalysisResult) -> None:
    if analysis.intent not in CONTACT_GATED_LEAD_INTENTS or has_contact(analysis):
        return
    analysis.should_create_lead = False
    if CONTACT_FIELD not in analysis.missing_fields:
        analysis.missing_fields.append(CONTACT_FIELD)
    if not analysis.extracted_contact.first_name and "first_name" not in analysis.missing_fields:
        analysis.missing_fields.append("first_name")
    analysis.qualification.recommended_next_action = "ask_contact_details"
    analysis.reply = ensure_contact_request_reply(analysis)


def apply_info_only_no_contact_guard(analysis: AIAnalysisResult) -> None:
    """Keep finance/deadline information requests from surfacing lead intent without contact."""
    if has_contact(analysis) or not is_info_only_no_contact_question(analysis):
        return
    analysis.should_create_lead = False
    analysis.missing_fields = [field for field in analysis.missing_fields if field != CONTACT_FIELD]
    if analysis.qualification.recommended_next_action in {"ask_phone_or_email", "create_follow_up_task"}:
        analysis.qualification.recommended_next_action = "answer_or_handover_without_lead"


def is_info_only_no_contact_question(analysis: AIAnalysisResult) -> bool:
    return analysis.intent in INFO_ONLY_NO_CONTACT_INTENTS or (
        analysis.qualification.intent in INFO_ONLY_NO_CONTACT_QUALIFICATION_INTENTS
        and analysis.intent not in CONTACT_GATED_LEAD_INTENTS
    )


def ensure_contact_request_reply(analysis: AIAnalysisResult) -> str:
    if reply_requests_contact(analysis.reply):
        return analysis.reply
    if analysis.language == "en":
        return (
            f"{analysis.reply} Please share your name and phone number or email so an admissions consultant can follow up."
        )
    return f"{analysis.reply} გთხოვთ მოგვწეროთ სახელი და ტელეფონი ან ელფოსტა, რომ კონსულტანტი დაგიკავშირდეთ."


def reply_requests_contact(reply: str) -> bool:
    lowered = reply.lower()
    return any(
        token in lowered
        for token in [
            "phone",
            "email",
            "contact",
            "name",
            "ტელეფ",
            "ელფოსტ",
            "საკონტაქტ",
            "სახელი",
        ]
    )


def is_medical(analysis: AIAnalysisResult) -> bool:
    haystack = f"{analysis.program or ''} {analysis.conversation_summary or ''}".lower()
    return "medicine" in haystack or "md" in haystack or "სამედიცინო" in haystack


def mentions_relocation(analysis: AIAnalysisResult) -> bool:
    haystack = f"{analysis.conversation_summary or ''}".lower()
    return "visa" in haystack or "relocation" in haystack


async def retrieve_chat_knowledge(db: AsyncSession, message: str, analysis: AIAnalysisResult) -> dict:
    if not should_use_knowledge(analysis):
        return {"answer_source_status": "not_required", "used_sources": [], "snippet_titles": []}
    category = category_for_analysis(analysis)
    results = await search_knowledge_snippets(
        db,
        query=message,
        language=analysis.language if analysis.language in {"ka", "en"} else None,
        category=category,
        source_domain=analysis.source_domain if analysis.source_domain in {"alte.edu.ge", "join.alte.edu.ge"} else None,
        program_name=analysis.program,
        approved_only=True,
    )
    if not results:
        return {"answer_source_status": "no_approved_source_found", "used_sources": [], "snippet_titles": []}
    if any(item.source_status == "source_stale" for item in results):
        status = "source_stale"
    else:
        status = "answered_from_approved_source"
    return {
        "answer_source_status": status,
        "used_sources": [item.source.source_key or item.source.title for item in results],
        "snippet_titles": [item.snippet.title for item in results],
    }


async def retrieve_initial_knowledge_context(db: AsyncSession, message: str) -> list[dict]:
    results = await search_knowledge_snippets(
        db,
        query=message,
        approved_only=True,
        include_stale=False,
        limit=3,
    )
    return [
        {
            "id": item.snippet.id,
            "title": item.snippet.title,
            "content": item.snippet.content,
            "category": item.snippet.category,
            "program_name": item.snippet.program_name,
            "source_id": item.source.id,
            "source_key": item.source.source_key,
            "source_title": item.source.title,
            "source_domain": item.source.source_domain,
            "sensitivity": item.snippet.sensitivity,
            "score": item.score,
        }
        for item in results
    ]


async def conversation_history(db: AsyncSession, conversation_id: str) -> list[dict[str, str]]:
    messages = (
        await db.scalars(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(8)
        )
    ).all()
    return [
        {"sender_type": message.sender_type, "text": message.text}
        for message in reversed(messages)
    ]


async def persist_ai_interaction(
    db: AsyncSession,
    *,
    conversation_id: str,
    message_id: str | None,
    analysis: AIAnalysisResult,
    ai_meta: dict,
) -> None:
    db.add(
        AIInteraction(
            conversation_id=conversation_id,
            message_id=message_id,
            provider=ai_meta["provider"],
            model=ai_meta["model"],
            intent=analysis.intent,
            confidence=analysis.confidence,
            answer=analysis.reply,
            sources_json=analysis.used_sources,
            flags_json=analysis.risk_flags,
            raw_response_json=ai_meta.get("raw_response"),
        )
    )


def should_use_knowledge(analysis: AIAnalysisResult) -> bool:
    return analysis.intent in {"admission_interest", "international_admission", "finance_question"} or (
        analysis.qualification.intent
        in {"program_info", "admission_requirements", "tuition_fee", "scholarship", "application"}
    )


def should_require_knowledge(analysis: AIAnalysisResult) -> bool:
    return analysis.intent == "finance_question" or analysis.qualification.intent in {
        "tuition_fee",
        "scholarship",
        "admission_requirements",
    }


def category_for_analysis(analysis: AIAnalysisResult) -> str | None:
    if analysis.qualification.intent == "tuition_fee":
        return "finance"
    if analysis.qualification.intent == "scholarship":
        return "scholarship"
    if analysis.qualification.intent in {"admission_requirements", "application"}:
        return "admissions"
    if analysis.program:
        return "programs"
    return None


def build_source_backed_reply(analysis: AIAnalysisResult, snippet_titles: list[str]) -> str:
    source_hint = ", ".join(snippet_titles[:2])
    if analysis.language == "en":
        return f"I found verified information from approved sources: {source_hint}. A consultant can help with the next step if you want."
    return f"მოვძებნე დადასტურებული ინფორმაცია დამტკიცებული წყაროდან: {source_hint}. სურვილის შემთხვევაში კონსულტანტიც დაგეხმარებათ შემდეგ ნაბიჯში."


def build_no_source_reply(analysis: AIAnalysisResult) -> str:
    if analysis.language == "en":
        return "I need verified information from admissions before giving an exact answer. A consultant can confirm this for you."
    return "ზუსტი პასუხისთვის მჭირდება დადასტურებული ინფორმაცია admissions/კონსულტანტისგან. კონსულტანტი დაგიდასტურებთ დეტალებს."


def should_convert_contact_followup_to_admission(
    analysis: AIAnalysisResult,
    history: list[dict[str, str]],
    conversation: Conversation,
) -> bool:
    if conversation.lead_id or not has_contact(analysis):
        return False
    if analysis.intent not in {"general_info", "unknown"}:
        return False
    return history_contains_admission_interest(history)


def history_contains_admission_interest(history: list[dict[str, str]]) -> bool:
    haystack = " ".join(item["text"] for item in history).lower()
    return any(
        needle in haystack
        for needle in [
            "admission",
            "apply",
            "application",
            "program",
            "business",
            "მიღება",
            "ჩარიცხვა",
            "პროგრამა",
            "ბიზნეს",
            "მაინტერესებს",
        ]
    )


def infer_program_from_history(history: list[dict[str, str]]) -> str | None:
    haystack = " ".join(item["text"] for item in history).lower()
    if "business" in haystack or "ბიზნეს" in haystack:
        return "Business"
    if "medicine" in haystack or "md" in haystack or "მედიცინ" in haystack:
        return "Medicine / 6-year MD"
    if "law" in haystack or "სამართ" in haystack:
        return "Law"
    return None


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
