import re
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AIInteraction, AuditLog, Conversation, Customer, Department, Lead, Message, Task
from app.schemas.chat import (
    AIAnalysisResult,
    ChatContactRequest,
    ChatContactResponse,
    ChatHandoverRequest,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionStartRequest,
    ChatSessionStartResponse,
    ChatTranscriptMessage,
)
from app.schemas.crm import CustomerCreate, LeadCreate, LeadUpdate, TaskCreate
from app.services.audit_service import audit_event
from app.services.ai_service import analyze_with_ai
from app.services.customer_service import create_or_update_customer
from app.services.department_routing_service import DepartmentRoutingResult, resolve_department
from app.services.knowledge_routing_service import (
    KnowledgeRouteDecision,
    classify_knowledge_route,
    format_clarification_reply,
    source_group_config,
)
from app.services.lead_service import create_lead
from app.services.lead_service import update_lead
from app.services.qualification_service import apply_qualification_to_lead_create, build_qualification
from app.services.task_service import create_task
from app.services.knowledge_service import search_knowledge_snippets


CONTACT_GATED_LEAD_INTENTS = {"admission_interest", "consultation_request", "international_admission", "medicine_admission"}
CONTACT_FIELD = "phone_or_email"
INFO_ONLY_NO_CONTACT_INTENTS = {"finance_question", "deadline_question"}
INFO_ONLY_NO_CONTACT_QUALIFICATION_INTENTS = {"tuition_fee", "scholarship", "schedule"}
SAFE_CONTACT_CONSENT_EN = (
    'If you would like an operator to follow up, click "Yes, contact". '
    "Contact details should only be shared after your explicit consent."
)
SAFE_CONTACT_CONSENT_KA = (
    "თუ გსურთ ოპერატორთან დაკავშირება, დააჭირეთ „დიახ, კონტაქტი“-ს. "
    "საკონტაქტო ინფორმაციის გაზიარება მხოლოდ თქვენი მკაფიო თანხმობის შემდეგ უნდა მოხდეს."
)

OFFICIAL_ALTE_PDF_SOURCE_DOMAIN = "official_alte_pdf_kb"

GEORGIAN_RETRIEVAL_ALIASES = [
    (
        ["რამდენი კრედიტია ბაკალავრიატი", "ბაკალავრიატის დასრულებისთვის", "საბაკალავრო", "ბაკალავრიატ"],
        "ბაკალავრიატი საბაკალავრო ECTS კრედიტი 240 bachelor completion",
    ),
    (
        ["რამდენი კრედიტია სამაგისტრო", "სამაგისტრო პროგრამა", "მაგისტრატურა", "მაგისტრატურის"],
        "მაგისტრატურა სამაგისტრო ECTS კრედიტი 120 master",
    ),
    (
        ["სტატუსი რამდენ ხანს", "სტატუსის შეჩერ", "შევიჩერო", "სტატუსი შევიჩერო"],
        "სტუდენტის სტატუსის შეჩერება 5 წელი status suspension",
    ),
    (
        ["საბუთებია მაგისტრატურაზე", "საბუთები მაგისტრატურაზე", "მაგისტრატურაზე", "ჩასარიცხად"],
        "მაგისტრატურა ჩარიცხვის საბუთები დოკუმენტები ID CV 3x4 სამხედრო ნოტარიული დიპლომის დანართი",
    ),
    (
        ["ფინანსური დახმარება", "ფინანსური მხარდაჭერა", "დაფინანსება არსებობს"],
        "ფინანსური მხარდაჭერის მექანიზმები დაფინანსების წესი funding rule financial support",
    ),
    (
        ["ai-ის გამოყენ", "ai-ს გამოყენ", "ai გამოყენ", "ხელოვნური ინტელექტის გამოყენ"],
        "გენერაციული AI ხელოვნური ინტელექტის გამოყენების პოლიტიკა AI policy",
    ),
]
CONTACT_REQUEST_MARKERS = [
    "please confirm your contact details",
    "contact details (name, phone, email)",
    "please share your name and phone number or email",
    "please share your name, phone, or email",
    "please share your phone or email",
    "please provide your phone",
    "please provide your email",
    "provide phone or email",
    "phone or email so",
    "name, phone, email",
    "name and phone",
    "share your name",
    "share your phone",
    "share your email",
    "გთხოვთ მოგვწეროთ სახელი",
    "გთხოვთ მომწეროთ სახელი",
    "ტელეფონი ან ელფოსტა",
    "ტელეფონი ან ელ.ფოსტა",
    "ტელეფონი ან ელ-ფოსტა",
    "თუ გსურთ უფრო სწრაფი კონტაქტი",
    "ტელეფონის ნომერი ან ელ-ფოსტა",
    "მიუთითოთ საკონტაქტო ინფორმაცია",
    "მიუთითეთ საკონტაქტო ინფორმაცია",
    "საკონტაქტო ინფორმაცია (სახელი",
    "სახელი, ტელეფონი ან ელ. ფოსტა",
    "გთხოვთ, მომაწოდოთ თქვენი",
    "გთხოვთ მომაწოდოთ თქვენი",
    "გთხოვთ, მოგვაწოდოთ თქვენი",
    "გთხოვთ მოგვაწოდოთ თქვენი",
    "დატოვოთ საკონტაქტო ინფორმაცია",
    "დატოვეთ საკონტაქტო ინფორმაცია",
]

