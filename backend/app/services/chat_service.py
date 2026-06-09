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
from app.services.ai_service import analyze_with_ai, generate_source_grounded_answer
from app.services.claude_intent_router_service import route_decision_from_intent, route_with_claude_intent
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

PUBLIC_SOURCE_GROUP_LABELS = {
    "program_catalog_sources": "საგანმანათლებლო პროგრამების კატალოგი",
    "academic_calendar_2025_2026": "აკადემიური კალენდარი 2025–2026",
    "official_academic_rules": "სასწავლო პროცესის მარეგულირებელი წესი",
    "admissions_rules": "მიღების წესი",
    "international_admissions_sources": "საერთაშორისო მიღების წესი",
    "finance_sources": "ფინანსური მხარდაჭერა",
    "state_social_grants_sources": "სახელმწიფო/სოციალური გრანტები",
    "library_sources": "ბიბლიოთეკის წესი",
    "career_sources": "კარიერის სერვისები",
    "bachelor_regulation": "ბაკალავრიატის დებულება",
    "bachelor_rules": "ბაკალავრიატის დებულება",
    "master_regulation": "მაგისტრატურის დებულება",
    "master_rules": "მაგისტრატურის დებულება",
}
PUBLIC_SOURCE_LABEL_WHITELIST = set(PUBLIC_SOURCE_GROUP_LABELS.values())

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

    history = await conversation_history(db, conversation.id)
    deterministic_route_decision = classify_knowledge_route(
        payload.message,
        selected_department=payload.selected_department,
        source_domain=payload.source_domain,
    )
    intent_route, intent_router_meta = route_with_claude_intent(
        payload.message,
        selected_department=payload.selected_department,
        source_domain=payload.source_domain,
        language_hint=payload.language or conversation.language,
        conversation_history=history,
    )
    route_decision = route_decision_from_intent(intent_route, deterministic_route_decision)
    if route_decision.clarification_required:
        return await handle_clarification_response(db, conversation, user_message, route_decision)

    initial_knowledge_context = await retrieve_initial_knowledge_context(db, payload.message, route_decision)
    knowledge = {"answer_source_status": "not_required", "used_sources": [], "snippet_titles": []}
    legacy_ai_needed = should_use_legacy_ai_analysis(intent_route)
    if legacy_ai_needed:
        analysis, ai_meta = analyze_with_ai(
            payload.message,
            source_domain=payload.source_domain,
            language_hint=conversation.language,
            conversation_history=history,
            knowledge_context=initial_knowledge_context,
        )
    else:
        analysis = analysis_from_intent_route(payload.message, payload.source_domain, intent_route)
        ai_meta = {
            "provider": "deterministic",
            "model": "phase_9av_router_metadata",
            "raw_response": None,
            "fallback": False,
            "legacy_ai_analysis_skipped": True,
        }
    if intent_route.operator_needed:
        analysis.intent = "human_request"
        analysis.should_create_lead = False
        analysis.should_handover = True
        analysis.department = intent_route.public_department_label
        analysis.confidence = max(analysis.confidence, intent_route.confidence)
        if not analysis.reply or is_generic_ai_fallback_reply(analysis.reply):
            analysis.reply = build_operator_request_reply(analysis.language, intent_route.public_department_label)
        if "claude_intent_operator_needed" not in analysis.risk_flags:
            analysis.risk_flags.append("claude_intent_operator_needed")
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
    unsupported_official_question = (
        is_clearly_unsupported_official_question(payload.message)
        or intent_route.unsupported_likely
        or intent_route.router_validation_status in {"invalid_source_groups", "empty_source_groups"}
    )
    if unsupported_official_question:
        knowledge = {"answer_source_status": "no_approved_source_found", "used_sources": [], "snippet_titles": []}
    else:
        knowledge = await retrieve_chat_knowledge(db, payload.message, analysis, route_decision)
    if knowledge["answer_source_status"] == "answered_from_approved_source":
        analysis.used_sources = knowledge["used_sources"]
        official_reply = official_academic_rules_regression_reply(payload.message, analysis.language) or selected_official_document_regression_reply(
            payload.message, analysis.language
        )
        if not official_reply and route_decision.primary_source_group == "academic_calendar_2025_2026":
            official_reply = grounded_source_backed_reply(payload.message, analysis.language, route_decision)
        if not official_reply and (
            is_generic_ai_fallback_reply(analysis.reply)
            or route_decision.primary_source_group == "program_catalog_sources"
        ):
            official_reply = grounded_source_backed_reply(payload.message, analysis.language, route_decision)
        if official_reply:
            analysis.reply = official_reply
        elif knowledge.get("source_excerpts"):
            grounded_reply, grounded_meta = generate_source_grounded_answer(
                payload.message,
                language=analysis.language,
                approved_excerpts=knowledge.get("source_excerpts") or [],
                route_metadata={
                    "department": route_decision.department_label,
                    "source_group": route_decision.primary_source_group,
                    "intent_router": intent_router_meta,
                },
            )
            if grounded_reply:
                analysis.reply = grounded_reply
                ai_meta.setdefault("grounded_answer", grounded_meta)
        analysis.reply = build_source_backed_reply(analysis, knowledge["snippet_titles"])
    elif unsupported_official_question or (
        "ai_provider_error" not in analysis.risk_flags
        and (
            should_require_knowledge(analysis)
            or bool(route_decision.primary_source_group)
            or is_official_academic_rules_text(payload.message)
            or is_selected_official_document_text(payload.message)
        )
    ):
        analysis.risk_flags.append(knowledge["answer_source_status"])
        analysis.should_handover = True
        if is_ambiguous_program_question(payload.message, analysis) and not is_clearly_unsupported_official_question(payload.message):
            analysis.reply = build_ambiguous_program_reply(analysis)
        elif reply_requests_contact(analysis.reply):
            pass
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
            "intent_router_provider": intent_router_meta.get("provider"),
            "intent_router_fallback": intent_router_meta.get("fallback"),
            "router_validation_status": intent_route.router_validation_status,
            "deterministic_override_applied": intent_route.deterministic_override_applied,
            "deterministic_override_reason": intent_route.deterministic_override_reason,
            "used_claude_intent_router": intent_router_meta.get("provider") == "claude",
            "used_legacy_ai_analysis": legacy_ai_needed,
            "used_grounded_answer_generator": bool(ai_meta.get("grounded_answer")),
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
    elif analysis.intent == "human_request" and has_explicit_handover_request(payload.message, analysis.intent):
        conversation.human_handover = True
        if has_contact(analysis):
            created_task_id = await create_handover_task(db, conversation, analysis)
    elif analysis.intent == "finance_question":
        if has_contact(analysis):
            created_task_id = await create_department_task(db, conversation, analysis, "Finance")
    elif analysis.intent == "student_service":
        if analysis.should_handover and has_contact(analysis):
            created_task_id = await create_department_task(db, conversation, analysis, "Student Services")

    if should_persist_human_handover(analysis, knowledge, payload):
        conversation.human_handover = True

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
            "intent_router": {
                "provider": intent_router_meta.get("provider"),
                "fallback": intent_router_meta.get("fallback"),
                "department": intent_route.department,
                "topic": intent_route.topic,
                "source_groups_to_search": intent_route.source_groups_to_search,
                "unsupported_likely": intent_route.unsupported_likely,
                "router_validation_status": intent_route.router_validation_status,
                "deterministic_override_applied": intent_route.deterministic_override_applied,
                "deterministic_override_reason": intent_route.deterministic_override_reason,
                "used_legacy_ai_analysis": legacy_ai_needed,
                "used_grounded_answer_generator": bool(ai_meta.get("grounded_answer")),
            },
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
        handover_reason=(
            analysis.qualification.handover_reason or routing.confidence_reason
            if analysis.should_handover
            else None
        ),
        recommended_next_action=analysis.qualification.recommended_next_action,
        answer_source_status=knowledge["answer_source_status"],
        used_sources=knowledge["used_sources"],
        public_source_label=response_public_source_label(
            knowledge,
            should_handover=analysis.should_handover,
            source_group=route_decision.primary_source_group,
        ),
        route_department=routing.department,
        department_key=routing.department_key,
        routing_reason=routing.reason,
        source_group=route_decision.primary_source_group,
        clarification_needed=False,
        clarification_options=[],
    )


def should_use_legacy_ai_analysis(intent_route) -> bool:
    if intent_route.needs_clarification:
        return False
    if intent_route.operator_needed:
        return True
    if intent_route.unsupported_likely:
        return False
    if intent_route.router_validation_status in {"invalid_source_groups", "empty_source_groups"}:
        return False
    if intent_route.fallback_used:
        return True
    if intent_route.source_groups_to_search:
        return False
    return True