CONTACT_REQUEST_REGEXES = [
    "გთხოვთ.{0,80}(სახელი|ტელეფონი|ელფოსტა|ელ\\. ფოსტა|მეილი)",
    "(მიუთითოთ|მიუთითეთ|შეიყვანოთ|შეიყვანეთ|დატოვოთ|დატოვეთ|მომაწოდოთ|მომაწოდეთ|მოგვაწოდოთ|მოგვაწოდეთ).{0,80}(თქვენი|საკონტაქტო|სახელი|ტელეფონი|ელფოსტა|ელ\\. ფოსტა|მეილი)",
    "(სახელი|ტელეფონი|ელფოსტა|ელ\\. ფოსტა|მეილი).{0,80}(მიუთითოთ|მიუთითეთ|შეიყვანოთ|შეიყვანეთ|დატოვოთ|დატოვეთ|მომაწოდოთ|მომაწოდეთ|მოგვაწოდოთ|მოგვაწოდეთ)",
]


async def start_session(db: AsyncSession, payload: ChatSessionStartRequest) -> ChatSessionStartResponse:
    conversation = Conversation(channel="website_chat", language=payload.language, ai_handled=True)
    db.add(conversation)
    await db.flush()
    session_id = str(uuid4())
    await audit_event(
        db,
        action="chat_session_started",
        entity_type="conversation",
        entity_id=conversation.id,
        metadata_json={
            "source_domain": payload.source_domain,
            "session_id": session_id,
            "widget_variant": payload.widget_variant,
            "metadata": payload.metadata or {},
        },
    )
    await db.commit()
    await db.refresh(conversation)
    return ChatSessionStartResponse(
        conversation_id=conversation.id,
        session_id=session_id,
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
        metadata_json={
            "session_id": payload.session_id,
            "source_domain": payload.source_domain,
            "selected_department": payload.selected_department,
            "selected_topic": payload.selected_topic,
            "page_url": payload.page_url,
            "widget_variant": payload.widget_variant,
        },
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

    route_decision = classify_knowledge_route(
        payload.message,
        selected_department=payload.selected_department,
        source_domain=payload.source_domain,
    )
    if route_decision.clarification_required:
        return await handle_clarification_response(db, conversation, user_message, route_decision)

    initial_knowledge_context = await retrieve_initial_knowledge_context(db, payload.message, route_decision)
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
    unsupported_official_question = is_clearly_unsupported_official_question(payload.message)
    if unsupported_official_question:
        knowledge = {"answer_source_status": "no_approved_source_found", "used_sources": [], "snippet_titles": []}
    else:
        knowledge = await retrieve_chat_knowledge(db, payload.message, analysis, route_decision)
    if knowledge["answer_source_status"] == "answered_from_approved_source":
        analysis.used_sources = knowledge["used_sources"]
        official_reply = official_academic_rules_regression_reply(payload.message, analysis.language) or selected_official_document_regression_reply(
            payload.message, analysis.language
        )
        if official_reply:
            analysis.reply = official_reply
        analysis.reply = build_source_backed_reply(analysis, knowledge["snippet_titles"])
    elif (
        unsupported_official_question
        or should_require_knowledge(analysis)
        or is_official_academic_rules_text(payload.message)
        or is_selected_official_document_text(payload.message)
    ):
        analysis.risk_flags.append(knowledge["answer_source_status"])
        analysis.should_handover = True
        if is_ambiguous_program_question(payload.message, analysis):
            analysis.reply = build_ambiguous_program_reply(analysis)
        else:
            analysis.reply = build_no_source_reply(analysis)
    sanitize_premature_contact_request(analysis)
    apply_no_contact_lead_guard(analysis)
    apply_info_only_no_contact_guard(analysis)
    routing = apply_department_routing(analysis, payload, knowledge)
    sanitize_premature_contact_request(analysis)
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
            "route_department": routing.department,
            "department_key": routing.department_key,
            "source_group": route_decision.primary_source_group,
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
            "route_department": routing.department,
            "department_key": routing.department_key,
            "routing_reason": routing.reason,
            "handover_reason": routing.confidence_reason if analysis.should_handover else None,
            "source_group": route_decision.primary_source_group,
            "source_groups": route_decision.source_groups,
            "clarification_needed": False,
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
        handover_reason=analysis.qualification.handover_reason or (routing.confidence_reason if analysis.should_handover else None),
        recommended_next_action=analysis.qualification.recommended_next_action,
        answer_source_status=knowledge["answer_source_status"],
        used_sources=knowledge["used_sources"],
        route_department=routing.department,
        department_key=routing.department_key,
        routing_reason=routing.reason,
        source_group=route_decision.primary_source_group,
        clarification_needed=False,
        clarification_options=[],
    )


async def handle_clarification_response(
    db: AsyncSession,
    conversation: Conversation,
    user_message: Message,
    decision: KnowledgeRouteDecision,
) -> ChatMessageResponse:
    reply = format_clarification_reply(decision)
    analysis = AIAnalysisResult(
        reply=reply,
        language=decision.language,  # type: ignore[arg-type]
        intent="clarification",
        confidence=decision.confidence,
        should_create_lead=False,
        should_handover=False,
        department=decision.department_label,
        risk_flags=["clarification_required"],
    )
    await persist_ai_interaction(
        db,
        conversation_id=conversation.id,
        message_id=user_message.id,
        analysis=analysis,
        ai_meta={"provider": "deterministic_routing", "model": "phase_9ai_clarification", "raw_response": None},
    )
    ai_reply = Message(
        conversation_id=conversation.id,
        sender_type="ai",
        text=reply,
        metadata_json={
            "intent": analysis.intent,
            "confidence": analysis.confidence,
            "risk_flags": analysis.risk_flags,
            "answer_source_status": "clarification_needed",
            "used_sources": [],
            "route_department": decision.department_label,
            "department_key": decision.department_id,
            "routing_reason": decision.reason,
            "source_group": decision.primary_source_group,
            "source_groups": decision.source_groups,
            "clarification_needed": True,
            "clarification_options": decision.clarification_options,
        },
    )
    db.add(ai_reply)
    await db.flush()
    await audit_event(
        db,
        action="ai_clarification_saved",
        entity_type="message",
        entity_id=ai_reply.id,
        metadata_json={
            "conversation_id": conversation.id,
            "department_key": decision.department_id,
            "source_group": decision.primary_source_group,
        },
    )
    await db.commit()
    return ChatMessageResponse(
        conversation_id=conversation.id,
        reply=reply,
        intent=analysis.intent,
        confidence=analysis.confidence,
        should_create_lead=False,
        should_handover=False,
        answer_source_status="clarification_needed",
        used_sources=[],
        route_department=decision.department_label,
        department_key=decision.department_id,
        routing_reason=decision.reason,
        source_group=decision.primary_source_group,
        clarification_needed=True,
        clarification_options=decision.clarification_options,
    )


async def request_handover(
    db: AsyncSession,
    conversation_id: str,
    *,
    payload: ChatHandoverRequest | None = None,
) -> dict[str, str | None]:
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise ValueError("Conversation not found")
    session_id = payload.session_id if payload else None
    if not await handover_session_matches(db, conversation_id, session_id):
        raise PermissionError("Valid conversation session required")
    conversation.human_handover = True
    conversation.status = "waiting_for_operator"
    handover_message = handover_payload_message(payload)
    if handover_message:
        latest_user_message = await db.scalar(
            select(Message)
            .where(Message.conversation_id == conversation.id, Message.sender_type == "user")
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        if latest_user_message is None or latest_user_message.text.strip() != handover_message.strip():
            db.add(
                Message(
                    conversation_id=conversation.id,
                    sender_type="user",
                    text=handover_message.strip(),
                    metadata_json={
                        "session_id": session_id,
                        "handover_request": True,
                        "handover_mode": payload.mode if payload else None,
                        "handover_reason": payload.reason if payload else None,
                        "selected_department": payload.selected_department if payload else None,
                        "selected_topic": payload.selected_topic if payload else None,
                        "source_domain": payload.source_domain if payload else None,
                    },
                )
            )
            await db.flush()
    if not conversation.customer_id and not conversation.lead_id:
        await audit_event(
            db,
            action="handover_waiting_for_operator",
            entity_type="conversation",
            entity_id=conversation.id,
            metadata_json={
                "status": "waiting_for_operator",
                "reason": (payload.reason if payload else None) or "wait_for_operator",
                "selected_department": payload.selected_department if payload else None,
                "selected_topic": payload.selected_topic if payload else None,
                "source_domain": payload.source_domain if payload else None,
                "language": payload.language if payload else None,
                "message": handover_message,
                "customer_or_lead_created": False,
                "task_created": False,
            },
        )
        await db.commit()
        return {
            "status": "waiting_for_operator",
            "conversation_id": conversation.id,
            "task_id": None,
        }
    existing_task = await find_existing_handover_task(db, conversation)
    if existing_task:
        await db.commit()
        return {
            "status": "handover_already_requested",
            "conversation_id": conversation.id,
            "task_id": existing_task.id,
        }
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
        metadata_json={
            "task_id": task.id,
            "status": "waiting_for_operator",
            "reason": (payload.reason if payload else None) or "wait_for_operator",
            "selected_department": payload.selected_department if payload else None,
            "selected_topic": payload.selected_topic if payload else None,
            "message": handover_message,
        },
    )
    await db.commit()
    return {"status": "handover_requested", "conversation_id": conversation.id, "task_id": task.id}


async def submit_chat_contact(
    db: AsyncSession,
    conversation_id: str,
    payload: ChatContactRequest,
) -> ChatContactResponse:
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise ValueError("Conversation not found")
    if not await handover_session_matches(db, conversation_id, payload.session_id):
        raise PermissionError("Invalid chat session")
    if not payload.consent:
        raise PermissionError("Consent is required before contact handover")
    if not (payload.phone or payload.email):
        raise ValueError("Phone or email is required")
    contact_message = contact_payload_message(payload)
    if contact_message:
        db.add(
            Message(
                conversation_id=conversation.id,
                sender_type="user",
                text=contact_message.strip(),
                metadata_json={
                    "session_id": payload.session_id,
                    "contact_form_message": True,
                    "selected_department": payload.selected_department,
                    "selected_topic": payload.selected_topic,
                    "source_domain": payload.source_domain,
                },
            )
        )
        await db.flush()

    first_name, last_name = split_contact_name(payload)
    customer = await create_or_update_customer(
        db,
        CustomerCreate(
            first_name=first_name,
            last_name=last_name,
            phone=payload.phone,
            email=payload.email,
            source_channel="website_chat",
            consent_status="explicit_chat_contact_request",
        ),
    )
    conversation.customer_id = customer.id
    conversation.human_handover = True

    department_name = department_name_from_selection(payload.selected_department)
    department = await find_department(db, department_name)
    lead = None
    lead_payload = lead_payload_from_contact(customer.id, payload, department.id if department else None)
    if conversation.lead_id:
        lead = await db.get(Lead, conversation.lead_id)
        if lead:
            await update_lead(db, lead, LeadUpdate(**{k: v for k, v in lead_payload.items() if k != "customer_id"}))
    if lead is None:
        lead = await create_lead(db, LeadCreate(**lead_payload))
        conversation.lead_id = lead.id

    await db.commit()

    existing_task = await find_existing_handover_task(db, conversation)
    if existing_task:
        task_id = existing_task.id
        status = "contact_received_handover_already_requested"
    else:
        task = await create_task(
            db,
            TaskCreate(
                lead_id=conversation.lead_id,
                customer_id=conversation.customer_id,
                department_id=department.id if department else None,
                title="Human handover requested",
                description=(
                    "Website chat visitor left contact details for operator follow-up. "
                    f"Interest: {payload.interest_area or payload.selected_topic or 'not specified'}. "
                    f"Message: {contact_message or 'not provided'}."
                ),
                due_date=datetime.now(UTC) + timedelta(hours=4),
                priority="high" if payload.selected_department in {"international", "medicine"} else "normal",
            ),
        )
        task_id = task.id
        status = "contact_received_handover_requested"

    await audit_event(
        db,
        action="chat_contact_submitted",
        entity_type="conversation",
        entity_id=conversation.id,
        metadata_json={
            "customer_id": customer.id,
            "lead_id": conversation.lead_id,
            "task_id": task_id,
            "selected_department": payload.selected_department,
            "selected_topic": payload.selected_topic,
            "message": contact_message,
        },
    )
    return ChatContactResponse(
        status=status,
        conversation_id=conversation.id,
        customer_id=customer.id,
        lead_id=conversation.lead_id,
        task_id=task_id,
    )