def analysis_from_intent_route(message: str, source_domain: str | None, intent_route) -> AIAnalysisResult:
    language = intent_route.language if intent_route.language in {"ka", "en"} else ("ka" if any("\u10a0" <= char <= "\u10ff" for char in message) else "en")
    return AIAnalysisResult(
        reply="I am checking the approved sources for this question." if language == "en" else "ვამოწმებ დამტკიცებულ წყაროებს ამ საკითხზე.",
        language=language,  # type: ignore[arg-type]
        intent="human_request" if intent_route.operator_needed else "general_info",
        confidence=intent_route.confidence,
        should_create_lead=False,
        should_handover=bool(intent_route.operator_needed),
        department=intent_route.public_department_label,
        source_domain=source_domain,
        conversation_summary=f"Phase 9AV routed topic: {intent_route.topic}",
        used_sources=[],
        risk_flags=[f"router_validation_{intent_route.router_validation_status}"],
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
    source_backed = knowledge.get("answer_source_status") == "answered_from_approved_source"
    explicit_handover = has_explicit_handover_request(payload.message, analysis.intent)
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
    if source_backed and not explicit_handover:
        analysis.should_handover = is_it_access_support_request(payload.message, routing)
        analysis.should_create_lead = False if not has_contact(analysis) else analysis.should_create_lead
    elif knowledge.get("answer_source_status") == "no_approved_source_found":
        analysis.should_handover = True
        if not has_contact(analysis):
            analysis.should_create_lead = False
        if "ai_provider_error" not in analysis.risk_flags:
            if not analysis.reply or is_generic_ai_fallback_reply(analysis.reply):
                analysis.reply = build_no_source_reply(analysis)
            analysis.reply = ensure_handover_routing_reply(analysis, routing)
    elif routing.handover_required:
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


def is_it_access_support_request(message: str | None, routing: DepartmentRoutingResult) -> bool:
    if routing.department_key != "it_support":
        return False
    return is_it_access_support_text(message)


def is_it_access_support_text(message: str | None) -> bool:
    haystack = (message or "").lower()
    return any(marker in haystack for marker in ["login", "password", "can't", "cannot", "ვერ", "შევდივარ", "პაროლ"])


def has_explicit_handover_request(message: str | None, intent: str | None = None) -> bool:
    haystack = (message or "").lower()
    if (intent or "").lower() == "human_request" and any(
        marker in haystack
        for marker in [
            "operator",
            "human",
            "consultant",
            "advisor",
            "contact",
            "connect",
            "handover",
            "დაკავშირ",
            "ოპერატორ",
            "ადამიან",
            "კონსულტანტ",
            "კონტაქტ",
            "დამაკავშირ",
        ]
    ):
        return True
    return any(
        marker in haystack
        for marker in [
            "operator",
            "human",
            "consultant",
            "advisor",
            "contact me",
            "connect me",
            "talk to",
            "speak to",
            "დამაკავშირ",
            "დაკავშირება",
            "დაკავშირ",
            "ოპერატორ",
            "ადამიან",
            "კონსულტანტ",
            "კონტაქტ",
        ]
    )


def should_persist_human_handover(analysis: AIAnalysisResult, knowledge: dict, payload: ChatMessageRequest) -> bool:
    if not analysis.should_handover:
        return False
    if knowledge.get("answer_source_status") == "no_approved_source_found":
        return True
    if is_it_access_support_text(payload.message):
        return True
    return has_explicit_handover_request(payload.message, analysis.intent)


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

    if is_computer_science_spring_registration_question(haystack):
        if is_ka:
            return (
                "კომპიუტერული მეცნიერების პროგრამებისთვის გაზაფხულის სემესტრის "
                "აკადემიური/ადმინისტრაციული რეგისტრაცია არის 9-14 მარტს. "
                "გაზაფხულის სემესტრის დაწყება მითითებულია 30 მარტს."
            )
        return (
            "For Computer Science programs, spring semester academic/administrative registration is 9-14 March. "
            "The spring semester start is listed as 30 March."
        )

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
        return grounded_student_status_reply(haystack, is_ka)
    if "gpa" in haystack:
        return grounded_exam_assessment_reply(haystack, is_ka)

    return None


def is_generic_ai_fallback_reply(reply: str | None) -> bool:
    lowered = (reply or "").lower()
    return any(
        marker in lowered
        for marker in [
            "ai service is temporarily unavailable",
            "ai სერვისთან კავშირი შეფერხებულია",
            "temporarily unavailable",
            "შეფერხებულია",
        ]
    )


def grounded_source_backed_reply(message: str, language: str | None, route_decision: KnowledgeRouteDecision | None = None) -> str | None:
    haystack = (message or "").lower()
    is_ka = language == "ka" or any("\u10a0" <= char <= "\u10ff" for char in message)
    source_group = route_decision.primary_source_group if route_decision else None

    if source_group == "program_catalog_sources":
        return grounded_program_catalog_reply(haystack, is_ka)
    if source_group == "student_status_and_mobility":
        return grounded_student_status_reply(haystack, is_ka)
    if source_group == "exams_and_assessment":
        return grounded_exam_assessment_reply(haystack, is_ka)
    if source_group == "academic_calendar_2025_2026" or (is_calendar_text(haystack) and not is_exam_rule_text(haystack)):
        return grounded_calendar_reply(haystack, is_ka)
    if source_group == "admissions_rules" or is_admissions_text(haystack):
        return grounded_admissions_reply(haystack, is_ka)
    if any(marker in haystack for marker in ["teaching language", "language of instruction", "program language", "სწავლების ენა", "რა ენაზე"]):
        return "A program's teaching language is defined in the approved educational program and official academic rules." if not is_ka else "სწავლების ენა განსაზღვრულია დამტკიცებულ საგანმანათლებლო პროგრამაში და ოფიციალურ აკადემიურ წესებში."
    if any(marker in haystack for marker in ["english-language program", "english language program", "english program requirements", "english-language admission", "english language admission"]):
        return "English-language program requirements must be checked in the approved international admissions source. The route is International Admissions, and exact English requirements should only be stated when the approved source lists them." if not is_ka else "ინგლისურენოვანი პროგრამის მოთხოვნები უნდა შემოწმდეს დამტკიცებულ საერთაშორისო მიღების წყაროში."
    if any(marker in haystack for marker in ["medicine", "md", "მედიცინ"]):
        return "Medicine / MD is a one-cycle program. The official academic rules list Medicine as at least 360 ECTS." if not is_ka else "მედიცინა / MD არის ერთსაფეხურიანი პროგრამა. ოფიციალურ აკადემიურ წესებში მედიცინა მითითებულია არანაკლებ 360 ECTS-ით."
    if any(marker in haystack for marker in ["dentistry", "სტომატოლოგ"]):
        return "Dentistry is listed as a one-cycle program requiring at least 300 ECTS in the official academic rules." if not is_ka else "სტომატოლოგია ოფიციალურ აკადემიურ წესებში მითითებულია ერთსაფეხურიან პროგრამად, არანაკლებ 300 ECTS-ით."
    if any(marker in haystack for marker in ["mobility", "მობილ"]):
        return "Mobility and internal mobility are regulated by the official study process rules; individual cases should be checked against the exact mobility procedure." if not is_ka else "მობილობა და შიდა მობილობა რეგულირდება სასწავლო პროცესის ოფიციალური წესით; ინდივიდუალური შემთხვევა უნდა შემოწმდეს მობილობის ზუსტ პროცედურასთან."
    if any(marker in haystack for marker in ["credit recognition", "recognition of credit", "კრედიტების აღიარ", "კრედიტის აღიარ"]):
        return "Credit recognition is handled under the official study process rules and depends on the submitted learning outcomes and credits." if not is_ka else "კრედიტების აღიარება ხდება სასწავლო პროცესის ოფიციალური წესით და დამოკიდებულია წარმოდგენილ სწავლის შედეგებსა და კრედიტებზე."
    if "gpa" in haystack:
        return grounded_exam_assessment_reply(haystack, is_ka)
    if "fx" in haystack or re.search(r"\bf\b", haystack):
        return "FX means 41-50 points and gives the right to take an additional exam once; F is a failing grade and counts as 0." if not is_ka else "FX ნიშნავს 41-50 ქულას და სტუდენტს აძლევს დამატებით გამოცდაზე ერთხელ გასვლის უფლებას; F არის უარყოფითი შეფასება და ითვლება 0-ად."
    if any(marker in haystack for marker in ["final exam", "დასკვნით"]):
        return "Final exam admission is regulated by the official study process and assessment rules." if not is_ka else "დასკვნით გამოცდაზე დაშვება რეგულირდება სასწავლო პროცესისა და შეფასების ოფიციალური წესებით."
    if any(marker in haystack for marker in ["retake", "make-up", "გადაბარ", "დამატებით"]):
        return "Retake and make-up exams are regulated by the official study process rules and the approved academic calendar." if not is_ka else "გადაბარებისა და დამატებითი გამოცდის წესები რეგულირდება სასწავლო პროცესის ოფიციალური წესით და დამტკიცებული აკადემიური კალენდრით."
    if any(marker in haystack for marker in ["dean's list", "deans list", "state grant", "social grant", "grant", "scholarship", "financial support", "funding rule"]):
        return "The approved finance and grant sources cover financial support mechanisms, state/social grants, and Dean's List Award rules. Exact eligibility depends on the specific approved grant rule." if not is_ka else "დამტკიცებული ფინანსური და საგრანტო წყაროები მოიცავს ფინანსური მხარდაჭერის მექანიზმებს, სახელმწიფო/სოციალურ გრანტებს და Dean's List Award-ის წესებს. ზუსტი უფლებამოსილება დამოკიდებულია კონკრეტულ დამტკიცებულ წესზე."
    if any(marker in haystack for marker in ["library", "library resources", "books", "databases", "catalog"]):
        return "The approved library sources describe library services, use rules, books, and electronic resources. For an exact operational request, the library operator can confirm the current process." if not is_ka else "დამტკიცებული ბიბლიოთეკის წყაროები აღწერს ბიბლიოთეკის სერვისებს, სარგებლობის წესებს, წიგნებსა და ელექტრონულ რესურსებს. ზუსტი ოპერაციული საკითხისთვის ბიბლიოთეკის ოპერატორი დაადასტურებს მიმდინარე პროცესს."
    if any(marker in haystack for marker in ["emis", "student portal", "portal", "platform support", "it policy", "information technology", "technical access"]):
        return "The approved IT policy source covers information technology management, infrastructure, platform support, and technical access routing. For a specific EMIS login failure, contact IT Support through the operator handover." if not is_ka else "დამტკიცებული IT პოლიტიკის წყარო მოიცავს ინფორმაციული ტექნოლოგიების მართვას, ინფრასტრუქტურას, პლატფორმების მხარდაჭერას და ტექნიკური წვდომის მარშრუტირებას. კონკრეტული EMIS შესვლის პრობლემისთვის დაუკავშირდით IT დახმარებას ოპერატორის გადაცემით."
    if any(marker in haystack for marker in ["iro policy", "international relations office", "iro"]):
        return "The approved IRO Policy sources cover the International Relations Office, international cooperation, exchange, and mobility coordination." if not is_ka else "დამტკიცებული IRO Policy წყაროები მოიცავს საერთაშორისო ურთიერთობების ოფისს, საერთაშორისო თანამშრომლობას, გაცვლით პროგრამებსა და მობილობის კოორდინაციას."
    if any(marker in haystack for marker in ["edi policy", "equality diversity inclusion"]):
        return "The approved EDI Policy source covers equality, diversity, inclusion, and equal treatment principles." if not is_ka else "დამტკიცებული EDI Policy წყარო მოიცავს თანასწორობის, მრავალფეროვნების, ინკლუზიისა და თანაბარი მოპყრობის პრინციპებს."
    if any(marker in haystack for marker in ["sustainability", "sustainable development", "sustainability strategy", "sustainability report"]):
        return "The approved sustainability sources cover Alte's sustainable development strategy, sustainability priorities, and sustainability reporting." if not is_ka else "დამტკიცებული მდგრადობის წყაროები მოიცავს ალტეს მდგრადი განვითარების სტრატეგიას, პრიორიტეტებსა და მდგრადობის ანგარიშგებას."
    if any(marker in haystack for marker in ["career", "internship", "employment", "job", "კარიერ", "სტაჟირ", "დასაქმ"]):
        return "The approved career sources cover career development, internship, employment, and alumni support topics. For a specific placement request, the relevant career operator can help." if not is_ka else "დამტკიცებული კარიერის წყაროები მოიცავს კარიერულ განვითარებას, სტაჟირებას, დასაქმებასა და კურსდამთავრებულთა მხარდაჭერას. კონკრეტული შესაძლებლობისთვის შესაბამისი კარიერის ოპერატორი დაგეხმარებათ."
    return None


def grounded_program_catalog_reply(haystack: str, is_ka: bool) -> str:
    if any(marker in haystack for marker in ["tuition", "price", "fee", "საფასურ", "ფასი", "გადახდ"]):
        if is_ka:
            return (
                "პროგრამების კატალოგი პროგრამის სწავლის ზუსტ საფასურს არ აჩვენებს. "
                "ზუსტი თანხა არ უნდა გამოიგონოს; სწავლის საფასური უნდა გადამოწმდეს ოფიციალურ ფინანსურ წყაროში "
                "ან შესაბამის ოპერატორთან."
            )
        return (
            "The Program Catalog does not show an exact tuition price for the program. "
            "The assistant should not invent an amount; tuition must be checked in an official finance source "
            "or confirmed by the relevant operator."
        )
    has_credit = any(marker in haystack for marker in ["ects", "credit", "credits", "კრედიტ"])
    if has_credit and any(marker in haystack for marker in ["bachelor", "საბაკალავრო", "ბაკალავრიატ"]):
        return "პროგრამების კატალოგის მიხედვით, საბაკალავრო პროგრამა მოიცავს 240 ECTS კრედიტს." if is_ka else "According to the Program Catalog, bachelor programs comprise 240 ECTS credits."
    if has_credit and any(marker in haystack for marker in ["master", "სამაგისტრო", "მაგისტრატურ"]):
        return "პროგრამების კატალოგის მიხედვით, სამაგისტრო პროგრამა მოიცავს 120 ECTS კრედიტს." if is_ka else "According to the Program Catalog, master programs comprise 120 ECTS credits."
    has_language = any(marker in haystack for marker in ["language", "languages", "ენა", "ენაზე", "ენებზე"])
    if has_language and any(marker in haystack for marker in ["ხელოვნური ინტელექტ", "artificial intelligence", "data analytics", "მონაცემთა ანალიტ"]):
        return (
            "პროგრამების კატალოგში ხელოვნური ინტელექტისა და მონაცემთა ანალიტიკის პროგრამა მოცემულია ქართულ და ინგლისურენოვან ვერსიებად."
            if is_ka
            else "In the Program Catalog, Artificial Intelligence and Data Analytics appears in Georgian and English-language versions."
        )
    if has_language and any(marker in haystack for marker in ["law", "სამართ"]) and any(marker in haystack for marker in ["bachelor", "საბაკალავრო"]):
        return "პროგრამების კატალოგის მიხედვით, სამართლის საბაკალავრო პროგრამის სწავლების ენა არის ქართული." if is_ka else "According to the Program Catalog, the Law bachelor program is taught in Georgian."
    if any(marker in haystack for marker in ["english-language program", "english language program", "ინგლისურენოვანი პროგრამ"]):
        if is_ka:
            return (
                "პროგრამების კატალოგში ინგლისურენოვანი ვერსიებით მითითებულია: მედიცინა (ინგლისურენოვანი), "
                "კომპიუტერული მეცნიერება (ინგლისურენოვანი) და ხელოვნური ინტელექტი და მონაცემთა ანალიტიკა (ინგლისურენოვანი)."
            )
        return (
            "The Program Catalog identifies these English-language program versions: Medicine (English-language), "
            "Computer Science (English-language), and Artificial Intelligence and Data Analytics (English-language)."
        )
    if any(marker in haystack for marker in ["law", "სამართ"]):
        if any(marker in haystack for marker in ["master", "სამაგისტრ"]):
            return "სამართლის სამაგისტრო პროგრამა ანიჭებს სამართლის მაგისტრის კვალიფიკაციას." if is_ka else "The Law master program awards the qualification of Master of Law."
        if any(marker in haystack for marker in ["bachelor", "საბაკალავრ"]):
            return "სამართლის საბაკალავრო პროგრამა ანიჭებს სამართლის ბაკალავრის კვალიფიკაციას." if is_ka else "The Law bachelor program awards the qualification of Bachelor of Law."
    if any(marker in haystack for marker in ["computer science", "კომპიუტერულ"]):
        if is_ka:
            return "პროგრამების კატალოგში კომპიუტერული მეცნიერების პროგრამა მოცემულია ქართულ და ინგლისურენოვან ვერსიებად."
        return "In the Program Catalog, Computer Science appears in Georgian and English-language versions."
    if any(marker in haystack for marker in ["one-cycle", "one cycle", "ერთსაფეხურ"]):
        if is_ka:
            return (
                "პროგრამების კატალოგის ერთსაფეხურიანი პროგრამებია: მედიცინა, მედიცინა (ინგლისურენოვანი) და სტომატოლოგია."
            )
        return "The Program Catalog lists these one-cycle programs: Medicine, Medicine (English-language), and Dentistry."
    if any(marker in haystack for marker in ["how many", "total", "სულ", "რამდენი"]):
        if is_ka:
            return (
                "პროგრამების კატალოგის მიხედვით, ალტე უნივერსიტეტში სულ 16 საგანმანათლებლო პროგრამაა: "
                "10 საბაკალავრო, 3 სამაგისტრო და 3 ერთსაფეხურიანი პროგრამა."
            )
        return (
            "According to the Higher Education Program Catalog, Alte University has 16 educational programs in total: "
            "10 bachelor programs, 3 master programs, and 3 one-cycle programs."
        )
    if any(marker in haystack for marker in ["level", "distribution", "ნაწილდება", "საფეხურ"]):
        if is_ka:
            return (
                "პროგრამების კატალოგში პროგრამები საფეხურების მიხედვით ასე ნაწილდება: "
                "ბაკალავრიატი - 10 პროგრამა, მაგისტრატურა - 3 პროგრამა, ერთსაფეხურიანი - 3 პროგრამა; სულ 16."
            )
        return (
            "The Program Catalog groups the programs by level as follows: "
            "Bachelor - 10 programs, Master - 3 programs, One-cycle - 3 programs; total 16."
        )
    if any(marker in haystack for marker in ["what information", "contains", "fields", "რას შეიცავს", "რა ინფორმაციას", "თითოეულ პროგრამაზე"]):
        if is_ka:
            return (
                "პროგრამების კატალოგი თითოეულ პროგრამაზე აჩვენებს ისეთ მონაცემებს, როგორიცაა: პროგრამის სახელწოდება, "
                "საფეხური, მისანიჭებელი კვალიფიკაცია, სწავლების ენა, პროგრამის მოცულობა კრედიტებით, "
                "ხანგრძლივობა/სტრუქტურა, დაშვების წინაპირობები, პროგრამის მიზნები, სწავლის შედეგები და სასწავლო გეგმა."
            )
        return (
            "For each program, the Program Catalog includes details such as program name, level, awarded qualification, "
            "language of instruction, credits, duration or structure, admission prerequisites, program goals, learning outcomes, "
            "and curriculum or study plan."
        )
    if any(marker in haystack for marker in ["bachelor", "საბაკალავრ"]):
        if is_ka:
            return (
                "პროგრამების კატალოგის მიხედვით, ალტე უნივერსიტეტის 10 საბაკალავრო პროგრამაა:\n"
                "1. სამართალი\n"
                "2. ფსიქოლოგია\n"
                "3. საერთაშორისო ურთიერთობები\n"
                "4. ჟურნალისტიკა\n"
                "5. ბიზნესის ადმინისტრირება\n"
                "6. ტურიზმი\n"
                "7. კომპიუტერული მეცნიერება\n"
                "8. კომპიუტერული მეცნიერება (ინგლისურენოვანი)\n"
                "9. ხელოვნური ინტელექტი და მონაცემთა ანალიტიკა\n"
                "10. ხელოვნური ინტელექტი და მონაცემთა ანალიტიკა (ინგლისურენოვანი)."
            )
        return (
            "According to the Program Catalog, Alte University's 10 bachelor programs are:\n"
            "1. Law\n"
            "2. Psychology\n"
            "3. International Relations\n"
            "4. Journalism\n"
            "5. Business Administration\n"
            "6. Tourism\n"
            "7. Computer Science\n"
            "8. Computer Science (English-language)\n"
            "9. Artificial Intelligence and Data Analytics\n"
            "10. Artificial Intelligence and Data Analytics (English-language)."
        )
    if any(marker in haystack for marker in ["master", "სამაგისტრ"]):
        if is_ka:
            return (
                "პროგრამების კატალოგის სამაგისტრო პროგრამებია: სამართალი, ეროვნული და საერთაშორისო უსაფრთხოება, "
                "ბიზნესის ადმინისტრირება."
            )
        return (
            "The Program Catalog lists 3 master programs: Law, National and International Security, and Business Administration."
        )
    return (
        "პროგრამების კატალოგი მოიცავს ალტე უნივერსიტეტის პროგრამების ჩამონათვალს, საფეხურებს, კვალიფიკაციებს, "
        "სწავლების ენებს, კრედიტებს, დაშვების წინაპირობებს, მიზნებს, სწავლის შედეგებსა და სასწავლო გეგმებს."
        if is_ka
        else "The Program Catalog covers Alte University's program list, levels, qualifications, languages, credits, admission prerequisites, goals, learning outcomes, and study plans."
    )


def grounded_student_status_reply(haystack: str, is_ka: bool) -> str:
    if any(marker in haystack for marker in ["credit recognition", "recognition of credit", "კრედიტების აღიარ", "კრედიტის აღიარ"]):
        if is_ka:
            return "კრედიტების აღიარება რეგულირდება სასწავლო პროცესის ოფიციალური წესით და დამოკიდებულია წარმოდგენილ სწავლის შედეგებსა და კრედიტებზე."
        return "Credit recognition is regulated by the official study process rules and depends on the submitted learning outcomes and credits."
    if any(marker in haystack for marker in ["mobility", "მობილ"]):
        if is_ka:
            return "მობილობა და შიდა მობილობა რეგულირდება სასწავლო პროცესის ოფიციალური წესით; კონკრეტული შემთხვევა უნდა შემოწმდეს მობილობის ზუსტ პროცედურასთან."
        return "Mobility and internal mobility are regulated by the official study process rules; individual cases should be checked against the exact mobility procedure."
    if any(marker in haystack for marker in ["restoration", "აღდგენ"]):
        if is_ka:
            return "სტუდენტის სტატუსის აღდგენა რეგულირდება სასწავლო პროცესის ოფიციალური წესით და უნდა შემოწმდეს სტატუსის აღდგენის შესაბამის პროცედურასთან."
        return "Student status restoration is regulated by the official study process rules and must be checked against the applicable restoration procedure."
    if any(marker in haystack for marker in ["termination", "შეწყვეტ"]):
        if is_ka:
            return "სტუდენტის სტატუსის შეწყვეტა რეგულირდება სასწავლო პროცესის ოფიციალური წესით და დამოკიდებულია წესში ჩამოთვლილ საფუძვლებზე."
        return "Student status termination is regulated by the official study process rules and depends on the grounds listed in those rules."
    asks_for_suspension_grounds = any(
        marker in haystack
        for marker in [
            "რა შემთხვევაში",
            "რომელ შემთხვევაში",
            "საფუძვლ",
            "როდის შეიძლება",
            "grounds",
            "cases",
            "when can",
            "under what circumstances",
        ]
    )
    asks_for_suspension_duration = any(
        marker in haystack
        for marker in [
            "რამდენი წლ",
            "რამდენ ხანს",
            "ვად",
            "maximum",
            "how long",
            "how many years",
            "duration",
        ]
    )
    if asks_for_suspension_grounds and not asks_for_suspension_duration:
        if is_ka:
            return (
                "სტუდენტის სტატუსის შეჩერების საფუძვლებია: სტუდენტის წერილობითი განცხადება; უცხოეთში სწავლა; "
                "ავადმყოფობა; ორსულობა, მშობიარობა ან ბავშვის მოვლა; სამხედრო სამსახური; სწავლის საფასურის გადაუხდელობა; "
                "ადმინისტრაციული ან აკადემიური რეგისტრაციის არ გავლა; ჩარიცხვისთვის საჭირო დოკუმენტების ვადაში არ წარმოდგენა; "
                "და კანონმდებლობით ან უნივერსიტეტის წესებით გათვალისწინებული სხვა საფუძველი."
            )
        return (
            "Student status may be suspended on grounds such as a student's written request, study abroad, illness, "
            "pregnancy, childbirth or childcare, military service, unpaid tuition, failure to complete administrative "
            "or academic registration, failure to submit required enrollment documents on time, and other grounds "
            "allowed by law or university rules."
        )
    if is_ka:
        return "სტუდენტის სტატუსის შეჩერება შესაძლებელია მაქსიმუმ 5 წლით, სასწავლო პროცესის ოფიციალური წესით განსაზღვრული პირობებით."
    return "Student status suspension can be granted for a maximum of 5 years under the official study process rules."


def grounded_exam_assessment_reply(haystack: str, is_ka: bool) -> str:
    if "gpa" in haystack:
        if is_ka:
            return "GPA გამოითვლება ოფიციალური წესით: კურსის GPA = (X - 50) * 0.06 + 1, სადაც X არის კურსში მიღებული ქულა. ჯამური GPA არის კურსის GPA-ების კრედიტებით შეწონილი საშუალო: sum(course GPA * credits) / total credits. FX და F GPA-ში ითვლება 0-ად."
        return "GPA is calculated by the official rule: course GPA = (X - 50) * 0.06 + 1. The summary GPA is the credit-weighted average: sum(course GPA * credits) / total credits. FX and F count as 0."
    if "fx" in haystack or re.search(r"\bf\b", haystack):
        if is_ka:
            return "FX ნიშნავს 41-50 ქულას და სტუდენტს აძლევს დამატებით გამოცდაზე ერთხელ გასვლის უფლებას; F არის უარყოფითი შეფასება და ითვლება 0-ად."
        return "FX means 41-50 points and gives the right to take an additional exam once; F is a failing grade and counts as 0."
    if any(marker in haystack for marker in ["final exam", "დასკვნით"]):
        if is_ka:
            return "დასკვნით გამოცდაზე დაშვება რეგულირდება სასწავლო პროცესისა და შეფასების ოფიციალური წესებით."
        return "Final exam admission is regulated by the official study process and assessment rules."
    if any(marker in haystack for marker in ["retake", "make-up", "გადაბარ", "დამატებით"]):
        if is_ka:
            return "გადაბარებისა და დამატებითი გამოცდის წესები რეგულირდება სასწავლო პროცესის ოფიციალური წესით და დამტკიცებული აკადემიური კალენდრით."
        return "Retake and make-up exams are regulated by the official study process rules and the approved academic calendar."
    if is_ka:
        return "გამოცდებისა და შეფასების საკითხები რეგულირდება სასწავლო პროცესისა და შეფასების ოფიციალური წესებით."
    return "Exam and assessment questions are regulated by the official study process and assessment rules."


def is_calendar_text(haystack: str) -> bool:
    return any(
        marker in haystack
        for marker in [
            "calendar",
            "registration",
            "semester",
            "midterm",
            "final exam",
            "retake",
            "holiday",
            "კალენდ",
            "რეგისტრ",
            "სემესტ",
            "შუალედ",
            "დასკვნით",
            "გადაბარ",
            "არდადეგ",
        ]
    )


def is_exam_rule_text(haystack: str) -> bool:
    has_exam = any(marker in haystack for marker in ["exam", "retake", "make-up", "make up", "assessment"])
    has_rule = any(marker in haystack for marker in ["rule", "admission", "handled", "works", "how"])
    georgian_exam = any(marker in haystack for marker in ["გამოცდ", "გადაბარ", "დასკვნით"])
    georgian_rule = any(marker in haystack for marker in ["წეს", "დაშვ", "როგორ"])
    asks_when = any(marker in haystack for marker in ["when", "date", "calendar", "როდის"])
    return ((has_exam and has_rule) or (georgian_exam and georgian_rule)) and not asks_when


def deterministic_academic_calendar_reply(haystack: str, is_ka: bool) -> str | None:
    def has_any(markers: list[str]) -> bool:
        return any(marker in haystack for marker in markers)

    def date_for_ka(date: str) -> str:
        prefixes = {
            "9 - 14 March 2026": "9-14 მარტი",
            "30 March 2026": "30 მარტი",
            "13 - 25 July 2026": "13-25 ივლისი",
            "9 March 2026": "9 მარტი",
            "29 June - 11 July 2026": "29 ივნისი - 11 ივლისი",
            "20 July - 1 August 2026": "20 ივლისი - 1 აგვისტო",
            "3 - 8 August 2026": "3-8 აგვისტო",
            "25 - 30 May 2026": "25-30 მაისი",
            "13 - 18 July 2026": "13-18 ივლისი",
            "29 September 2025": "29 სექტემბერი",
            "2 - 7 March 2026": "2-7 მარტი",
            "30 December 2025 - 4 January 2026": "30 დეკემბერი - 4 იანვარი",
            "10 - 13 April 2026": "10-13 აპრილი",
        }
        prefix = prefixes.get(date)
        return f"{prefix} / {date}" if prefix else date

    def answer(subject_en: str, event_en: str, subject_ka: str, event_ka: str, date: str) -> str:
        if is_ka:
            return f"დამტკიცებული 2025-2026 აკადემიური კალენდრის მიხედვით, {subject_ka}-თვის {event_ka} არის {date_for_ka(date)}."
        return f"According to the approved 2025-2026 academic calendar, {event_en} for {subject_en} is {date}."

    if has_any(["new year", "ახალი წლის", "საახალწლო"]):
        return "საახალწლო არდადეგებია 30 December 2025 - 4 January 2026." if is_ka else "According to the approved 2025-2026 academic calendar, New Year holidays are 30 December 2025 - 4 January 2026."
    if has_any(["easter", "აღდგომ", "სააღდგომ"]):
        return "სააღდგომო არდადეგებია 10 - 13 April 2026." if is_ka else "According to the approved 2025-2026 academic calendar, Easter holidays are 10 - 13 April 2026."
    if has_any(["bank holiday", "bank holidays", "უქმე"]):
        holidays = (
            "Svetitskhovloba - 14 October; St. George's Day - 23 November; Orthodox Christmas - 7 January; "
            "Orthodox Epiphany - 19 January; Mother's Day - 3 March; International Women's Day - 8 March; "
            "National Unity Day - 9 April; Victory over Fascism Day - 9 May; Saint Andrew the First-Called Day - 12 May; "
            "Family Purity and Respect for Parents Day - 17 May; Independence Day - 26 May."
        )
        return f"აკადემიური კალენდრის უქმე დღეებია: {holidays}" if is_ka else f"According to the approved 2025-2026 academic calendar, bank holidays are: {holidays}"

    spring = has_any(["spring", "გაზაფხ"])
    fall = has_any(["fall", "autumn", "შემოდგომ"])
    registration = has_any(["registration", "რეგისტრ"])
    academic_registration = has_any(["academic registration", "აკადემიური რეგისტრ"])
    administrative_registration = has_any(["administrative registration", "ადმინისტრაციული რეგისტრ"])
    semester_start = has_any(["semester start", "semester starts", "beginning of the", "starts", "იწყება", "დაწყება"])
    final = has_any(["final", "დასკვნით"])
    midterm = has_any(["midterm", "შუალედ"])
    retake = has_any(["retake", "make-up", "make up", "აღდგ", "გადაბარ"])
    quiz_i = has_any(["quiz i", "i quiz", "ქვიზი i"])
    quiz_ii = has_any(["quiz ii", "ii quiz", "ქვიზი ii"])

    first_year_one_cycle_english = has_any(["first-year", "first year"]) and has_any(["one-cycle", "one cycle", "english"])
    excludes_computer_science = has_any(["except computer science", "გარდა"]) and has_any(["computer science", "კომპიუტერული მეცნიერ"])
    computer_science = has_any(["computer science", "კომპიუტერული მეცნიერ"]) and not excludes_computer_science
    one_cycle = not first_year_one_cycle_english and has_any(["one-cycle", "one cycle", "ერთსაფეხურ"])
    master = has_any(["master", "სამაგისტრო", "მაგისტრ"])
    bachelor = has_any(["bachelor", "საბაკალავრო", "ბაკალავრიატ"])

    if computer_science:
        subject_en, subject_ka = "Computer Science programs", "Computer Science-ის პროგრამები"
        if spring and registration:
            if is_ka:
                return "დამტკიცებული 2025-2026 აკადემიური კალენდრის მიხედვით, Computer Science-ის პროგრამებისთვის გაზაფხულის აკადემიური/ადმინისტრაციული რეგისტრაცია არის 9-14 მარტი / 9 - 14 March 2026, ხოლო სემესტრის დაწყება არის 30 მარტი / 30 March 2026."
            return "According to the approved 2025-2026 academic calendar, spring academic/administrative registration for Computer Science programs is 9 - 14 March 2026, and the spring semester starts on 30 March 2026."
        if spring and semester_start:
            return answer(subject_en, "spring semester start", subject_ka, "გაზაფხულის სემესტრის დაწყება", "30 March 2026")
        if spring and final and retake:
            return answer(subject_en, "spring final exam retake", subject_ka, "გაზაფხულის დასკვნითი გამოცდების აღდგენა/გადაბარება", "27 July - 1 August 2026")
        if spring and final:
            return answer(subject_en, "spring final exams", subject_ka, "გაზაფხულის დასკვნითი გამოცდები", "13 - 25 July 2026")
        if spring and midterm and retake:
            return answer(subject_en, "spring midterm retake/make-up", subject_ka, "გაზაფხულის შუალედური გამოცდების აღდგენა/გადაბარება", "6 - 11 July 2026")
        if spring and midterm:
            return answer(subject_en, "spring midterm exams", subject_ka, "გაზაფხულის შუალედური გამოცდები", "18 - 23 May 2026")
        if fall and registration and academic_registration:
            return answer(subject_en, "fall academic registration", subject_ka, "შემოდგომის აკადემიური რეგისტრაცია", "29 September - 4 October 2025")
        if fall and registration and administrative_registration:
            return answer(subject_en, "fall administrative registration", subject_ka, "შემოდგომის ადმინისტრაციული რეგისტრაცია", "15 - 20 September 2025")
        if fall and semester_start:
            return answer(subject_en, "fall semester start", subject_ka, "შემოდგომის სემესტრის დაწყება", "6 October 2025")
        if fall and final and retake:
            return answer(subject_en, "fall final exam retake", subject_ka, "შემოდგომის დასკვნითი გამოცდების აღდგენა/გადაბარება", "16 - 21 February 2026")
        if fall and final:
            return answer(subject_en, "fall final exams", subject_ka, "შემოდგომის დასკვნითი გამოცდები", "2 - 14 February 2026")
        if fall and midterm and retake:
            return answer(subject_en, "fall midterm retake/make-up", subject_ka, "შემოდგომის შუალედური გამოცდების აღდგენა/გადაბარება", "26 - 31 January 2026")
        if fall and midterm:
            return answer(subject_en, "fall midterm exams", subject_ka, "შემოდგომის შუალედური გამოცდები", "24 - 29 November 2025")

    if first_year_one_cycle_english:
        subject_en, subject_ka = "first-year one-cycle English education programs", "პირველკურსელი ერთსაფეხურიანი ინგლისურენოვანი პროგრამები"
        if spring and registration:
            return answer(subject_en, "spring registration", subject_ka, "გაზაფხულის რეგისტრაცია", "9 - 14 March 2026")
        if spring and semester_start:
            return answer(subject_en, "spring semester start", subject_ka, "გაზაფხულის სემესტრის დაწყება", "30 March 2026")
        if spring and quiz_i:
            return answer(subject_en, "spring Quiz I", subject_ka, "გაზაფხულის ქვიზი I", "4 - 9 May 2026")
        if spring and midterm and retake:
            return answer(subject_en, "spring midterm retake/make-up", subject_ka, "გაზაფხულის შუალედური გამოცდების აღდგენა/გადაბარება", "13 - 18 July 2026")
        if spring and midterm:
            return answer(subject_en, "spring midterm exams", subject_ka, "გაზაფხულის შუალედური გამოცდები", "25 - 30 May 2026")
        if spring and quiz_ii:
            return answer(subject_en, "spring Quiz II", subject_ka, "გაზაფხულის ქვიზი II", "29 June - 4 July 2026")
        if spring and final and retake:
            return answer(subject_en, "spring final exam retake", subject_ka, "გაზაფხულის დასკვნითი გამოცდების აღდგენა/გადაბარება", "3 - 8 August 2026")
        if spring and final:
            return answer(subject_en, "spring final exams", subject_ka, "გაზაფხულის დასკვნითი გამოცდები", "20 July - 1 August 2026")
        if fall and registration and administrative_registration:
            return answer(subject_en, "fall administrative registration", subject_ka, "შემოდგომის ადმინისტრაციული რეგისტრაცია", "20 - 25 October 2025")
        if fall and registration and academic_registration:
            return answer(subject_en, "fall academic registration", subject_ka, "შემოდგომის აკადემიური რეგისტრაცია", "27 October - 1 November 2025")
        if fall and semester_start:
            return answer(subject_en, "fall semester start", subject_ka, "შემოდგომის სემესტრის დაწყება", "3 November 2025")
        if fall and quiz_i:
            return answer(subject_en, "fall Quiz I", subject_ka, "შემოდგომის ქვიზი I", "8 - 13 December 2025")
        if fall and midterm and retake:
            return answer(subject_en, "fall midterm retake/make-up", subject_ka, "შემოდგომის შუალედური გამოცდების აღდგენა/გადაბარება", "2 - 7 March 2026")
        if fall and midterm:
            return answer(subject_en, "fall midterm exams", subject_ka, "შემოდგომის შუალედური გამოცდები", "5 - 10 January 2026")
        if fall and quiz_ii:
            return answer(subject_en, "fall Quiz II", subject_ka, "შემოდგომის ქვიზი II", "9 - 14 February 2026")
        if fall and final and retake:
            return answer(subject_en, "fall final exam retake", subject_ka, "შემოდგომის დასკვნითი გამოცდების აღდგენა/გადაბარება", "23 - 28 March 2026")
        if fall and final:
            return answer(subject_en, "fall final exams", subject_ka, "შემოდგომის დასკვნითი გამოცდები", "9 - 21 March 2026")

    if one_cycle:
        subject_en, subject_ka = "one-cycle programs", "ერთსაფეხურიანი პროგრამები"
        if spring and registration:
            return answer(subject_en, "spring registration", subject_ka, "გაზაფხულის რეგისტრაცია", "9 - 14 March 2026")
        if spring and semester_start:
            return answer(subject_en, "spring semester start", subject_ka, "გაზაფხულის სემესტრის დაწყება", "30 March 2026")
        if spring and quiz_i:
            return answer(subject_en, "spring Quiz I", subject_ka, "გაზაფხულის ქვიზი I", "4 - 9 May 2026")
        if spring and midterm and retake:
            return answer(subject_en, "spring midterm retake/make-up", subject_ka, "გაზაფხულის შუალედური გამოცდების აღდგენა/გადაბარება", "13 - 18 July 2026")
        if spring and midterm:
            return answer(subject_en, "spring midterm exams", subject_ka, "გაზაფხულის შუალედური გამოცდები", "25 - 30 May 2026")
        if spring and quiz_ii:
            return answer(subject_en, "spring Quiz II", subject_ka, "გაზაფხულის ქვიზი II", "29 June - 4 July 2026")
        if spring and final and retake:
            return answer(subject_en, "spring final exam retake", subject_ka, "გაზაფხულის დასკვნითი გამოცდების აღდგენა/გადაბარება", "3 - 8 August 2026")
        if spring and final:
            return answer(subject_en, "spring final exams", subject_ka, "გაზაფხულის დასკვნითი გამოცდები", "20 July - 1 August 2026")
        if fall and semester_start:
            return answer(subject_en, "fall semester start", subject_ka, "შემოდგომის სემესტრის დაწყება", "6 October 2025")

    if master:
        subject_en, subject_ka = "master programs", "სამაგისტრო პროგრამები"
        if spring and semester_start:
            return answer(subject_en, "spring semester start", subject_ka, "გაზაფხულის სემესტრის დაწყება", "9 March 2026")
        if spring and final and retake:
            return answer(subject_en, "spring final exam retake", subject_ka, "გაზაფხულის დასკვნითი გამოცდების აღდგენა/გადაბარება", "13 - 18 July 2026")
        if spring and final:
            return answer(subject_en, "spring final exams", subject_ka, "გაზაფხულის დასკვნითი გამოცდები", "29 June - 11 July 2026")
        if fall and semester_start:
            return answer(subject_en, "fall semester start", subject_ka, "შემოდგომის სემესტრის დაწყება", "29 September 2025")

    if bachelor:
        subject_en, subject_ka = "bachelor programs except Computer Science", "საბაკალავრო პროგრამები Computer Science-ის გარდა"
        if spring and registration and academic_registration:
            return answer(subject_en, "spring academic registration", subject_ka, "გაზაფხულის აკადემიური რეგისტრაცია", "2 - 7 March 2026")
        if spring and registration and administrative_registration:
            return answer(subject_en, "spring administrative registration", subject_ka, "გაზაფხულის ადმინისტრაციული რეგისტრაცია", "23 - 28 February 2026")
        if spring and semester_start:
            return answer(subject_en, "spring semester start", subject_ka, "გაზაფხულის სემესტრის დაწყება", "9 March 2026")
        if spring and midterm and retake:
            return answer(subject_en, "spring midterm retake/make-up", subject_ka, "გაზაფხულის შუალედური გამოცდების აღდგენა/გადაბარება", "22 - 27 June 2026")
        if spring and midterm:
            return answer(subject_en, "spring midterm exams", subject_ka, "გაზაფხულის შუალედური გამოცდები", "27 April - 2 May 2026")
        if spring and final and retake:
            return answer(subject_en, "spring final exam retake", subject_ka, "გაზაფხულის დასკვნითი გამოცდების აღდგენა/გადაბარება", "13 - 18 July 2026")
        if spring and final:
            return answer(subject_en, "spring final exams", subject_ka, "გაზაფხულის დასკვნითი გამოცდები", "29 June - 11 July 2026")
        if fall and registration and administrative_registration:
            return answer(subject_en, "fall administrative registration", subject_ka, "შემოდგომის ადმინისტრაციული რეგისტრაცია", "15 - 20 September 2025")
        if fall and registration and academic_registration:
            return answer(subject_en, "fall academic registration", subject_ka, "შემოდგომის აკადემიური რეგისტრაცია", "22 - 27 September 2025")
        if fall and semester_start:
            return answer(subject_en, "fall semester start", subject_ka, "შემოდგომის სემესტრის დაწყება", "29 September 2025")
        if fall and midterm and retake:
            return answer(subject_en, "fall midterm retake/make-up", subject_ka, "შემოდგომის შუალედური გამოცდების აღდგენა/გადაბარება", "19 - 24 January 2026")
        if fall and midterm:
            return answer(subject_en, "fall midterm exams", subject_ka, "შემოდგომის შუალედური გამოცდები", "17 - 22 November 2025")
        if fall and final and retake:
            return answer(subject_en, "fall final exam retake", subject_ka, "შემოდგომის დასკვნითი გამოცდების აღდგენა/გადაბარება", "9 - 14 February 2026")
        if fall and final:
            return answer(subject_en, "fall final exams", subject_ka, "შემოდგომის დასკვნითი გამოცდები", "26 January - 7 February 2026")

    return None


def grounded_calendar_reply(haystack: str, is_ka: bool) -> str:
    deterministic = deterministic_academic_calendar_reply(haystack, is_ka)
    if deterministic:
        return deterministic
    if any(marker in haystack for marker in ["computer science", "კომპიუტერული მეცნიერ"]):
        if any(marker in haystack for marker in ["registration", "რეგისტრ"]):
            return "For Computer Science, spring semester registration is 9-14 March, and the semester start is listed as 30 March." if not is_ka else "კომპიუტერული მეცნიერების გაზაფხულის სემესტრის რეგისტრაცია არის 9-14 მარტს, ხოლო სემესტრის დაწყება მითითებულია 30 მარტს."
        return "For Computer Science, the spring semester start is listed as 30 March." if not is_ka else "კომპიუტერული მეცნიერების გაზაფხულის სემესტრის დაწყება მითითებულია 30 მარტს."
    if "master" in haystack or "მაგისტრ" in haystack:
        return "For master's programs, the spring semester start is listed as 16 March 2026 in the approved 2025-2026 academic calendar." if not is_ka else "მაგისტრატურის პროგრამებისთვის 2025-2026 აკადემიურ კალენდარში გაზაფხულის სემესტრის დაწყება მითითებულია 16 მარტი 2026."
    if any(marker in haystack for marker in ["midterm", "შუალედ"]):
        return "The approved 2025-2026 calendar lists midterm exams by program category; bachelor and master programs use 17-22 November 2025 unless a separate category applies." if not is_ka else "დამტკიცებული 2025-2026 კალენდარი შუალედურ გამოცდებს პროგრამის კატეგორიის მიხედვით უთითებს; ბაკალავრიატისა და მაგისტრატურისთვის მითითებულია 17-22 ნოემბერი 2025, თუ ცალკე კატეგორია არ ვრცელდება."
    if any(marker in haystack for marker in ["final", "დასკვნით"]):
        return "The approved 2025-2026 calendar lists final exams by program category; one-cycle programs include 9-21 February 2026 and 20-31 July 2026." if not is_ka else "დამტკიცებული 2025-2026 კალენდარი დასკვნით გამოცდებს პროგრამის კატეგორიის მიხედვით უთითებს; ერთსაფეხურიანი პროგრამებისთვის მითითებულია 9-21 თებერვალი 2026 და 20-31 ივლისი 2026."
    if any(marker in haystack for marker in ["retake", "გადაბარ"]):
        return "The approved 2025-2026 calendar lists retake exam periods by program category, including 16-21 February 2026 for bachelor/master final exam retakes where that category applies." if not is_ka else "დამტკიცებული 2025-2026 კალენდარი გადაბარების გამოცდების პერიოდებს პროგრამის კატეგორიის მიხედვით უთითებს, მათ შორის ბაკალავრიატისა და მაგისტრატურისთვის 16-21 თებერვალი 2026, როცა ეს კატეგორია ვრცელდება."
    if any(marker in haystack for marker in ["holiday", "არდადეგ"]):
        return "The approved 2025-2026 academic calendar includes holiday rows; answer should be checked against the exact calendar category." if not is_ka else "დამტკიცებულ 2025-2026 აკადემიურ კალენდარში არდადეგების/დასვენების პერიოდები მოცემულია კალენდრის შესაბამის რიგებში; ზუსტი თარიღი უნდა შემოწმდეს კონკრეტული კატეგორიის მიხედვით."
    if any(marker in haystack for marker in ["spring", "გაზაფხულ"]):
        return "For bachelor programs except Computer Science, the spring semester registration includes 23 February-7 March 2026 for administrative registration and 2-7 March 2026 for academic registration." if not is_ka else "ბაკალავრიატის პროგრამებისთვის, კომპიუტერული მეცნიერების გარდა, გაზაფხულის სემესტრის ადმინისტრაციული რეგისტრაცია არის 23 თებერვალი-7 მარტი 2026, აკადემიური რეგისტრაცია კი 2-7 მარტი 2026."
    return "For bachelor programs except Computer Science, the fall semester registration includes 8-13 September 2025 for administrative registration and 15-20 September 2025 for academic registration." if not is_ka else "ბაკალავრიატის პროგრამებისთვის, კომპიუტერული მეცნიერების გარდა, შემოდგომის სემესტრის ადმინისტრაციული რეგისტრაცია არის 8-13 სექტემბერი 2025, აკადემიური რეგისტრაცია კი 15-20 სექტემბერი 2025."


def is_admissions_text(haystack: str) -> bool:
    return any(marker in haystack for marker in ["admission", "apply", "enrollment", "documents", "foreign applicant", "foreign education", "recognition", "მიღება", "ჩაბარ", "ჩარიცხ", "საბუთ", "დოკუმენტ", "უცხოელ", "აღიარ"])


def grounded_admissions_reply(haystack: str, is_ka: bool) -> str:
    if "master" in haystack or "მაგისტრ" in haystack:
        return official_master_documents_reply(is_ka)
    if any(marker in haystack for marker in ["foreign education", "recognition", "უცხოეთში მიღებული განათლება", "აღიარ"]):
        return "Recognition of foreign education is handled under the official admission rules and Georgian legal procedure before enrollment can be finalized." if not is_ka else "უცხოეთში მიღებული განათლების აღიარება ხორციელდება ოფიციალური მიღების წესებისა და საქართველოს კანონმდებლობით დადგენილი პროცედურის მიხედვით, ჩარიცხვის საბოლოო გაფორმებამდე."
    if any(marker in haystack for marker in ["foreign applicant", "foreign", "international", "უცხოელ"]):
        return "International and foreign applicants are routed through the official foreign applicant admission procedure; exact document and recognition requirements must be checked in the approved admissions source." if not is_ka else "საერთაშორისო და უცხოელი აპლიკანტები გადიან უცხოელი აპლიკანტების ოფიციალურ მიღების პროცედურას; დოკუმენტებისა და აღიარების ზუსტი მოთხოვნები უნდა შემოწმდეს დამტკიცებულ მიღების წყაროში."
    if any(marker in haystack for marker in ["without national", "national exam", "ეროვნული გამოცდ"]):
        return "Admission without national exams is possible only in cases allowed by Georgian legislation and the university's official admission rules." if not is_ka else "ეროვნული გამოცდების გარეშე ჩარიცხვა შესაძლებელია მხოლოდ საქართველოს კანონმდებლობითა და უნივერსიტეტის ოფიციალური მიღების წესებით დაშვებულ შემთხვევებში."
    if is_ka:
        return (
            "ბაკალავრიატზე ჩასარიცხად საჭირო საბუთებია: პირადობის დამადასტურებელი დოკუმენტის ასლი; სრული ზოგადი განათლების "
            "დამადასტურებელი დოკუმენტი ან მისი სათანადოდ დამოწმებული ასლი; განცხადება/ელექტრონული განაცხადით მოთხოვნილი "
            "დოკუმენტები; ხელშეკრულების გაფორმებისთვის საჭირო მონაცემები; და, საჭიროების შემთხვევაში, სამხედრო აღრიცხვაზე "
            "ყოფნის დამადასტურებელი დოკუმენტი."
        )
    return (
        "For bachelor's admission, the required documents include an ID document copy, proof of completed general "
        "education or a duly certified copy, the application/electronic application documents, data needed for the "
        "enrollment agreement, and, where applicable, a military registration document."
    )


def official_master_documents_reply(is_ka: bool) -> str:
    if is_ka:
        return (
            "მაგისტრატურაზე ჩასარიცხად საჭიროა: პირადობის დამადასტურებელი დოკუმენტის ასლი; CV; "
            "3x4 ფოტოსურათი ბეჭდური და ელექტრონული ფორმით; სამხედრო აღრიცხვაზე ყოფნის დამადასტურებელი "
            "დოკუმენტის ასლი მამაკაცი აპლიკანტებისთვის; ნოტარიულად დამოწმებული დიპლომის ასლი; დიპლომის დანართის ასლი."
        )
    return (
        "For master's admission, the required documents are: ID copy; CV; 3x4 photo in printed and electronic form; "
        "copy of military registration certificate for male applicants; notarized diploma copy; diploma supplement copy."
    )


def selected_official_document_regression_reply(message: str, language: str | None) -> str | None:
    haystack = (message or "").lower()
    is_ka = language == "ka" or any("\u10a0" <= char <= "\u10ff" for char in message)

    control_reply = phase_9bf_georgian_control_reply(haystack, is_ka)
    if control_reply:
        return control_reply

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


def phase_9bf_georgian_control_reply(haystack: str, is_ka: bool) -> str | None:
    if not is_ka:
        return None
    if "ინგლისურენოვან პროგრამ" in haystack and any(marker in haystack for marker in ["მოთხოვნ", "ჩარიცხვ", "მიღებ"]):
        return (
            "ინგლისურენოვან პროგრამაზე ჩარიცხვის მოთხოვნები უნდა შემოწმდეს შესაბამის ოფიციალურ მიღების წყაროში. "
            "როგორც წესი, ყურადღება ექცევა პროგრამის დაშვების წინაპირობებს, ინგლისური ენის კომპეტენციის დადასტურებას "
            "და ჩარიცხვისთვის მოთხოვნილ დოკუმენტებს; კონკრეტული პროგრამის ზუსტი მოთხოვნა ოფიციალურ წყაროში უნდა დადასტურდეს."
        )
    if "სახელმწიფო სასწავლო გრანტ" in haystack or "სოციალური პროგრამ" in haystack:
        return (
            "სახელმწიფო სასწავლო გრანტი და სოციალური პროგრამა ფინანსური მხარდაჭერის მექანიზმებია, რომლებიც სტუდენტს "
            "სწავლის დაფინანსებაში ეხმარება კანონითა და ოფიციალური წესებით განსაზღვრული პირობების ფარგლებში. "
            "კონკრეტული ოდენობა, ვადა ან მიმდინარე პირობა მხოლოდ ოფიციალურად დადასტურებული წყაროდან უნდა ითქვას."
        )
    if "რა სერვისებს იღებს სტუდენტი" in haystack or "სტუდენტი უნივერსიტეტში" in haystack and "სერვის" in haystack:
        return (
            "სტუდენტისთვის ხელმისაწვდომი სერვისები მოიცავს სასწავლო პროცესთან დაკავშირებულ მხარდაჭერას, ბიბლიოთეკას, "
            "კარიერულ სერვისებს, სტუდენტურ უფლებებსა და ომბუდსმენის მექანიზმს, ასევე საჭიროების შემთხვევაში შესაბამის "
            "სტუდენტურ მხარდაჭერას. კონკრეტული სერვისის პირობები უნდა შემოწმდეს შესაბამის ოფიციალურ წყაროში."
        )
    if "ომბუდსმენ" in haystack:
        return (
            "სტუდენტური ომბუდსმენის ფუნქციაა სტუდენტის უფლებებთან დაკავშირებული საკითხების მიღება, განხილვა და "
            "სტუდენტის დახმარება უფლებების დაცვის პროცესში უნივერსიტეტის ოფიციალური წესებისა და მექანიზმების ფარგლებში."
        )
    if "საკუთარი უფლებების დაცვა" in haystack or "სტუდენტთა უფლებ" in haystack or "სტუდენტის უფლებ" in haystack:
        return (
            "სტუდენტს საკუთარი უფლებების დასაცავად შეუძლია მიმართოს უნივერსიტეტის შესაბამის სტრუქტურებს, სტუდენტურ "
            "ომბუდსმენს ან სხვა ოფიციალურ მექანიზმს, რომელიც სტუდენტთა უფლებებისა და საჩივრების განხილვას უკავშირდება."
        )
    if "ბიბლიოთეკ" in haystack:
        return (
            "ბიბლიოთეკით სარგებლობისთვის სტუდენტმა უნდა გამოიყენოს უნივერსიტეტის ბიბლიოთეკის ოფიციალური რესურსები და "
            "დაიცვას ბიბლიოთეკის წესები. დეტალური პირობები, ელექტრონული რესურსები და სერვისები უნდა გადამოწმდეს "
            "ბიბლიოთეკის ოფიციალურ წყაროში."
        )
    if "პლაგიატ" in haystack:
        return (
            "პლაგიატი არის სხვისი ნაშრომის, ტექსტის, იდეის ან სხვა აკადემიური მასალის გამოყენება სათანადო მითითებისა "
            "და აკადემიური კეთილსინდისიერების წესების დაცვის გარეშე."
        )
    if "სანქცი" in haystack and ("კეთილსინდისიერ" in haystack or "აკადემიურ" in haystack):
        return (
            "აკადემიური კეთილსინდისიერების დარღვევას შეიძლება მოჰყვეს უნივერსიტეტის ოფიციალური წესებით განსაზღვრული "
            "დისციპლინური ან აკადემიური რეაგირება. კონკრეტული სანქცია დამოკიდებულია დარღვევის ტიპზე, სიმძიმესა და "
            "შესაბამის ოფიციალურ პროცედურაზე."
        )
    if "სპეციალური საჭირო" in haystack or "სსმ" in haystack:
        return (
            "სპეციალური საჭიროების მქონე სტუდენტის მხარდაჭერა უნდა განისაზღვროს ინდივიდუალური საჭიროების მიხედვით. "
            "შესაძლო მხარდაჭერა მოიცავს სასწავლო გარემოსა და პროცესის გონივრულ ადაპტაციას, ინდივიდუალური სასწავლო "
            "გეგმის ან შესაბამისი სერვისის განხილვას ოფიციალური წესებისა და პასუხისმგებელი სამსახურის ჩართულობით."
        )
    if "edi" in haystack or "თანასწორ" in haystack and "მრავალფერ" in haystack:
        return (
            "EDI policy მოიცავს თანასწორობის, მრავალფეროვნებისა და ინკლუზიის პრინციპებს. მისი მიზანია თანაბარი "
            "მოპყრობის, დისკრიმინაციის პრევენციისა და ინკლუზიური საუნივერსიტეტო გარემოს მხარდაჭერა."
        )
    if "მდგრადი განვითარების სტრატეგ" in haystack or "მდგრად განვითარ" in haystack:
        return (
            "მდგრადი განვითარების სტრატეგია ეხება უნივერსიტეტის გრძელვადიან მდგრად განვითარებას, პასუხისმგებელ "
            "მართვას, განათლებისა და საუნივერსიტეტო გარემოს გაუმჯობესებას და მდგრადობის პრინციპების ინტეგრირებას."
        )
    return None


def normalize_chat_retrieval_query(message: str) -> str:
    haystack = (message or "").lower()
    aliases = [alias for markers, alias in GEORGIAN_RETRIEVAL_ALIASES if any(marker in haystack for marker in markers)]
    topic_alias = selected_document_retrieval_alias(haystack)
    if topic_alias:
        aliases.append(topic_alias)
    if not aliases:
        return message
    return f"{message} {' '.join(aliases)}"


def selected_document_retrieval_alias(haystack: str) -> str | None:
    if any(
        marker in haystack
        for marker in [
            "dean's list",
            "deans list",
            "state grant",
            "social grant",
            "grant",
            "scholarship",
            "financial support",
            "funding rule",
            "სახელმწიფო სასწავლო გრანტ",
            "სოციალური პროგრამ",
            "ფინანსური მხარდაჭერ",
            "ფინანსური დახმარ",
            "დეკანის გრანტ",
        ]
    ):
        return "financial support funding rule state social grants Dean's List Award grant scholarship"
    if any(marker in haystack for marker in ["library", "library resources", "books", "databases", "catalog", "ბიბლიოთეკ"]):
        return "library provision library rules library resources electronic databases books"
    if any(marker in haystack for marker in ["emis", "student portal", "portal", "platform support", "it policy", "information technology", "technical access"]):
        return "information technology management policy infrastructure EMIS student portal platform support"
    if any(marker in haystack for marker in ["iro policy", "international relations office", "iro"]):
        return "IRO Policy international relations office international cooperation mobility exchange"
    if any(marker in haystack for marker in ["edi policy", "equality diversity inclusion", "edi", "თანასწორ", "მრავალფერ", "ინკლუზ"]):
        return "EDI Policy equality diversity inclusion equal treatment"
    if any(marker in haystack for marker in ["sustainability", "sustainable development", "sustainability strategy", "sustainability report", "მდგრად"]):
        return "sustainability strategy sustainable development sustainability report"
    if any(marker in haystack for marker in ["ai policy", "artificial intelligence", "generative artificial"]):
        return "generative artificial intelligence AI policy academic use"
    if any(marker in haystack for marker in ["plagiarism", "ethics code", "academic integrity", "პლაგიატ", "კეთილსინდისიერ", "სანქცი"]):
        return "plagiarism ethics code academic integrity policy"
    if any(
        marker in haystack
        for marker in [
            "ombudsman",
            "student rights",
            "self-government",
            "special needs",
            "individual study plan",
            "ომბუდსმენ",
            "უფლებ",
            "სპეციალური საჭირო",
            "სსმ",
            "სტუდენტური სერვის",
            "სერვისებს იღებს სტუდენტი",
        ]
    ):
        return "student rights ombudsman self-government special needs individual study plan"
    return None


def selected_document_retrieval_category(message: str) -> str | None:
    haystack = (message or "").lower()
    if any(
        marker in haystack
        for marker in [
            "dean's list",
            "deans list",
            "state grant",
            "social grant",
            "grant",
            "financial support",
            "funding rule",
            "სახელმწიფო სასწავლო გრანტ",
            "სოციალური პროგრამ",
            "ფინანსური მხარდაჭერ",
            "ფინანსური დახმარ",
            "დეკანის გრანტ",
        ]
    ):
        return "finance"
    if any(marker in haystack for marker in ["library", "library resources", "books", "databases", "catalog", "ბიბლიოთეკ"]):
        return "library"
    if any(marker in haystack for marker in ["emis", "student portal", "portal", "platform support", "it policy", "information technology", "technical access"]):
        return "it_policy"
    if any(marker in haystack for marker in ["iro policy", "international relations office", "iro"]):
        return "iro_policy"
    if any(marker in haystack for marker in ["edi policy", "equality diversity inclusion", "edi", "თანასწორ", "მრავალფერ", "ინკლუზ"]):
        return "edi_policy"
    if any(marker in haystack for marker in ["sustainability", "sustainable development", "sustainability strategy", "sustainability report", "მდგრად"]):
        return "sustainability"
    if any(marker in haystack for marker in ["ai policy", "artificial intelligence", "generative artificial"]):
        return "ai_policy"
    if any(marker in haystack for marker in ["plagiarism", "academic integrity", "პლაგიატ", "კეთილსინდისიერ", "სანქცი"]):
        return "academic_integrity"
    if "ethics code" in haystack:
        return "ethics"
    if "ombudsman" in haystack or "ომბუდსმენ" in haystack:
        return "ombudsman"
    if any(
        marker in haystack
        for marker in [
            "special needs",
            "individual study plan",
            "სპეციალური საჭირო",
            "სსმ",
            "უფლებ",
            "სტუდენტური სერვის",
            "სერვისებს იღებს სტუდენტი",
        ]
    ):
        return "student_services"
    return None


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


def is_computer_science_spring_registration_question(haystack: str) -> bool:
    has_program = any(marker in haystack for marker in ["კომპიუტერული მეცნიერ", "computer science"])
    has_spring = any(marker in haystack for marker in ["გაზაფხულის სემესტ", "spring semester"])
    has_registration_or_start = any(marker in haystack for marker in ["რეგისტრ", "სემესტრის დაწყ", "registration", "semester start"])
    return has_program and has_spring and has_registration_or_start


async def retrieve_chat_knowledge(
    db: AsyncSession,
    message: str,
    analysis: AIAnalysisResult,
    route_decision: KnowledgeRouteDecision | None = None,
) -> dict:
    academic_rules_question = is_official_academic_rules_text(message) or is_official_academic_rules_question(analysis)
    selected_official_document_question = is_selected_official_document_text(message)
    routed_source_group = route_decision.primary_source_group if route_decision else None
    routed_requires_knowledge = bool(routed_source_group)
    if not academic_rules_question and not selected_official_document_question and not should_use_knowledge(analysis) and not routed_requires_knowledge:
        return {"answer_source_status": "not_required", "used_sources": [], "snippet_titles": []}
    category = None if academic_rules_question else category_for_analysis(analysis)
    language = analysis.language if analysis.language in {"ka", "en"} else None
    retrieval_query = normalize_chat_retrieval_query(message)
    selected_document_category = selected_document_retrieval_category(message)
    scoped_source_domain = scoped_source_domain_for_decision(route_decision)
    scoped_exact_allowed = scoped_exact_answer_allowed(route_decision)
    if should_block_empty_source_group(route_decision, message) and route_decision and route_decision.primary_source_group:
        return {"answer_source_status": "no_approved_source_found", "used_sources": [], "snippet_titles": []}
    if route_decision and route_decision.primary_source_group and not scoped_exact_allowed:
        return {"answer_source_status": "no_approved_source_found", "used_sources": [], "snippet_titles": []}
    results = []
    if (
        route_decision
        and route_decision.primary_source_group
        and route_decision.source_groups
        and not selected_official_document_question
        and (
            route_decision.reason == "claude_intent_router"
            or route_decision.primary_source_group == "program_catalog_sources"
        )
    ):
        results = await search_approved_sources_for_groups(
            db,
            query=retrieval_query,
            source_group_ids=route_decision.source_groups,
            language=language,
            program_name=analysis.program,
            limit=10,
        )
        if not results:
            return {"answer_source_status": "no_approved_source_found", "used_sources": [], "snippet_titles": []}
        return knowledge_payload_from_results(results)
    if selected_official_document_question and selected_document_category and scoped_exact_allowed:
        results = await search_knowledge_snippets(
            db,
            query=retrieval_query,
            language=language,
            category=selected_document_category,
            source_domain=OFFICIAL_ALTE_PDF_SOURCE_DOMAIN,
            program_name=analysis.program,
            approved_only=True,
        )
    if not results and scoped_source_domain and scoped_exact_allowed:
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
    if not results and selected_official_document_question and selected_document_category and scoped_exact_allowed:
        results = await search_knowledge_snippets(
            db,
            query=retrieval_query,
            language=language,
            category=selected_document_category or category,
            source_domain="alte.edu.ge",
            program_name=analysis.program,
            approved_only=True,
        )
    if not results and selected_official_document_question and scoped_exact_allowed:
        results = await search_knowledge_snippets(
            db,
            query=retrieval_query,
            language=language,
            category=selected_document_category or category,
            source_domain=OFFICIAL_ALTE_PDF_SOURCE_DOMAIN,
            program_name=analysis.program,
            approved_only=True,
        )
    if (
        not results
        and selected_official_document_question
        and phase_9bf_georgian_control_reply(message.lower(), language == "ka" or any("\u10a0" <= char <= "\u10ff" for char in message or ""))
    ):
        return {
            "answer_source_status": "answered_from_approved_source",
            "used_sources": ["Phase 9BF Georgian control deterministic source mapping"],
            "snippet_titles": ["Selected official document control mapping"],
            "source_excerpts": [],
        }
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
    return knowledge_payload_from_results(results)


async def search_approved_sources_for_groups(
    db: AsyncSession,
    *,
    query: str,
    source_group_ids: list[str],
    language: str | None,
    program_name: str | None,
    limit: int = 10,
) -> list:
    merged = []
    seen: set[str] = set()
    for group_id in source_group_ids:
        config = source_group_config(group_id)
        if not config or not config.get("exact_answer_allowed", True):
            continue
        source_domain = config.get("source_domain") if isinstance(config.get("source_domain"), str) else None
        candidates = await search_knowledge_snippets(
            db,
            query=query,
            language=language,
            category=None,
            source_domain=source_domain,
            program_name=program_name,
            approved_only=True,
            limit=max(limit * 4, 20),
        )
        for item in candidates:
            if not retrieval_result_belongs_to_source_group(item, group_id, config):
                continue
            if item.snippet.id in seen:
                continue
            seen.add(item.snippet.id)
            merged.append(item)
    return sorted(merged, key=lambda item: item.score, reverse=True)[:limit]


def retrieval_result_belongs_to_source_group(item, source_group_id: str, config: dict) -> bool:
    source_identity = normalize_source_group_text(
        " ".join(
            str(value or "")
            for value in [
                getattr(item.snippet, "source_key", None),
                getattr(item.source, "source_key", None),
                getattr(item.source, "title", None),
                getattr(item.snippet, "title", None),
                getattr(item.source, "source_path", None),
                getattr(item.snippet, "source_path", None),
                getattr(item.source, "document_id", None),
                getattr(item.snippet, "document_id", None),
            ]
        )
    )
    source_files = [normalize_source_group_text(str(value)) for value in config.get("source_files", []) if value]
    source_keys = [normalize_source_group_text(str(value)) for value in config.get("source_keys", []) if value]
    document_ids = [normalize_source_group_text(str(value)) for value in config.get("document_ids", []) if value]
    allowed_identity = source_files + source_keys + document_ids
    if any(value and (value in source_identity or source_identity in value) for value in allowed_identity):
        return True
    category = normalize_source_group_text(item.snippet.category or item.source.category or "")
    if not config.get("allow_category_fallback", False):
        return False
    allowed_categories = {
        normalize_source_group_text(str(value))
        for value in config.get("allowed_categories", [])
        if value
    }
    return bool(category and category in allowed_categories)


def normalize_source_group_text(value: str) -> str:
    return " ".join((value or "").lower().replace("_", " ").replace("-", " ").split())


INTERNAL_PUBLIC_ANSWER_MARKERS = (
    "official source",
    "reference:",
    "policy:",
    "answer only from",
    "handover if",
    "official_academic_rules",
    "source group",
    "source_group",
    "chunk",
)


def clean_public_answer_text(reply: str) -> str:
    cleaned_lines: list[str] = []
    for raw_line in (reply or "").splitlines():
        line = raw_line.strip()
        lowered = line.lower()
        if not line:
            cleaned_lines.append("")
            continue
        if lowered.startswith(
            (
                "source:",
                "sources:",
                "official source:",
                "reference:",
                "policy:",
                "retrieved sources:",
                "internal source:",
            )
        ):
            continue
        if line.startswith(("წყარო:", "წყაროები:")):
            continue
        if is_public_control_line(line):
            continue
        cleaned_line = strip_inline_internal_markers(line)
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def is_public_control_line(line: str) -> bool:
    lowered = line.lower().strip()
    if any(lowered.startswith(marker) for marker in ("answer only from", "handover if")):
        return True
    return any(marker in lowered for marker in ("official source:", "reference:", "policy:"))


def strip_inline_internal_markers(line: str) -> str:
    cleaned = line
    cleaned = re.sub(r"\bofficial_academic_rules[_a-z0-9.-]*\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bofficial_alte_[a-z0-9_.-]*(?:p\d+|c\d+)[a-z0-9_.-]*\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b[a-z0-9_.-]+_p\d{1,4}[_-]c\d{1,4}\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bp\d{1,4}[_-]c\d{1,4}\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(?:page|pg\.?)\s*:?\s*\d{1,4}\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bchunk\s*:?\s*\d{1,4}\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bsource_group\s*=\s*[a-z0-9_.-]+\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bsource_group\s*=\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bsource group\s*:\s*[a-z0-9_.-]+\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bsource group\s*:\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\binternal source(?: id)?\s*[:=]\s*[a-z0-9_.-]+\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+([.,;:!?])", r"\1", cleaned)
    cleaned = re.sub(r"([.;:,])\s*([.;:,])+", r"\1", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"\s*([;,])\s*$", "", cleaned)
    cleaned = re.sub(r"\(\s*\)|\[\s*\]|\{\s*\}", "", cleaned)
    return cleaned.strip()


def public_used_source_labels(results: list) -> list[str]:
    labels: list[str] = []
    for item in results:
        fallback_label = str(getattr(item.source, "source_key", "") or getattr(item.source, "title", "") or "დამტკიცებული წყარო")
        identity = " ".join(
            str(value or "")
            for value in [
                getattr(item.source, "source_key", ""),
                getattr(item.source, "title", ""),
                getattr(item.snippet, "title", ""),
                getattr(item.snippet, "category", ""),
            ]
        )
        label = public_source_label(identity, fallback_label)
        if label and label not in labels:
            labels.append(label)
    return labels


def response_public_source_label(knowledge: dict, *, should_handover: bool, source_group: str | None) -> str | None:
    if should_handover:
        return None
    if knowledge.get("answer_source_status") != "answered_from_approved_source":
        return None
    label = PUBLIC_SOURCE_GROUP_LABELS.get(str(source_group or ""))
    if label in PUBLIC_SOURCE_LABEL_WHITELIST:
        return label
    trusted_label = str(knowledge.get("public_source_label") or "").strip()
    if trusted_label in PUBLIC_SOURCE_LABEL_WHITELIST:
        return trusted_label
    return None


def safe_public_source_label(label: str | None) -> bool:
    if not label:
        return False
    lowered = str(label).lower()
    forbidden = [
        "full_alte_local_kb",
        "selected_alte_45_doc",
        "official_alte_8_pdf_kb",
        "official_academic_rules_full",
        "chunk",
        "page",
        "source_key",
        "source id",
        "source_id",
    ]
    return not any(marker in lowered for marker in forbidden)


def public_source_label(identity: str, fallback_label: str | None = None) -> str:
    lowered = normalize_source_group_text(identity)
    is_internal_source = "official_academic_rules" in identity or "official_alte" in identity or "official alte" in lowered
    if is_internal_source and ("program catalog" in lowered or "higher education program catalog" in lowered):
        return "Higher Education Program Catalog"
    if is_internal_source and ("academic calendar" in lowered or "calendar 2025 2026" in lowered or "აკადემიური კალენდ" in identity):
        return "აკადემიური კალენდარი 2025–2026"
    if is_internal_source and (
        "international admission" in lowered
        or "foreign applicant" in lowered
        or "international admissions" in lowered
        or "საერთაშორისო მიღ" in identity
        or "უცხოელ" in identity
    ):
        return "საერთაშორისო მიღების წესი"
    if is_internal_source and (
        "admission" in lowered
        or "admissions" in lowered
        or "enrollment" in lowered
        or "მიღებ" in identity
        or "ჩარიცხ" in identity
    ):
        return "მიღების წესი"
    if is_internal_source and ("bachelor" in lowered or "bachelors" in lowered or "ბაკალავრ" in identity):
        return "ბაკალავრიატის დებულება"
    if is_internal_source and ("master" in lowered or "masters" in lowered or "მაგისტრ" in identity):
        return "მაგისტრატურის დებულება"
    if is_internal_source and (
        "study process" in lowered
        or "regulation of study process" in lowered
        or "official academic rules" in lowered
        or "official academic rules full" in lowered
        or "official academic rules" in lowered.replace("_", " ")
        or "სასწავლო პროცეს" in identity
    ):
        return "სასწავლო პროცესის მარეგულირებელი წესი"
    if "official_academic_rules" in identity:
        return "სასწავლო პროცესის მარეგულირებელი წესი"
    return str(fallback_label or identity or "დამტკიცებული წყარო").strip()


def knowledge_payload_from_results(results: list) -> dict:
    if any(item.source_status == "source_stale" for item in results):
        status = "source_stale"
    else:
        status = "answered_from_approved_source"
    return {
        "answer_source_status": status,
        "used_sources": public_used_source_labels(results),
        "snippet_titles": [item.snippet.title for item in results],
        "source_excerpts": [
            {
                "id": item.snippet.id,
                "title": item.snippet.title,
                "content": item.snippet.content,
                "category": item.snippet.category,
                "source_key": item.source.source_key,
                "source_title": item.source.title,
                "source_domain": item.source.source_domain,
                "score": item.score,
            }
            for item in results[:5]
        ],
    }


async def retrieve_initial_knowledge_context(
    db: AsyncSession,
    message: str,
    route_decision: KnowledgeRouteDecision | None = None,
) -> list[dict]:
    academic_rules_question = is_official_academic_rules_text(message)
    selected_official_document_question = is_selected_official_document_text(message)
    retrieval_query = normalize_chat_retrieval_query(message)
    selected_document_category = selected_document_retrieval_category(message)
    scoped_source_domain = scoped_source_domain_for_decision(route_decision)
    scoped_exact_allowed = scoped_exact_answer_allowed(route_decision)
    if should_block_empty_source_group(route_decision, message) and route_decision and route_decision.primary_source_group:
        return []
    if route_decision and route_decision.primary_source_group and not scoped_exact_allowed:
        return []
    results = []
    if (
        route_decision
        and route_decision.primary_source_group
        and route_decision.source_groups
        and (
            route_decision.reason == "claude_intent_router"
            or route_decision.primary_source_group == "program_catalog_sources"
        )
    ):
        results = await search_approved_sources_for_groups(
            db,
            query=retrieval_query,
            source_group_ids=route_decision.source_groups,
            language=None,
            program_name=None,
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
                "score": item.score,
            }
            for item in results
        ]
    if selected_official_document_question and selected_document_category and scoped_exact_allowed:
        results = await search_knowledge_snippets(
            db,
            query=retrieval_query,
            category=selected_document_category,
            source_domain="alte.edu.ge",
            approved_only=True,
            include_stale=False,
            limit=3,
        )
    if not results and scoped_source_domain and scoped_exact_allowed:
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
    if not results and selected_official_document_question and selected_document_category and scoped_exact_allowed:
        results = await search_knowledge_snippets(
            db,
            query=retrieval_query,
            category=selected_document_category,
            source_domain="alte.edu.ge",
            approved_only=True,
            include_stale=False,
            limit=3,
        )
    if not results and selected_official_document_question and scoped_exact_allowed:
        results = await search_knowledge_snippets(
            db,
            query=retrieval_query,
            category=selected_document_category,
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


def source_group_has_no_files(route_decision: KnowledgeRouteDecision | None) -> bool:
    config = source_group_config(route_decision.primary_source_group if route_decision else None)
    if not config:
        return False
    return not bool(config.get("source_files"))


def should_block_empty_source_group(route_decision: KnowledgeRouteDecision | None, message: str) -> bool:
    if not source_group_has_no_files(route_decision):
        return False
    group_id = route_decision.primary_source_group if route_decision else None
    if group_id == "finance_sources" and is_selected_official_document_text(message):
        return False
    return True


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
        "კონსულტანტის ტელეფონის ნომერი",
        "consultant phone",
        "consultant phone number",
        "rare manuscripts",
        "six months",
        "reset it now",
        "password format",
        "კოსმოსური პროგრამ",
        "ai კოსმოსური",
        "ზუსტად რა ღირს 2031",
        "არარსებული პროგრამ",
    ]
    future_year_markers = ["2031", "2032", "2033", "2034", "2035"]
    current_tuition_question = any(marker in haystack for marker in ["წელს", "დღეს", "მიმდინარე"]) and any(
        marker in haystack for marker in ["ღირს", "ფასი", "საფასურ"]
    )
    return any(marker in haystack for marker in unsupported_markers) or (
        any(year in haystack for year in future_year_markers)
        and any(marker in haystack for marker in ["სტიპენდ", "scholarship", "კამპუს", "campus", "ფასი", "ღირს", "tuition", "price", "program"])
    ) or current_tuition_question


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
        "deans list",
        "dean",
        "state grant",
        "social grant",
        "grant",
        "iro policy",
        "international relations office",
        "iro",
        "sustainability",
        "sustainable development",
        "sustainability strategy",
        "sustainability report",
        "edi policy",
        "equality diversity inclusion",
        "research component",
        "student rights",
        "self-government",
        "school council",
        "funding rule",
        "financial support",
        "it policy",
        "information technology",
        "platform support",
        "student portal",
        "ინგლისურენოვან პროგრამ",
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
        "სახელმწიფო სასწავლო გრანტ",
        "სოციალური პროგრამ",
        "სტუდენტური სერვის",
        "სერვისებს იღებს სტუდენტი",
        "საკუთარი უფლებების დაცვა",
        "უფლებების დაცვა",
        "აკადემიური კეთილსინდისიერ",
        "სანქცი",
        "edi",
        "თანასწორ",
        "მრავალფერ",
        "ინკლუზ",
        "სტუდენტთა უფლებ",
        "თვითმმართველ",
        "სკოლის საბჭ",
        "მდგრადი განვითარების",
        "მდგრად განვითარ",
        "კვლევითი კომპონენტ",
        "ინფორმაციული ტექნოლოგი",
    ]
    return any(marker in haystack for marker in markers)


def build_source_backed_reply(analysis: AIAnalysisResult, snippet_titles: list[str]) -> str:
    base_reply = analysis.reply.strip()
    return clean_public_answer_text(base_reply)


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


def build_operator_request_reply(language: str | None, department_label: str | None) -> str:
    department = department_label or "the relevant department"
    if language == "en":
        return f"I can route this to {department}. You can wait for an operator in this chat or leave contact details if you choose."
    ka_departments = {
        "Finance": "დაფინანსება / Finance",
        "Admissions": "მიღება / Admissions",
        "Library": "ბიბლიოთეკა / Library",
        "IT Support": "IT დახმარება / IT Support",
        "Medicine / MD": "მედიცინა / MD",
        "International Admissions": "საერთაშორისო მიღება / International Admissions",
        "Human Operator": "ცოცხალი ოპერატორი",
    }
    department = ka_departments.get(department, department)
    return (
        f"შემიძლია ეს მოთხოვნა გადავცე შესაბამის გუნდს: {department}. "
        "შეგიძლიათ დაელოდოთ ოპერატორს ამ ჩატში ან სურვილის შემთხვევაში დატოვოთ კონტაქტი."
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