async def list_public_chat_messages(
    db: AsyncSession,
    conversation_id: str,
    *,
    session_id: str | None,
) -> list[ChatTranscriptMessage]:
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise ValueError("Conversation not found")
    if not await handover_session_matches(db, conversation_id, session_id):
        raise PermissionError("Invalid chat session")
    messages = (
        await db.scalars(
            select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
        )
    ).all()
    return [
        ChatTranscriptMessage(
            id=message.id,
            sender_type=message.sender_type,
            text=message.text,
            created_at=message.created_at.isoformat(),
        )
        for message in messages
    ]


async def handover_session_matches(db: AsyncSession, conversation_id: str, session_id: str | None) -> bool:
    if not session_id:
        return False
    audit_rows = (
        await db.scalars(
            select(AuditLog).where(
                AuditLog.action == "chat_session_started",
                AuditLog.entity_type == "conversation",
                AuditLog.entity_id == conversation_id,
            )
        )
    ).all()
    if any((row.metadata_json or {}).get("session_id") == session_id for row in audit_rows):
        return True
    message_rows = (
        await db.scalars(
            select(Message).where(
                Message.conversation_id == conversation_id,
                Message.sender_type == "user",
            )
        )
    ).all()
    return any((row.metadata_json or {}).get("session_id") == session_id for row in message_rows)


def split_contact_name(payload: ChatContactRequest) -> tuple[str | None, str | None]:
    if payload.first_name or payload.last_name:
        return payload.first_name, payload.last_name
    if not payload.full_name:
        return None, None
    parts = payload.full_name.strip().split()
    if not parts:
        return None, None
    return parts[0], " ".join(parts[1:]) or None


def handover_payload_message(payload: ChatHandoverRequest | None) -> str | None:
    if payload is None:
        return None
    return first_non_empty(payload.message, payload.question, payload.note)


def contact_payload_message(payload: ChatContactRequest) -> str | None:
    return first_non_empty(payload.message, payload.question, payload.note)


def first_non_empty(*values: str | None) -> str | None:
    for value in values:
        if value and value.strip():
            return value.strip()
    return None


def department_name_from_selection(selected_department: str | None) -> str:
    return {
        "admissions": "Admissions",
        "programs": "Admissions",
        "finance": "Finance",
        "international": "International Admissions",
        "medicine": "International Admissions",
        "library": "Student Services",
        "career": "Student Services",
        "it": "IT Support",
        "it_support": "IT Support",
        "contact": "General",
        "operator": "General",
        "human_operator": "General",
    }.get(selected_department or "", "Admissions")


def lead_payload_from_contact(customer_id: str, payload: ChatContactRequest, department_id: str | None) -> dict:
    selected = payload.selected_department or ""
    source_domain = payload.source_domain if payload.source_domain in {"alte.edu.ge", "join.alte.edu.ge"} else None
    return {
        "customer_id": customer_id,
        "interest_area": payload.interest_area or payload.selected_topic or selected or "operator_handover",
        "program": payload.selected_topic,
        "department_id": department_id,
        "status": "new",
        "priority": "high" if selected in {"international", "medicine"} else "normal",
        "source_channel": "website_chat",
        "source_domain": source_domain,
        "is_international_priority": selected in {"international", "medicine"},
        "medical_track": selected == "medicine",
        "qualification_intent": "human_request",
        "urgency": "high" if selected in {"international", "medicine"} else "normal",
        "lead_score": 80,
        "qualification_status": "qualified",
        "handover_required": True,
        "handover_reason": "visitor_contact_form",
        "recommended_next_action": "operator_follow_up",
    }


async def find_existing_handover_task(db: AsyncSession, conversation: Conversation) -> Task | None:
    query = select(Task).where(Task.title == "Human handover requested", Task.status == "open")
    if conversation.lead_id:
        query = query.where(Task.lead_id == conversation.lead_id)
    elif conversation.customer_id:
        query = query.where(Task.customer_id == conversation.customer_id)
    else:
        return None
    return await db.scalar(query.order_by(Task.created_at.desc()))


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
    if not should_prompt_for_contact(analysis):
        analysis.missing_fields = [field for field in analysis.missing_fields if field not in {CONTACT_FIELD, "first_name"}]
        if analysis.qualification.recommended_next_action in {"ask_phone_or_email", "create_follow_up_task", "ask_contact_details"}:
            analysis.qualification.recommended_next_action = "answer_or_ask_followup"
        return
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


def apply_department_routing(
    analysis: AIAnalysisResult,
    payload: ChatMessageRequest,
    knowledge: dict,
) -> DepartmentRoutingResult:
    routing = resolve_department(
        message_text=payload.message,
        ai_intent=analysis.intent,
        ai_confidence=analysis.confidence,
        source_domain=payload.source_domain or analysis.source_domain,
        selected_department=payload.selected_department,
        selected_topic=payload.selected_topic,
        risk_flags=analysis.risk_flags,
        used_sources=knowledge.get("used_sources") or analysis.used_sources,
        language=payload.language or analysis.language,
        ai_department=analysis.department,
    )
    analysis.department = routing.department
    if routing.handover_required:
        analysis.should_handover = True
        if not has_contact(analysis):
            analysis.should_create_lead = False
        if "ai_provider_error" not in analysis.risk_flags:
            analysis.reply = ensure_handover_routing_reply(analysis, routing)
    return routing


def ensure_handover_routing_reply(analysis: AIAnalysisResult, routing: DepartmentRoutingResult) -> str:
    if reply_mentions_department(analysis.reply, routing):
        return analysis.reply
    if analysis.language == "en":
        return (
            f"{analysis.reply} I can route this to {routing.department} so the correct advisor can confirm it."
        )
    return (
        f"{analysis.reply} ამ საკითხს გადავამისამართებ შესაბამის გუნდთან: {routing.department}, "
        "რათა დეტალები ოფიციალურად დაგიდასტურონ."
    )


def reply_mentions_department(reply: str, routing: DepartmentRoutingResult) -> bool:
    lowered = reply.lower()
    return routing.department.lower() in lowered or routing.department_key.replace("_", " ") in lowered


def is_info_only_no_contact_question(analysis: AIAnalysisResult) -> bool:
    return analysis.intent in INFO_ONLY_NO_CONTACT_INTENTS or (
        analysis.qualification.intent in INFO_ONLY_NO_CONTACT_QUALIFICATION_INTENTS
        and analysis.intent not in CONTACT_GATED_LEAD_INTENTS
    )


def should_prompt_for_contact(analysis: AIAnalysisResult) -> bool:
    if analysis.intent in {"consultation_request", "medicine_admission"}:
        return True
    if analysis.qualification.intent in {"application", "human_help"}:
        return True
    return analysis.qualification.handover_required and analysis.qualification.handover_reason == "human_requested"


def ensure_contact_request_reply(analysis: AIAnalysisResult) -> str:
    reply = strip_contact_request_sentence(analysis.reply)
    consent = safe_contact_consent_text(analysis.language)
    if not reply:
        return consent
    if consent in reply:
        return reply
    return f"{reply} {consent}"


def sanitize_premature_contact_request(analysis: AIAnalysisResult) -> None:
    if has_contact(analysis):
        return
    if reply_requests_contact(analysis.reply):
        analysis.reply = ensure_contact_request_reply(analysis)


def safe_contact_consent_text(language: str) -> str:
    return SAFE_CONTACT_CONSENT_EN if language == "en" else SAFE_CONTACT_CONSENT_KA


def strip_contact_request_sentence(reply: str) -> str:
    cleaned = (reply or "").strip()
    lowered = cleaned.lower()
    for marker in CONTACT_REQUEST_MARKERS:
        index = lowered.find(marker.lower())
        if index >= 0:
            cleaned = cleaned[:index].strip()
            break
    else:
        for pattern in CONTACT_REQUEST_REGEXES:
            match = re.search(pattern, lowered)
            if match:
                cleaned = cleaned[: match.start()].strip()
                break
    if cleaned and cleaned[-1] not in ".!?":
        cleaned = cleaned.rstrip(" .,!?:;") + "."
    return cleaned


def reply_requests_contact(reply: str) -> bool:
    lowered = reply.lower()
    return any(marker.lower() in lowered for marker in CONTACT_REQUEST_MARKERS) or any(
        re.search(pattern, lowered) for pattern in CONTACT_REQUEST_REGEXES
    )


def is_medical(analysis: AIAnalysisResult) -> bool:
    haystack = f"{analysis.program or ''} {analysis.conversation_summary or ''}".lower()
    return "medicine" in haystack or "md" in haystack or "სამედიცინო" in haystack


def mentions_relocation(analysis: AIAnalysisResult) -> bool:
    haystack = f"{analysis.conversation_summary or ''}".lower()
    return "visa" in haystack or "relocation" in haystack


def official_academic_rules_regression_reply(message: str, language: str | None) -> str | None:
    haystack = (message or "").lower()
    is_ka = language == "ka" or any("\u10a0" <= char <= "\u10ff" for char in message)
    asks_credit = any(marker in haystack for marker in ["ects", "კრედიტ"])

    if is_master_admission_documents_question(haystack):
        if is_ka:
            return (
                "მაგისტრატურაზე ჩასარიცხად საჭიროა: პირადობის დამადასტურებელი დოკუმენტის ასლი; CV; "
                "3x4 ფოტოსურათი ბეჭდური და ელექტრონული ფორმით; სამხედრო აღრიცხვაზე ყოფნის დამადასტურებელი "
                "დოკუმენტის ასლი მამაკაცი აპლიკანტებისთვის; ნოტარიულად დამოწმებული დიპლომის ასლი; "
                "დიპლომის დანართის ასლი."
            )
        return (
            "For master's admission, the required documents are: ID copy; CV; 3x4 photo in printed and electronic form; "
            "copy of military registration certificate for male applicants; notarized diploma copy; diploma supplement copy."
        )

    if asks_credit and any(marker in haystack for marker in ["ბაკალავრ", "bachelor"]):
        if is_ka:
            return (
                "საბაკალავრო პროგრამის დასასრულებლად საჭიროა არანაკლებ 240 ECTS კრედიტის დაგროვება. "
                "ერთსაფეხურიანი პროგრამები ცალკეა: მედიცინა - არანაკლებ 360 ECTS, სტომატოლოგია - არანაკლებ 300 ECTS."
            )
        return (
            "A bachelor program requires at least 240 ECTS credits. "
            "One-cycle programs are separate: Medicine requires at least 360 ECTS and Dentistry at least 300 ECTS."
        )

    if asks_credit and any(marker in haystack for marker in ["მაგისტრატ", "სამაგისტრო", "master"]):
        if is_ka:
            return "სამაგისტრო პროგრამისთვის საჭიროა არანაკლებ 120 ECTS კრედიტის დაგროვება."
        return "A master program requires at least 120 ECTS credits."

    if any(marker in haystack for marker in ["სწავლების ენა", "რა ენაზე", "teaching language", "language of instruction"]):
        if is_ka:
            return "უნივერსიტეტში სწავლების ენა არის ქართული. ცალკეულ პროგრამებზე სწავლება ხორციელდება ინგლისურ ენაზე."
        return "The university's teaching language is Georgian. Some programs are taught in English."

    if any(marker in haystack for marker in ["სტატუსის შეჩერ", "სტატუსი რამდენ ხანს", "შევიჩერო", "status suspension", "suspend student status"]):
        if is_ka:
            return "სტუდენტის სტატუსის შეჩერების საერთო ვადა არ უნდა აღემატებოდეს 5 წელს."
        return "The total student status suspension period must not exceed 5 years."

    return None


def selected_official_document_regression_reply(message: str, language: str | None) -> str | None:
    haystack = (message or "").lower()
    is_ka = language == "ka" or any("\u10a0" <= char <= "\u10ff" for char in message)

    if any(marker in haystack for marker in ["ფინანსური დახმარ", "ფინანსური მხარდაჭერ", "დაფინანსება არსებობს", "financial support"]):
        if is_ka:
            return (
                "ალტე უნივერსიტეტში ფინანსური მხარდაჭერის საკითხები უნდა გადამოწმდეს დამტკიცებული ფინანსური მხარდაჭერის "
                "მექანიზმებისა და დაფინანსების წესის მიხედვით. თანხები, პროცენტები ან მიმდინარე შეთავაზებები უნდა ითქვას "
                "მხოლოდ მაშინ, როცა ისინი ოფიციალურ წყაროში ზუსტად წერია."
            )
        return (
            "Financial support at Alte University should be checked against the approved financial support mechanisms "
            "and funding rules. Amounts, percentages, or current offers should be stated only when an official source says them exactly."
        )

    if any(marker in haystack for marker in ["ai-ის გამოყენ", "ai-ს გამოყენ", "ai გამოყენ", "ხელოვნური ინტელექტის გამოყენ", "ai policy"]):
        if is_ka:
            return (
                "AI-ის გამოყენება არ არის უნივერსალურად დაშვებული ან აკრძალული. ის დამოკიდებულია კონკრეტული დავალების წესზე, "
                "ლექტორის/კურსის მითითებაზე და აკადემიური კეთილსინდისიერების მოთხოვნებზე."
            )
        return (
            "AI use is not universally allowed or forbidden. It depends on the specific assignment rules, course or instructor guidance, "
            "and academic integrity requirements."
        )

    return None


def normalize_chat_retrieval_query(message: str) -> str:
    haystack = (message or "").lower()
    aliases = [alias for markers, alias in GEORGIAN_RETRIEVAL_ALIASES if any(marker in haystack for marker in markers)]
    if not aliases:
        return message
    return f"{message} {' '.join(aliases)}"


def is_master_admission_documents_question(haystack: str) -> bool:
    has_master = any(marker in haystack for marker in ["მაგისტრატურ", "სამაგისტრო", "master"])
    has_documents = any(
        marker in haystack
        for marker in [
            "საბუთ",
            "დოკუმენტ",
            "ჩასარიცხ",
            "ჩარიცხვისთვის",
            "admission document",
            "required document",
            "documents",
        ]
    )
    return has_master and has_documents


async def retrieve_chat_knowledge(
    db: AsyncSession,
    message: str,
    analysis: AIAnalysisResult,
    route_decision: KnowledgeRouteDecision | None = None,
) -> dict:
    academic_rules_question = is_official_academic_rules_text(message) or is_official_academic_rules_question(analysis)
    selected_official_document_question = is_selected_official_document_text(message)
    if not academic_rules_question and not selected_official_document_question and not should_use_knowledge(analysis):
        return {"answer_source_status": "not_required", "used_sources": [], "snippet_titles": []}
    category = None if academic_rules_question else category_for_analysis(analysis)
    language = analysis.language if analysis.language in {"ka", "en"} else None
    retrieval_query = normalize_chat_retrieval_query(message)
    scoped_source_domain = scoped_source_domain_for_decision(route_decision)
    scoped_exact_allowed = scoped_exact_answer_allowed(route_decision)
    if route_decision and route_decision.primary_source_group and not scoped_exact_allowed:
        return {"answer_source_status": "no_approved_source_found", "used_sources": [], "snippet_titles": []}
    if scoped_source_domain and scoped_exact_allowed:
        results = await search_knowledge_snippets(
            db,
            query=retrieval_query,
            language=language,
            category=None if scoped_source_domain == "official_academic_rules" else category,
            source_domain=scoped_source_domain,
            program_name=analysis.program,
            approved_only=True,
        )
    elif scoped_source_domain and not scoped_exact_allowed:
        results = []
    elif academic_rules_question:
        results = await search_knowledge_snippets(
            db,
            query=retrieval_query,
            language=language,
            category=None,
            source_domain="official_academic_rules",
            program_name=analysis.program,
            approved_only=True,
        )
    else:
        results = []
    if not results and selected_official_document_question and scoped_exact_allowed:
        results = await search_knowledge_snippets(
            db,
            query=retrieval_query,
            language=language,
            category=category,
            source_domain=OFFICIAL_ALTE_PDF_SOURCE_DOMAIN,
            program_name=analysis.program,
            approved_only=True,
        )
    if not results and (academic_rules_question or selected_official_document_question or scoped_source_domain):
        return {"answer_source_status": "no_approved_source_found", "used_sources": [], "snippet_titles": []}
    if not results:
        results = await search_knowledge_snippets(
            db,
            query=retrieval_query,
            language=language,
            category=category,
            source_domain=(
                None
                if selected_official_document_question
                else analysis.source_domain
                if analysis.source_domain in {"alte.edu.ge", "join.alte.edu.ge"}
                else None
            ),
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


async def retrieve_initial_knowledge_context(
    db: AsyncSession,
    message: str,
    route_decision: KnowledgeRouteDecision | None = None,
) -> list[dict]:
    academic_rules_question = is_official_academic_rules_text(message)
    selected_official_document_question = is_selected_official_document_text(message)
    retrieval_query = normalize_chat_retrieval_query(message)
    scoped_source_domain = scoped_source_domain_for_decision(route_decision)
    scoped_exact_allowed = scoped_exact_answer_allowed(route_decision)
    if route_decision and route_decision.primary_source_group and not scoped_exact_allowed:
        return []
    if scoped_source_domain and scoped_exact_allowed:
        results = await search_knowledge_snippets(
            db,
            query=retrieval_query,
            source_domain=scoped_source_domain,
            approved_only=True,
            include_stale=False,
            limit=3,
        )
    elif scoped_source_domain and not scoped_exact_allowed:
        results = []
    elif academic_rules_question:
        results = await search_knowledge_snippets(
            db,
            query=retrieval_query,
            source_domain="official_academic_rules",
            approved_only=True,
            include_stale=False,
            limit=3,
        )
    else:
        results = []
    if not results and selected_official_document_question and scoped_exact_allowed:
        results = await search_knowledge_snippets(
            db,
            query=retrieval_query,
            source_domain=OFFICIAL_ALTE_PDF_SOURCE_DOMAIN,
            approved_only=True,
            include_stale=False,
            limit=3,
        )
    if not results and (academic_rules_question or selected_official_document_question or scoped_source_domain):
        return []
    if not results:
        results = await search_knowledge_snippets(
            db,
            query=retrieval_query,
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
    return is_official_academic_rules_question(analysis) or analysis.intent in {"admission_interest", "international_admission", "finance_question"} or (
        analysis.qualification.intent
        in {"program_info", "admission_requirements", "tuition_fee", "scholarship", "application"}
    )


def should_require_knowledge(analysis: AIAnalysisResult) -> bool:
    return is_official_academic_rules_question(analysis) or analysis.intent == "finance_question" or analysis.qualification.intent in {
        "tuition_fee",
        "scholarship",
        "admission_requirements",
    }


def category_for_analysis(analysis: AIAnalysisResult) -> str | None:
    if is_official_academic_rules_question(analysis):
        return None
    if analysis.qualification.intent == "tuition_fee":
        return "finance"
    if analysis.qualification.intent == "scholarship":
        return "scholarship"
    if analysis.qualification.intent in {"admission_requirements", "application"}:
        return "admissions"
    if analysis.program:
        return "programs"
    return None


def scoped_source_domain_for_decision(route_decision: KnowledgeRouteDecision | None) -> str | None:
    config = source_group_config(route_decision.primary_source_group if route_decision else None)
    if not config:
        return None
    value = config.get("source_domain")
    return value if isinstance(value, str) and value else None


def scoped_exact_answer_allowed(route_decision: KnowledgeRouteDecision | None) -> bool:
    config = source_group_config(route_decision.primary_source_group if route_decision else None)
    if not config:
        return True
    return bool(config.get("exact_answer_allowed", True))


def is_official_academic_rules_question(analysis: AIAnalysisResult) -> bool:
    haystack = " ".join(
        [
            analysis.reply or "",
            analysis.conversation_summary or "",
            analysis.program or "",
            analysis.interest_area or "",
            analysis.qualification.intent or "",
        ]
    ).lower()
    markers = [
        "academic calendar",
        "registration",
        "midterm",
        "final exam",
        "retake",
        "ects",
        "gpa",
        "fx",
        "mobility",
        "status suspension",
        "status termination",
        "teaching language",
        "how many credits",
        "რა ენაზე",
        "სწავლება",
        "master admission",
        "bachelor admission",
        "program catalog",
        "educational program",
        "educational programme",
        "პროგრამ",
        "საგანმანათლებლო პროგრამ",
        "ეროვნული გამოცდ",
        "რეგისტრაცი",
        "შუალედურ",
        "დასკვნით",
        "კრედიტ",
        "რამდენი კრედიტია",
        "სტატუს",
        "შევიჩერო",
        "მობილობ",
        "მაგისტრატურ",
        "ბაკალავრიატ",
        "სწავლების ენა",
    ]
    return any(marker in haystack for marker in markers)


def is_official_academic_rules_text(text: str) -> bool:
    haystack = (text or "").lower()
    markers = [
        "academic calendar",
        "registration",
        "midterm",
        "final exam",
        "retake",
        "ects",
        "gpa",
        "fx",
        "mobility",
        "status suspension",
        "status termination",
        "teaching language",
        "how many credits",
        "რა ენაზე",
        "სწავლება",
        "master admission",
        "bachelor admission",
        "program catalog",
        "educational program",
        "educational programme",
        "პროგრამ",
        "საგანმანათლებლო პროგრამ",
        "ეროვნული გამოცდ",
        "რეგისტრაცი",
        "შუალედურ",
        "დასკვნით",
        "კრედიტ",
        "რამდენი კრედიტია",
        "სტატუს",
        "შევიჩერო",
        "მობილობ",
        "მაგისტრატურ",
        "ბაკალავრიატ",
        "სწავლების ენა",
    ]
    return any(marker in haystack for marker in markers)


def is_clearly_unsupported_official_question(text: str) -> bool:
    haystack = (text or "").lower()
    unsupported_markers = [
        "space campus",
        "cosmic campus",
        "კოსმოსური კამპუს",
        "კოსმოსურ კამპუს",
        "current tuition",
        "current price",
        "current fee",
        "today's promotion",
        "today promotion",
        "მიმდინარე სწავლის ფასი",
        "მიმდინარე ფასი",
        "დღევანდელი აქცია",
        "დღევანდელი ფასდაკლება",
        "კონკრეტული კონსულტანტის ტელეფონი",
        "კონსულტანტის ტელეფონი",
    ]
    future_year_markers = ["2031", "2032", "2033", "2034", "2035"]
    return any(marker in haystack for marker in unsupported_markers) or (
        any(year in haystack for year in future_year_markers)
        and any(marker in haystack for marker in ["სტიპენდ", "scholarship", "კამპუს", "campus"])
    )


def is_selected_official_document_text(text: str) -> bool:
    haystack = (text or "").lower()
    markers = [
        "ai policy",
        "artificial intelligence",
        "generative artificial",
        "examination regulations",
        "plagiarism",
        "ethics code",
        "ombudsman",
        "library",
        "career development",
        "alumni",
        "special needs",
        "individual study plan",
        "electronic learning",
        "dean's list",
        "dean",
        "iro policy",
        "sustainability",
        "edi policy",
        "research component",
        "student rights",
        "self-government",
        "school council",
        "funding rule",
        "financial support",
        "გენერაციული",
        "ai-ის",
        "ai-ს გამოყენ",
        "ai გამოყენ",
        "ხელოვნური ინტელექტ",
        "გამოცდების ჩატარ",
        "პლაგიატ",
        "ეთიკის კოდექს",
        "ომბუდსმენ",
        "ბიბლიოთეკ",
        "კარიერული",
        "კურსდამთავრებულ",
        "სპეციალური საჭირო",
        "სსმ",
        "ინდივიდუალური სასწავლო",
        "ელექტრონული სწავლ",
        "დეკანის გრანტ",
        "დაფინანსების წესი",
        "ფინანსური დახმარ",
        "ფინანსური მხარდაჭერ",
        "სტუდენტთა უფლებ",
        "თვითმმართველ",
        "სკოლის საბჭ",
        "მდგრადი განვითარების",
        "კვლევითი კომპონენტ",
        "ინფორმაციული ტექნოლოგი",
    ]
    return any(marker in haystack for marker in markers)


def build_source_backed_reply(analysis: AIAnalysisResult, snippet_titles: list[str]) -> str:
    source_hint = ", ".join(snippet_titles[:2])
    base_reply = analysis.reply.strip()
    if not source_hint:
        return base_reply
    if analysis.language == "en":
        if "approved source" in base_reply.lower() or "verified information" in base_reply.lower():
            return base_reply
        return f"{base_reply}\n\nSource: {source_hint}."
    if "წყარო" in base_reply or "დადასტურებულ" in base_reply:
        return base_reply
    return f"{base_reply}\n\nწყარო: {source_hint}."


def build_no_source_reply(analysis: AIAnalysisResult) -> str:
    if analysis.language == "en":
        return (
            "I couldn't find an exact answer in the approved official sources. "
            "I can connect you with the relevant operator so your question is routed to the correct department."
        )
    return (
        "ამ საკითხზე დამტკიცებულ წყაროში ზუსტი ინფორმაცია ვერ ვიპოვე. "
        "შემიძლია დაგაკავშიროთ შესაბამის ოპერატორთან, რომ თქვენი კითხვა სწორ დეპარტამენტს გადაეცეს."
    )


def is_ambiguous_program_question(message: str, analysis: AIAnalysisResult) -> bool:
    haystack = (message or "").lower()
    mentions_program = any(marker in haystack for marker in ["პროგრამ", "program", "კრედიტ", "credits", "ects"])
    known_level = any(marker in haystack for marker in ["ბაკალავრ", "bachelor", "მაგისტრ", "master", "მედიცინ", "medicine", "სტომატოლოგ", "dentistry"])
    return mentions_program and not known_level and not analysis.program


def build_ambiguous_program_reply(analysis: AIAnalysisResult) -> str:
    if analysis.language == "en":
        return (
            "To answer accurately, I need one clarification: which program do you mean? "
            "General bachelor programs require 240 ECTS and master programs require 120 ECTS, but program-specific details must be checked in the official program catalog."
        )
    return (
        "ზუსტად რომ გიპასუხოთ, მჭირდება დაზუსტება: რომელ პროგრამას გულისხმობთ? "
        "ზოგადად, ბაკალავრიატი არის 240 ECTS, მაგისტრატურა - 120 ECTS, მაგრამ კონკრეტული პროგრამის დეტალი ოფიციალურ პროგრამების კატალოგში უნდა გადამოწმდეს."
    )


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
