from __future__ import annotations

import json
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError, field_validator

from app.core.ai_client import get_ai_client
from app.core.config import get_settings
from app.services.ai_service import extract_response_text, parse_json_object
from app.services.knowledge_routing_service import (
    KnowledgeRouteDecision,
    classify_knowledge_route,
    detect_language,
    format_clarification_reply,
    load_source_groups,
    source_group_config,
)

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "knowledge"
SOURCE_GROUP_DESCRIPTIONS_PATH = DATA_DIR / "source_group_descriptions.json"

PUBLIC_DEPARTMENT_LABELS = {
    "admissions": "Admissions",
    "programs": "Programs",
    "finance": "Finance",
    "international_admissions": "International Admissions",
    "medicine_md": "Medicine / MD",
    "library": "Library",
    "career": "Career",
    "it_support": "IT Support",
    "human_operator": "Human Operator",
    "study_process": "Study Process",
    "academic_calendar": "Study Process",
}

DEPARTMENT_ALIASES = {
    "admission": "admissions",
    "admissions": "admissions",
    "program": "programs",
    "programs": "programs",
    "finance": "finance",
    "funding": "finance",
    "international": "international_admissions",
    "international_admissions": "international_admissions",
    "medicine": "medicine_md",
    "medicine_md": "medicine_md",
    "md": "medicine_md",
    "library": "library",
    "career": "career",
    "it": "it_support",
    "it_support": "it_support",
    "operator": "human_operator",
    "human": "human_operator",
    "human_operator": "human_operator",
    "study_process": "study_process",
    "student_status": "study_process",
    "academic_calendar": "academic_calendar",
}

BROAD_QUESTIONS = {
    "სწავლა მაინტერესებს": (
        "admissions",
        "ზუსტად რომ გიპასუხოთ, გთხოვთ დააზუსტოთ — რომელი საკითხი გაინტერესებთ?",
        ["მიღება", "პროგრამები", "სწავლის საფასური", "სტუდენტის სტატუსი"],
    ),
    "პროგრამები მაინტერესებს": (
        "programs",
        "რომელ პროგრამაზე გსურთ ინფორმაცია — ბაკალავრიატზე, მაგისტრატურაზე, მედიცინა / MD-ზე თუ საერთაშორისო მიღებაზე?",
        ["ბაკალავრიატი", "მაგისტრატურა", "მედიცინა / MD", "საერთაშორისო მიღება"],
    ),
    "მიღება მაინტერესებს": (
        "admissions",
        "გთხოვთ დააზუსტოთ: ბაკალავრიატი, მაგისტრატურა, საერთაშორისო მიღება, საბუთები თუ გამოცდების გარეშე ჩარიცხვა გაინტერესებთ?",
        ["ბაკალავრიატი", "მაგისტრატურა", "საერთაშორისო მიღება", "საბუთები", "გამოცდების გარეშე ჩარიცხვა"],
    ),
    "გადახდებზე მაინტერესებს": (
        "finance",
        "გადახდებზე რომ გიპასუხოთ, გთხოვთ დააზუსტოთ: სწავლის საფასური გაინტერესებთ, გადახდის გრაფიკი თუ ფინანსურ დეპარტამენტთან დაკავშირება?",
        ["სწავლის საფასური", "გადახდის გრაფიკი", "ფინანსურ დეპარტამენტთან დაკავშირება"],
    ),
    "სტატუსზე მაქვს კითხვა": (
        "study_process",
        "სტუდენტის სტატუსთან დაკავშირებით რომ გიპასუხოთ, გთხოვთ დააზუსტოთ: შეჩერება, აღდგენა, შეწყვეტა თუ მობილობა გაინტერესებთ?",
        ["შეჩერება", "აღდგენა", "შეწყვეტა", "მობილობა"],
    ),
    "სტატუსზე კითხვა მაქვს": (
        "study_process",
        "სტუდენტის სტატუსთან დაკავშირებით რა გაინტერესებთ — შეჩერება, აღდგენა, შეწყვეტა თუ მობილობა?",
        ["შეჩერება", "აღდგენა", "შეწყვეტა", "მობილობა"],
    ),
    "გამოცდებზე მაინტერესებს": (
        "study_process",
        "გთხოვთ დააზუსტოთ: გამოცდების თარიღები გაინტერესებთ, გამოცდაზე დაშვების წესი, შეფასება თუ გადაბარება?",
        ["გამოცდების თარიღები", "დაშვების წესი", "შეფასება", "გადაბარება"],
    ),
    "პროგრამის კრედიტები მაინტერესებს": (
        "programs",
        "რომელ პროგრამას გულისხმობთ? რომელი პროგრამის კრედიტები გაინტერესებთ — ბაკალავრიატი, მაგისტრატურა, მედიცინა / MD, სტომატოლოგია თუ კონკრეტული პროგრამა?",
        ["ბაკალავრიატი (240 ECTS)", "მაგისტრატურა (120 ECTS)", "მედიცინა / MD", "სტომატოლოგია", "კონკრეტული პროგრამა"],
    ),
    "რამდენი კრედიტია პროგრამა": (
        "programs",
        "რომელ პროგრამას გულისხმობთ? რომელი პროგრამის კრედიტები გაინტერესებთ — ბაკალავრიატი, მაგისტრატურა, მედიცინა / MD, სტომატოლოგია თუ კონკრეტული პროგრამა?",
        ["ბაკალავრიატი (240 ECTS)", "მაგისტრატურა (120 ECTS)", "მედიცინა / MD", "სტომატოლოგია", "კონკრეტული პროგრამა"],
    ),
    "დახმარება მინდა": (
        "admissions",
        "ზუსტად რომ გიპასუხოთ, გთხოვთ დააზუსტოთ, რა სახის დახმარება გჭირდებათ: მიღება, პროგრამები, ფინანსები, IT დახმარება თუ ოპერატორთან დაკავშირება?",
        ["მიღება", "პროგრამები", "ფინანსები", "IT დახმარება", "ოპერატორი"],
    ),
    "i need information about studying": (
        "admissions",
        "Please clarify which topic you mean.",
        ["Admissions", "Programs", "Tuition/Finance", "Student status"],
    ),
    "i have a question about payment": (
        "finance",
        "To answer about payments, please clarify: tuition, payment schedule, or contacting the finance department?",
        ["Tuition", "Payment schedule", "Finance department"],
    ),
}


class ClaudeIntentRoute(BaseModel):
    intent: str = "information_request"
    language: str = "unknown"
    department: str = "admissions"
    public_department_label: str = "Admissions"
    topic: str = "general"
    needs_clarification: bool = False
    clarification_question: str | None = None
    clarification_options: list[str] = Field(default_factory=list)
    source_groups_to_search: list[str] = Field(default_factory=list)
    search_terms: list[str] = Field(default_factory=list)
    operator_needed: bool = False
    operator_reason: str | None = None
    unsupported_likely: bool = False
    confidence: float = 0.0
    fallback_used: bool = False
    router_validation_status: str = "valid"
    deterministic_override_applied: bool = False
    deterministic_override_reason: str = "none"

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        return value if value in {"ka", "en", "unknown"} else "unknown"

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, value: float) -> float:
        return max(0.0, min(1.0, float(value)))


@lru_cache(maxsize=1)
def load_source_group_descriptions() -> dict[str, dict[str, Any]]:
    raw = json.loads(SOURCE_GROUP_DESCRIPTIONS_PATH.read_text(encoding="utf-8"))
    groups = raw.get("source_groups", [])
    if not isinstance(groups, list):
        return {}
    return {str(item.get("id")): item for item in groups if isinstance(item, dict) and item.get("id")}


def allowed_source_group_ids() -> set[str]:
    configured = {item.get("id") for item in load_source_groups().get("source_groups", []) if isinstance(item, dict)}
    described = set(load_source_group_descriptions())
    return {str(item) for item in configured.intersection(described) if item}


def route_with_claude_intent(
    message: str,
    *,
    selected_department: str | None = None,
    source_domain: str | None = None,
    language_hint: str | None = None,
    conversation_history: list[dict[str, str]] | None = None,
) -> tuple[ClaudeIntentRoute, dict[str, Any]]:
    settings = get_settings()
    provider = settings.AI_PROVIDER.lower().strip()
    if provider != "claude":
        route = fallback_intent_route(message, selected_department=selected_department, source_domain=source_domain)
        return route, {
            "provider": "mock",
            "model": "deterministic_intent_router",
            "fallback": True,
            "raw_response": None,
            "router_validation_status": route.router_validation_status,
            "deterministic_override_applied": route.deterministic_override_applied,
            "deterministic_override_reason": route.deterministic_override_reason,
        }

    try:
        raw_text = call_claude_intent_router(
            message,
            selected_department=selected_department,
            source_domain=source_domain,
            language_hint=language_hint,
            conversation_history=conversation_history or [],
        )
        raw_json = parse_json_object(raw_text)
        route = validate_router_payload(raw_json, message=message)
        return route, {
            "provider": "claude",
            "model": settings.AI_MODEL,
            "fallback": False,
            "raw_response": raw_json,
            "router_validation_status": route.router_validation_status,
            "deterministic_override_applied": route.deterministic_override_applied,
            "deterministic_override_reason": route.deterministic_override_reason,
        }
    except (ValueError, ValidationError, TypeError, RuntimeError) as exc:
        logger.warning("Claude intent router fallback: %s", type(exc).__name__)
        route = fallback_intent_route(message, selected_department=selected_department, source_domain=source_domain)
        return route, {
            "provider": "claude",
            "model": settings.AI_MODEL,
            "fallback": True,
            "raw_response": None,
            "error_type": type(exc).__name__,
            "router_validation_status": route.router_validation_status,
            "deterministic_override_applied": route.deterministic_override_applied,
            "deterministic_override_reason": route.deterministic_override_reason,
        }
    except Exception as exc:
        logger.warning("Claude intent router unavailable fallback: %s", type(exc).__name__)
        route = fallback_intent_route(message, selected_department=selected_department, source_domain=source_domain)
        return route, {
            "provider": "claude",
            "model": settings.AI_MODEL,
            "fallback": True,
            "raw_response": None,
            "error_type": type(exc).__name__,
            "router_validation_status": route.router_validation_status,
            "deterministic_override_applied": route.deterministic_override_applied,
            "deterministic_override_reason": route.deterministic_override_reason,
        }


def call_claude_intent_router(
    message: str,
    *,
    selected_department: str | None,
    source_domain: str | None,
    language_hint: str | None,
    conversation_history: list[dict[str, str]],
) -> str:
    settings = get_settings()
    handle = get_ai_client()
    prompt_payload = {
        "task": "Classify the user's question. Do not answer the user.",
        "strict_output": {
            "intent": "string",
            "language": "ka|en",
            "department": "known department id",
            "public_department_label": "string",
            "topic": "string",
            "needs_clarification": "boolean",
            "clarification_question": "string|null",
            "clarification_options": ["string"],
            "source_groups_to_search": ["allowed source group id"],
            "search_terms": ["string"],
            "operator_needed": "boolean",
            "operator_reason": "string|null",
            "unsupported_likely": "boolean",
            "confidence": "float 0..1"
        },
        "rules": [
            "Return JSON only.",
            "Do not answer the user's question.",
            "Use only source group ids listed in source_group_descriptions.",
            "If the question is broad, set needs_clarification true and do not select broad retrieval.",
            "If the user asks for human/operator/contact, set operator_needed true.",
            "If the question is fake, future, or unsupported, set unsupported_likely true or confidence low.",
            "Select at most 3 source groups."
        ],
        "message": message,
        "source_domain": source_domain,
        "selected_department": selected_department,
        "language_hint": language_hint,
        "conversation_history": conversation_history[-6:],
        "public_departments": PUBLIC_DEPARTMENT_LABELS,
        "source_group_descriptions": load_source_group_descriptions(),
    }
    response = handle.client.messages.create(
        model=settings.AI_MODEL,
        max_tokens=min(settings.AI_MAX_TOKENS, 1200),
        system=(
            "You are Alte University's intent router. You classify user intent and select approved source groups. "
            "You never answer the user and you never invent source group ids."
        ),
        messages=[{"role": "user", "content": json.dumps(prompt_payload, ensure_ascii=False)}],
        timeout=settings.AI_TIMEOUT_SECONDS,
    )
    return extract_response_text(response)


def validate_router_payload(payload: dict[str, Any], *, message: str) -> ClaudeIntentRoute:
    route = ClaudeIntentRoute.model_validate(payload)
    language = route.language if route.language in {"ka", "en"} else detect_language(message)
    lowered = " ".join((message or "").lower().split())
    department = normalize_department(route.department)
    allowed = allowed_source_group_ids()
    requested_groups = unique_preserve_order(route.source_groups_to_search)
    source_groups = unique_preserve_order(group for group in requested_groups if group in allowed)[:3]
    invalid_groups = [group for group in requested_groups if group not in allowed]
    validation_status = "valid"
    if invalid_groups:
        validation_status = "invalid_source_groups"
    if not source_groups and not route.needs_clarification and not route.operator_needed:
        validation_status = "empty_source_groups" if not invalid_groups else "invalid_source_groups"
    if route.needs_clarification:
        source_groups = []
    if route.operator_needed and not source_groups:
        source_groups = []
    label = PUBLIC_DEPARTMENT_LABELS.get(department, route.public_department_label or department)
    override = deterministic_override_for_message(lowered, language)
    if override:
        return override
    if validation_status == "valid":
        source_groups = specialize_source_groups_for_message(lowered, source_groups)
    if source_groups:
        department = department_for_specialized_route(lowered, source_groups, department)
        label = PUBLIC_DEPARTMENT_LABELS.get(department, label)
    return route.model_copy(
        update={
            "language": language,
            "department": department,
            "public_department_label": label,
            "source_groups_to_search": source_groups,
            "clarification_options": route.clarification_options[:6],
            "search_terms": unique_preserve_order(route.search_terms)[:8],
            "router_validation_status": validation_status,
            "deterministic_override_applied": False,
            "deterministic_override_reason": "none",
        }
    )


def deterministic_override_for_message(lowered: str, language: str) -> ClaudeIntentRoute | None:
    if has_operator_request(lowered):
        department = department_for_operator_request(lowered)
        return ClaudeIntentRoute(
            intent="operator_request",
            language=language,
            department=department,
            public_department_label=PUBLIC_DEPARTMENT_LABELS.get(department, "Human Operator"),
            topic="explicit_operator_request",
            needs_clarification=False,
            clarification_question=None,
            clarification_options=[],
            source_groups_to_search=[],
            search_terms=[],
            operator_needed=True,
            operator_reason="explicit_operator_request",
            unsupported_likely=False,
            confidence=1.0,
            fallback_used=False,
            router_validation_status="valid",
            deterministic_override_applied=True,
            deterministic_override_reason="explicit_operator_request",
        )
    deadline_clarification = admissions_deadline_clarification(lowered, language)
    if deadline_clarification:
        department, question, options = deadline_clarification
        return ClaudeIntentRoute(
            intent="clarification",
            language=language,
            department=department,
            public_department_label=PUBLIC_DEPARTMENT_LABELS.get(department, "Admissions"),
            topic="admissions_deadline_ambiguous",
            needs_clarification=True,
            clarification_question=question,
            clarification_options=options,
            source_groups_to_search=[],
            search_terms=[],
            operator_needed=False,
            operator_reason=None,
            unsupported_likely=False,
            confidence=1.0,
            fallback_used=False,
            router_validation_status="valid",
            deterministic_override_applied=True,
            deterministic_override_reason="admissions_deadline_clarification",
        )
    tuition_clarification = medical_tuition_clarification(lowered, language)
    if tuition_clarification:
        department, question, options = tuition_clarification
        return ClaudeIntentRoute(
            intent="clarification",
            language=language,
            department=department,
            public_department_label=PUBLIC_DEPARTMENT_LABELS.get(department, "Finance"),
            topic="medical_tuition_clarification",
            needs_clarification=True,
            clarification_question=question,
            clarification_options=options,
            source_groups_to_search=[],
            search_terms=[],
            operator_needed=False,
            operator_reason=None,
            unsupported_likely=False,
            confidence=1.0,
            fallback_used=False,
            router_validation_status="valid",
            deterministic_override_applied=True,
            deterministic_override_reason="medical_tuition_clarification",
        )
    broad = known_broad_question(lowered)
    if broad:
        department, question, options = broad
        return ClaudeIntentRoute(
            intent="clarification",
            language=language,
            department=department,
            public_department_label=PUBLIC_DEPARTMENT_LABELS.get(department, "Admissions"),
            topic="broad_question",
            needs_clarification=True,
            clarification_question=question,
            clarification_options=options,
            source_groups_to_search=[],
            search_terms=[],
            operator_needed=False,
            operator_reason=None,
            unsupported_likely=False,
            confidence=1.0,
            fallback_used=False,
            router_validation_status="valid",
            deterministic_override_applied=True,
            deterministic_override_reason="known_broad_question",
        )
    if has_unsupported_marker(lowered):
        department = department_for_unsupported(lowered)
        return ClaudeIntentRoute(
            intent="unsupported_or_unverified",
            language=language,
            department=department,
            public_department_label=PUBLIC_DEPARTMENT_LABELS.get(department, "Admissions"),
            topic="unsupported_high_risk",
            needs_clarification=False,
            clarification_question=None,
            clarification_options=[],
            source_groups_to_search=[],
            search_terms=[],
            operator_needed=False,
            operator_reason=None,
            unsupported_likely=True,
            confidence=0.95,
            fallback_used=False,
            router_validation_status="valid",
            deterministic_override_applied=True,
            deterministic_override_reason="unsupported_high_risk",
        )
    return None


def fallback_intent_route(
    message: str,
    *,
    selected_department: str | None = None,
    source_domain: str | None = None,
) -> ClaudeIntentRoute:
    language = detect_language(message)
    lowered = " ".join((message or "").lower().split())
    deadline_clarification = admissions_deadline_clarification(lowered, language)
    if deadline_clarification:
        department, question, options = deadline_clarification
        return ClaudeIntentRoute(
            intent="clarification",
            language=language,
            department=department,
            public_department_label=PUBLIC_DEPARTMENT_LABELS.get(department, "Admissions"),
            topic="admissions_deadline_ambiguous",
            needs_clarification=True,
            clarification_question=question,
            clarification_options=options,
            source_groups_to_search=[],
            operator_needed=False,
            unsupported_likely=False,
            confidence=1.0,
            fallback_used=True,
            router_validation_status="fallback_used",
            deterministic_override_applied=True,
            deterministic_override_reason="admissions_deadline_clarification",
        )
    tuition_clarification = medical_tuition_clarification(lowered, language)
    if tuition_clarification:
        department, question, options = tuition_clarification
        return ClaudeIntentRoute(
            intent="clarification",
            language=language,
            department=department,
            public_department_label=PUBLIC_DEPARTMENT_LABELS.get(department, "Finance"),
            topic="medical_tuition_clarification",
            needs_clarification=True,
            clarification_question=question,
            clarification_options=options,
            source_groups_to_search=[],
            operator_needed=False,
            unsupported_likely=False,
            confidence=1.0,
            fallback_used=True,
            router_validation_status="fallback_used",
            deterministic_override_applied=True,
            deterministic_override_reason="medical_tuition_clarification",
        )
    broad = known_broad_question(lowered)
    if broad:
        department, question, options = broad
        return ClaudeIntentRoute(
            intent="clarification",
            language=language,
            department=department,
            public_department_label=PUBLIC_DEPARTMENT_LABELS.get(department, "Admissions"),
            topic="broad_question",
            needs_clarification=True,
            clarification_question=question,
            clarification_options=options,
            source_groups_to_search=[],
            operator_needed=False,
            unsupported_likely=False,
            confidence=1.0,
            fallback_used=True,
            router_validation_status="fallback_used",
        )

    operator_needed = has_operator_request(lowered)
    if operator_needed:
        department = department_for_operator_request(lowered)
        return ClaudeIntentRoute(
            intent="operator_request",
            language=language,
            department=department,
            public_department_label=PUBLIC_DEPARTMENT_LABELS.get(department, "Human Operator"),
            topic="explicit_operator_request",
            needs_clarification=False,
            clarification_question=None,
            clarification_options=[],
            source_groups_to_search=[],
            search_terms=[],
            operator_needed=True,
            operator_reason="explicit_operator_request",
            unsupported_likely=False,
            confidence=1.0,
            fallback_used=True,
            router_validation_status="fallback_used",
        )

    unsupported_likely = has_unsupported_marker(lowered)
    if unsupported_likely:
        return ClaudeIntentRoute(
            intent="unsupported_or_unverified",
            language=language,
            department=department_for_unsupported(lowered),
            public_department_label=PUBLIC_DEPARTMENT_LABELS.get(department_for_unsupported(lowered), "Admissions"),
            topic="unsupported_likely",
            needs_clarification=False,
            clarification_question=None,
            clarification_options=[],
            source_groups_to_search=[],
            search_terms=[message],
            operator_needed=False,
            operator_reason=None,
            unsupported_likely=True,
            confidence=0.9,
            fallback_used=True,
            router_validation_status="fallback_used",
        )

    forced_group = forced_source_group(lowered)
    if forced_group:
        department = department_for_source_group(forced_group)
        return ClaudeIntentRoute(
            intent="information_request",
            language=language,
            department=department,
            public_department_label=PUBLIC_DEPARTMENT_LABELS.get(department, department),
            topic=forced_group,
            needs_clarification=False,
            clarification_question=None,
            clarification_options=[],
            source_groups_to_search=[forced_group],
            search_terms=[message],
            operator_needed=False,
            operator_reason=None,
            unsupported_likely=False,
            confidence=0.92,
            fallback_used=True,
            router_validation_status="fallback_used",
        )

    decision = classify_knowledge_route(message, selected_department=selected_department, source_domain=source_domain)
    source_groups = [] if unsupported_likely else [group for group in decision.source_groups if group in allowed_source_group_ids()]
    if source_groups:
        source_groups = specialize_source_groups_for_message(lowered, source_groups)
    department = department_for_specialized_route(lowered, source_groups, decision.department_id) if source_groups else decision.department_id
    return ClaudeIntentRoute(
        intent="information_request",
        language=decision.language,
        department=department,
        public_department_label=PUBLIC_DEPARTMENT_LABELS.get(department, decision.department_label),
        topic=decision.reason,
        needs_clarification=decision.clarification_required,
        clarification_question=decision.clarification_question,
        clarification_options=decision.clarification_options,
        source_groups_to_search=source_groups[:3],
        search_terms=[message],
        operator_needed=False,
        operator_reason=None,
        unsupported_likely=unsupported_likely,
        confidence=decision.confidence,
        fallback_used=True,
        router_validation_status="fallback_used",
    )


def route_decision_from_intent(route: ClaudeIntentRoute, fallback: KnowledgeRouteDecision) -> KnowledgeRouteDecision:
    if route.needs_clarification:
        return KnowledgeRouteDecision(
            department_id=route.department,
            department_label=route.public_department_label,
            source_groups=[],
            primary_source_group=None,
            clarification_required=True,
            clarification_question=route.clarification_question,
            clarification_options=route.clarification_options,
            language=route.language if route.language in {"ka", "en"} else fallback.language,
            confidence=route.confidence,
            reason="claude_intent_router_clarification",
        )
    source_groups = [group for group in route.source_groups_to_search if source_group_config(group)]
    if not source_groups and route.operator_needed:
        source_groups = []
    if (
        not source_groups
        and not route.operator_needed
        and not route.unsupported_likely
        and route.fallback_used
        and route.router_validation_status == "fallback_used"
    ):
        source_groups = fallback.source_groups
    return KnowledgeRouteDecision(
        department_id=route.department or fallback.department_id,
        department_label=route.public_department_label or fallback.department_label,
        source_groups=source_groups,
        primary_source_group=source_groups[0] if source_groups else None,
        clarification_required=False,
        clarification_question=None,
        clarification_options=[],
        language=route.language if route.language in {"ka", "en"} else fallback.language,
        confidence=route.confidence or fallback.confidence,
        reason="claude_intent_router" if not route.fallback_used else f"deterministic_router:{fallback.reason}",
    )


def format_router_clarification_reply(route: ClaudeIntentRoute) -> str:
    decision = KnowledgeRouteDecision(
        department_id=route.department,
        department_label=route.public_department_label,
        source_groups=[],
        primary_source_group=None,
        clarification_required=True,
        clarification_question=route.clarification_question,
        clarification_options=route.clarification_options,
        language=route.language,
        confidence=route.confidence,
        reason="claude_intent_router_clarification",
    )
    return format_clarification_reply(decision)


def normalize_department(value: str | None) -> str:
    if not value:
        return "admissions"
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    return DEPARTMENT_ALIASES.get(normalized, normalized if normalized in PUBLIC_DEPARTMENT_LABELS else "admissions")


def unique_preserve_order(values) -> list[str]:
    items: list[str] = []
    for value in values:
        if not value:
            continue
        text = str(value).strip()
        if text and text not in items:
            items.append(text)
    return items


def has_operator_request(lowered: str) -> bool:
    markers = [
        "operator",
        "human",
        "contact",
        "contact support",
        "connect me",
        "connect me to a human",
        "wait for operator",
        "\u10dd\u10de\u10d4\u10e0\u10d0\u10e2\u10dd\u10e0",
        "\u10d0\u10d3\u10d0\u10db\u10d8\u10d0\u10dc",
        "\u10d3\u10d0\u10d9\u10d0\u10d5\u10e8\u10d8\u10e0",
        "\u10d3\u10d0\u10db\u10d0\u10d9\u10d0\u10d5\u10e8\u10d8\u10e0",
        "\u10ea\u10dd\u10ea\u10ee\u10d0\u10da\u10d8 \u10dd\u10de\u10d4\u10e0\u10d0\u10e2\u10dd\u10e0",
        "\u10d9\u10dd\u10dc\u10e2\u10d0\u10e5\u10e2",
    ]
    return any(marker in lowered for marker in markers)


def known_broad_question(lowered: str):
    normalized = normalize_broad_question_text(lowered)
    calendar_broad = known_broad_calendar_question(normalized, detect_language(lowered))
    if calendar_broad:
        return calendar_broad
    if normalized == "\u10e1\u10ec\u10d0\u10d5\u10da\u10d0 \u10db\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10e1":
        return (
            "admissions",
            "\u10d6\u10e3\u10e1\u10e2\u10d0\u10d3 \u10e0\u10dd\u10db \u10d2\u10d8\u10de\u10d0\u10e1\u10e3\u10ee\u10dd\u10d7, \u10d2\u10d7\u10ee\u10dd\u10d5\u10d7 \u10d3\u10d0\u10d0\u10d6\u10e3\u10e1\u10e2\u10dd\u10d7 \u2014 \u10e0\u10dd\u10db\u10d4\u10da\u10d8 \u10e1\u10d0\u10d9\u10d8\u10d7\u10ee\u10d8 \u10d2\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10d7?",
            ["\u10db\u10d8\u10e6\u10d4\u10d1\u10d0", "\u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d4\u10d1\u10d8", "\u10e1\u10ec\u10d0\u10d5\u10da\u10d8\u10e1 \u10e1\u10d0\u10e4\u10d0\u10e1\u10e3\u10e0\u10d8", "\u10e1\u10e2\u10e3\u10d3\u10d4\u10dc\u10e2\u10d8\u10e1 \u10e1\u10e2\u10d0\u10e2\u10e3\u10e1\u10d8"],
        )
    if normalized == "\u10d2\u10d0\u10d3\u10d0\u10ee\u10d3\u10d4\u10d1\u10d6\u10d4 \u10db\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10e1":
        return (
            "finance",
            "\u10d2\u10d0\u10d3\u10d0\u10ee\u10d3\u10d4\u10d1\u10d6\u10d4 \u10e0\u10dd\u10db \u10d2\u10d8\u10de\u10d0\u10e1\u10e3\u10ee\u10dd\u10d7, \u10d2\u10d7\u10ee\u10dd\u10d5\u10d7 \u10d3\u10d0\u10d0\u10d6\u10e3\u10e1\u10e2\u10dd\u10d7: \u10e1\u10ec\u10d0\u10d5\u10da\u10d8\u10e1 \u10e1\u10d0\u10e4\u10d0\u10e1\u10e3\u10e0\u10d8 \u10d2\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10d7, \u10d2\u10d0\u10d3\u10d0\u10ee\u10d3\u10d8\u10e1 \u10d2\u10e0\u10d0\u10e4\u10d8\u10d9\u10d8 \u10d7\u10e3 \u10e4\u10d8\u10dc\u10d0\u10dc\u10e1\u10e3\u10e0 \u10d3\u10d4\u10de\u10d0\u10e0\u10e2\u10d0\u10db\u10d4\u10dc\u10e2\u10d7\u10d0\u10dc \u10d3\u10d0\u10d9\u10d0\u10d5\u10e8\u10d8\u10e0\u10d4\u10d1\u10d0?",
            ["\u10e1\u10ec\u10d0\u10d5\u10da\u10d8\u10e1 \u10e1\u10d0\u10e4\u10d0\u10e1\u10e3\u10e0\u10d8", "\u10d2\u10d0\u10d3\u10d0\u10ee\u10d3\u10d8\u10e1 \u10d2\u10e0\u10d0\u10e4\u10d8\u10d9\u10d8", "\u10e4\u10d8\u10dc\u10d0\u10dc\u10e1\u10e3\u10e0 \u10d3\u10d4\u10de\u10d0\u10e0\u10e2\u10d0\u10db\u10d4\u10dc\u10e2\u10d7\u10d0\u10dc \u10d3\u10d0\u10d9\u10d0\u10d5\u10e8\u10d8\u10e0\u10d4\u10d1\u10d0"],
        )
    if normalized == "\u10e1\u10e2\u10d0\u10e2\u10e3\u10e1\u10d6\u10d4 \u10db\u10d0\u10e5\u10d5\u10e1 \u10d9\u10d8\u10d7\u10ee\u10d5\u10d0":
        return (
            "study_process",
            "\u10e1\u10e2\u10e3\u10d3\u10d4\u10dc\u10e2\u10d8\u10e1 \u10e1\u10e2\u10d0\u10e2\u10e3\u10e1\u10d7\u10d0\u10dc \u10d3\u10d0\u10d9\u10d0\u10d5\u10e8\u10d8\u10e0\u10d4\u10d1\u10d8\u10d7 \u10e0\u10dd\u10db \u10d2\u10d8\u10de\u10d0\u10e1\u10e3\u10ee\u10dd\u10d7, \u10d2\u10d7\u10ee\u10dd\u10d5\u10d7 \u10d3\u10d0\u10d0\u10d6\u10e3\u10e1\u10e2\u10dd\u10d7: \u10e8\u10d4\u10e9\u10d4\u10e0\u10d4\u10d1\u10d0, \u10d0\u10e6\u10d3\u10d2\u10d4\u10dc\u10d0, \u10e8\u10d4\u10ec\u10e7\u10d5\u10d4\u10e2\u10d0 \u10d7\u10e3 \u10db\u10dd\u10d1\u10d8\u10da\u10dd\u10d1\u10d0 \u10d2\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10d7?",
            ["\u10e8\u10d4\u10e9\u10d4\u10e0\u10d4\u10d1\u10d0", "\u10d0\u10e6\u10d3\u10d2\u10d4\u10dc\u10d0", "\u10e8\u10d4\u10ec\u10e7\u10d5\u10d4\u10e2\u10d0", "\u10db\u10dd\u10d1\u10d8\u10da\u10dd\u10d1\u10d0"],
        )
    if normalized == "\u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d4\u10d1\u10d8 \u10db\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10e1":
        return (
            "programs",
            "\u10e0\u10dd\u10db\u10d4\u10da \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d0\u10d6\u10d4 \u10d2\u10e1\u10e3\u10e0\u10d7 \u10d8\u10dc\u10e4\u10dd\u10e0\u10db\u10d0\u10ea\u10d8\u10d0?",
            ["\u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0\u10d8\u10d0\u10e2\u10d8", "\u10db\u10d0\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10e2\u10e3\u10e0\u10d0", "\u10db\u10d4\u10d3\u10d8\u10ea\u10d8\u10dc\u10d0 / MD", "\u10e1\u10d0\u10d4\u10e0\u10d7\u10d0\u10e8\u10dd\u10e0\u10d8\u10e1\u10dd \u10db\u10d8\u10e6\u10d4\u10d1\u10d0"],
        )
    if normalized == "\u10d9\u10e0\u10d4\u10d3\u10d8\u10e2\u10d4\u10d1\u10d8 \u10db\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10e1":
        return (
            "programs",
            "\u10d6\u10e3\u10e1\u10e2\u10d0\u10d3 \u10e0\u10dd\u10db \u10d2\u10d8\u10de\u10d0\u10e1\u10e3\u10ee\u10dd\u10d7, \u10d2\u10d7\u10ee\u10dd\u10d5\u10d7 \u10d3\u10d0\u10d0\u10d6\u10e3\u10e1\u10e2\u10dd\u10d7: \u10e0\u10dd\u10db\u10d4\u10da\u10d8 \u10e1\u10d0\u10e4\u10d4\u10ee\u10e3\u10e0\u10d8\u10e1 \u10d0\u10dc \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d8\u10e1 \u10d9\u10e0\u10d4\u10d3\u10d8\u10e2\u10d4\u10d1\u10d8 \u10d2\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10d7?",
            ["\u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0\u10d8\u10d0\u10e2\u10d8", "\u10db\u10d0\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10e2\u10e3\u10e0\u10d0", "\u10d4\u10e0\u10d7\u10e1\u10d0\u10e4\u10d4\u10ee\u10e3\u10e0\u10d8\u10d0\u10dc\u10d8", "\u10d9\u10dd\u10dc\u10d9\u10e0\u10d4\u10e2\u10e3\u10da\u10d8 \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d0"],
        )
    if normalized in {
        "\u10d9\u10d0\u10e2\u10d0\u10da\u10dd\u10d2\u10e8\u10d8 \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d0\u10d6\u10d4 \u10d8\u10dc\u10e4\u10dd\u10e0\u10db\u10d0\u10ea\u10d8\u10d0 \u10db\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10e1",
        "\u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d8\u10e1 \u10e8\u10d4\u10e1\u10d0\u10ee\u10d4\u10d1 \u10d8\u10dc\u10e4\u10dd\u10e0\u10db\u10d0\u10ea\u10d8\u10d0 \u10db\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10e1",
    }:
        return (
            "programs",
            "\u10d2\u10d7\u10ee\u10dd\u10d5\u10d7 \u10d3\u10d0\u10d0\u10d6\u10e3\u10e1\u10e2\u10dd\u10d7, \u10e0\u10dd\u10db\u10d4\u10da\u10d8 \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d0 \u10d2\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10d7 \u10d0\u10dc \u10e0\u10dd\u10db\u10d4\u10da\u10d8 \u10d3\u10d4\u10e2\u10d0\u10da\u10d8 \u10d2\u10ed\u10d8\u10e0\u10d3\u10d4\u10d1\u10d0\u10d7: \u10d9\u10e0\u10d4\u10d3\u10d8\u10e2\u10d4\u10d1\u10d8, \u10d4\u10dc\u10d0, \u10d9\u10d5\u10d0\u10da\u10d8\u10e4\u10d8\u10d9\u10d0\u10ea\u10d8\u10d0 \u10d7\u10e3 \u10e1\u10d0\u10e1\u10ec\u10d0\u10d5\u10da\u10dd \u10d2\u10d4\u10d2\u10db\u10d0?",
            ["\u10d9\u10e0\u10d4\u10d3\u10d8\u10e2\u10d4\u10d1\u10d8", "\u10e1\u10ec\u10d0\u10d5\u10da\u10d4\u10d1\u10d8\u10e1 \u10d4\u10dc\u10d0", "\u10d9\u10d5\u10d0\u10da\u10d8\u10e4\u10d8\u10d9\u10d0\u10ea\u10d8\u10d0", "\u10e1\u10d0\u10e1\u10ec\u10d0\u10d5\u10da\u10dd \u10d2\u10d4\u10d2\u10db\u10d0"],
        )
    return BROAD_QUESTIONS.get(normalized) or BROAD_QUESTIONS.get(lowered)


def admissions_deadline_clarification(lowered: str, language: str):
    if not is_admissions_deadline_question(lowered):
        return None
    if is_academic_registration_deadline_question(lowered):
        return None
    if language == "en":
        return (
            "admissions",
            "Please clarify which admission deadline you mean.",
            [
                "Bachelor admission",
                "Master admission",
                "International student admission",
                "Specific program",
                "Academic/administrative registration",
            ],
        )
    return (
        "admissions",
        "გთხოვთ დამიზუსტოთ, რომელი ჩარიცხვის ბოლო ვადა გაინტერესებთ?",
        [
            "ბაკალავრიატის მიღება",
            "მაგისტრატურის მიღება",
            "საერთაშორისო სტუდენტების მიღება",
            "კონკრეტული პროგრამა",
            "აკადემიური/ადმინისტრაციული რეგისტრაცია",
        ],
    )


def medical_tuition_clarification(lowered: str, language: str):
    if not (has_tuition_marker(lowered) and has_medical_program_marker(lowered)):
        return None
    if language == "en":
        return (
            "finance",
            "Please clarify which Medicine program fee information you need. Exact/current tuition should be confirmed with Alte's admissions or finance office.",
            [
                "Medicine program tuition",
                "Payment terms",
                "Funding/grants",
                "International student fee",
            ],
        )
    return (
        "finance",
        "გთხოვთ დამიზუსტოთ, რომელი ინფორმაცია გჭირდებათ სამედიცინო პროგრამის საფასურზე? ზუსტი/current საფასური უნდა გადაამოწმოთ ალტეს მიღების ან საფინანსო სამსახურთან.",
        [
            "მედიცინის პროგრამის საფასური",
            "გადახდის პირობები",
            "დაფინანსება/გრანტები",
            "საერთაშორისო სტუდენტების საფასური",
        ],
    )


def is_admissions_deadline_question(lowered: str) -> bool:
    deadline_markers = [
        "ბოლო ვადა",
        "დედლაინი",
        "application deadline",
        "admission deadline",
        "როდის მთავრდება მიღება",
        "ჩარიცხვა როდის მთავრდება",
    ]
    has_deadline = any(marker in lowered for marker in deadline_markers) or (
        "deadline" in lowered and any(marker in lowered for marker in ["admission", "application", "apply"])
    )
    has_admissions = any(
        marker in lowered
        for marker in ["მიღებ", "ჩარიცხ", "ჩაბარ", "admission", "application", "apply", "enroll"]
    )
    return has_deadline and has_admissions


def is_academic_registration_deadline_question(lowered: str) -> bool:
    has_registration = any(marker in lowered for marker in ["რეგისტრ", "registration"])
    has_academic = any(marker in lowered for marker in ["აკადემიურ", "ადმინისტრაციულ", "academic", "administrative"])
    has_deadline = any(marker in lowered for marker in ["ბოლო ვადა", "დედლაინი", "deadline"])
    return has_registration and has_academic and has_deadline


def has_tuition_marker(lowered: str) -> bool:
    return any(
        marker in lowered
        for marker in [
            "რა ღირს",
            "ფასი",
            "საფასურ",
            "tuition",
            "fee",
            "cost",
            "how much",
            "payment",
            "გადახდ",
        ]
    )


def has_medical_program_marker(lowered: str) -> bool:
    return any(marker in lowered for marker in ["medicine", "medical", " md", "md program", "მედიცინ", "სამედიცინო"])


def normalize_broad_question_text(lowered: str) -> str:
    text = " ".join((lowered or "").strip().lower().split())
    return text.strip(" ?!.,;:؟؛")


def specialize_source_groups_for_message(lowered: str, source_groups: list[str]) -> list[str]:
    specialized = forced_source_group(lowered)
    if specialized:
        return [specialized]
    if is_credit_volume_question(lowered) or is_teaching_language_question(lowered):
        return ["official_academic_rules"] if "official_academic_rules" in source_groups else source_groups
    if "official_academic_rules" not in source_groups:
        return source_groups
    if any(
        marker in lowered
        for marker in [
            "student status",
            "status suspension",
            "status restoration",
            "status termination",
            "mobility",
            "credit recognition",
            "სტატუს",
            "მობილ",
            "კრედიტების აღიარ",
            "კრედიტის აღიარ",
        ]
    ):
        return ["student_status_and_mobility"]
    if is_exam_calendar_date_question(lowered):
        return ["academic_calendar_2025_2026"]
    if any(
        marker in lowered
        for marker in [
            "gpa",
            "fx",
            "retake",
            "make-up",
            "final exam admission",
            "დასკვნით",
            "გამოცდ",
            "დაშვებ",
            "გადაბარ",
            "დამატებით",
            "დამატებითი",
            "შუალედურ",
            "შეფასებ",
            "ქულა",
        ]
    ):
        return ["exams_and_assessment"]
    if any(marker in lowered for marker in ["foreign applicant", "foreign education", "international student", "english-language program", "english program requirements"]):
        return ["international_admissions_sources"]
    return source_groups


def is_exam_calendar_date_question(lowered: str) -> bool:
    exam_markers = ["exam", "retake", "midterm", "final", "გამოცდ", "გადაბარ", "შუალედურ", "დასკვნით"]
    date_markers = ["when", "date", "schedule", "calendar", "როდის", "თარიღ", "კალენდ", "პერიოდ", "გრაფიკ"]
    rule_markers = ["rule", "admission", "allowed", "mean", "means", "წესი", "დაშვებ", "ნიშნავს", "შეფასებ", "ქულა"]
    return (
        any(marker in lowered for marker in exam_markers)
        and any(marker in lowered for marker in date_markers)
        and not any(marker in lowered for marker in rule_markers)
    )


def department_for_specialized_route(lowered: str, source_groups: list[str], current_department: str) -> str:
    primary = source_groups[0] if source_groups else None
    if primary == "international_admissions_sources" and ("medicine" in lowered or " md" in lowered or "md " in lowered):
        return "medicine_md"
    if primary:
        return department_for_source_group(primary)
    return current_department


def has_unsupported_marker(lowered: str) -> bool:
    if has_unsupported_calendar_year(lowered):
        return True
    current_tuition_question = any(marker in lowered for marker in ["წელს", "დღეს", "მიმდინარე"]) and any(
        marker in lowered for marker in ["ღირს", "ფასი", "საფასურ"]
    )
    if current_tuition_question:
        return True
    return any(
        marker in lowered
        for marker in [
            "2031",
            "space campus",
            "cosmic campus",
            "კოსმოსური კამპუს",
            "rare manuscript",
            "current exact tuition",
            "consultant phone",
            "consultant phone number",
            "კონსულტანტის ტელეფონ",
            "reset it now",
        ]
    )


def known_broad_calendar_question(normalized: str, language: str):
    ka_questions = {
        "\u10d2\u10d0\u10db\u10dd\u10ea\u10d3\u10d4\u10d1\u10d8 \u10e0\u10dd\u10d3\u10d8\u10e1 \u10d0\u10e0\u10d8\u10e1",
        "\u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d0 \u10e0\u10dd\u10d3\u10d8\u10e1 \u10d0\u10e0\u10d8\u10e1",
        "\u10e1\u10d4\u10db\u10d4\u10e1\u10e2\u10e0\u10d8 \u10e0\u10dd\u10d3\u10d8\u10e1 \u10d8\u10ec\u10e7\u10d4\u10d1\u10d0",
        "როდის არის რეგისტრაციის პერიოდი აკადემიურ კალენდარში",
        "როდის იწყება სემესტრი",
        "როდის არის შუალედური ან დასკვნითი გამოცდები",
    }
    en_questions = {"when are exams", "when is registration", "when does the semester start"}
    if normalized in ka_questions:
        return (
            "academic_calendar",
            "\u10d2\u10d7\u10ee\u10dd\u10d5\u10d7 \u10d3\u10d0\u10d0\u10d6\u10e3\u10e1\u10e2\u10dd\u10d7: \u10e0\u10dd\u10db\u10d4\u10da\u10d8 \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d8\u10e1 \u10ef\u10d2\u10e3\u10e4\u10d8, \u10e0\u10dd\u10db\u10d4\u10da\u10d8 \u10e1\u10d4\u10db\u10d4\u10e1\u10e2\u10e0\u10d8 \u10d3\u10d0 \u10e0\u10dd\u10db\u10d4\u10da\u10d8 \u10db\u10dd\u10d5\u10da\u10d4\u10dc\u10d0 \u10d2\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10d7?",
            [
                "\u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0\u10d8\u10d0\u10e2\u10d8 \u10d9\u10dd\u10db\u10de\u10d8\u10e3\u10e2\u10d4\u10e0\u10e3\u10da\u10d8 \u10db\u10d4\u10ea\u10dc\u10d8\u10d4\u10e0\u10d4\u10d1\u10d8\u10e1 \u10d2\u10d0\u10e0\u10d3\u10d0",
                "Computer Science",
                "\u10db\u10d0\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10e2\u10e3\u10e0\u10d0",
                "\u10d4\u10e0\u10d7\u10e1\u10d0\u10e4\u10d4\u10ee\u10e3\u10e0\u10d8\u10d0\u10dc\u10d8",
            ],
        )
    if normalized in en_questions:
        return (
            "academic_calendar",
            "Please clarify which program group, semester, and event you mean.",
            ["Bachelor except Computer Science", "Computer Science", "Master programs", "One-cycle / first-year one-cycle English"],
        )
    return None


def has_unsupported_calendar_year(lowered: str) -> bool:
    years = {int(match) for match in re.findall(r"\b(20\d{2})\b", lowered)}
    if not years or years <= {2025, 2026}:
        return False
    return is_academic_calendar_priority_question(lowered)


def has_english_word_marker(lowered: str, markers: list[str]) -> bool:
    for marker in markers:
        pattern = re.escape(marker).replace(r"\ ", r"\s+")
        if re.search(rf"(?<![a-z0-9]){pattern}(?![a-z0-9])", lowered):
            return True
    return False


def is_academic_calendar_priority_question(lowered: str) -> bool:
    if is_exam_rule_like_question(lowered):
        return False
    english_explicit_calendar_context = [
        "academic calendar",
        "calendar",
        "schedule",
    ]
    georgian_explicit_calendar_context = [
        "\u10d0\u10d9\u10d0\u10d3\u10d4\u10db\u10d8\u10e3\u10e0\u10d8 \u10d9\u10d0\u10da\u10d4\u10dc\u10d3\u10d0\u10e0\u10d8",
        "\u10d0\u10d9\u10d0\u10d3\u10d4\u10db\u10d8\u10e3\u10e0\u10d8 \u10d9\u10d0\u10da\u10d4\u10dc\u10d3",
        "\u10d9\u10d0\u10da\u10d4\u10dc\u10d3\u10d0\u10e0\u10d8",
        "\u10d9\u10d0\u10da\u10d4\u10dc\u10d3",
        "\u10d2\u10d0\u10dc\u10e0\u10d8\u10d2\u10d8",
    ]
    english_date_time_markers = [
        "when",
        "date",
        "dates",
        "start",
        "starts",
        "begin",
        "begins",
        "start date",
        "semester start",
        "exam date",
        "final date",
        "midterm date",
        "holiday dates",
        "final exams",
        "midterm exams",
        "holidays",
        "vacation",
    ]
    georgian_date_time_markers = [
        "\u10e0\u10dd\u10d3\u10d8\u10e1",
        "\u10e0\u10dd\u10d3\u10d8\u10d3\u10d0\u10dc",
        "\u10e0\u10dd\u10d3\u10d4\u10db\u10d3\u10d4",
        "\u10d7\u10d0\u10e0\u10d8\u10e6",
        "\u10d7\u10d0\u10e0\u10d8\u10e6\u10d4\u10d1\u10d8",
        "\u10d9\u10d0\u10da\u10d4\u10dc\u10d3",
        "\u10d2\u10d0\u10dc\u10e0\u10d8\u10d2",
        "\u10d8\u10ec\u10e7\u10d4\u10d1\u10d0",
        "\u10d3\u10d0\u10ec\u10e7\u10d4\u10d1\u10d0",
        "\u10d3\u10d0\u10e1\u10e0\u10e3\u10da\u10d4\u10d1\u10d0",
        "\u10e0\u10d8\u10ea\u10ee\u10d5\u10e8\u10d8",
        "\u10e0\u10dd\u10db\u10d4\u10da \u10d3\u10e6\u10d4\u10e1",
    ]
    english_calendar_topics = [
        "semester",
        "registration",
        "exam",
        "midterm",
        "final",
        "retake",
        "holiday",
        "vacation",
        "bachelor",
        "master",
        "one-cycle",
        "one cycle",
        "computer science",
    ]
    georgian_calendar_topics = [
        "\u10e1\u10d4\u10db\u10d4\u10e1\u10e2\u10e0",
        "\u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0",
        "\u10d2\u10d0\u10db\u10dd\u10ea\u10d3",
        "\u10e8\u10e3\u10d0\u10da\u10d4\u10d3",
        "\u10d3\u10d0\u10e1\u10d9\u10d5\u10dc\u10d8\u10d7",
        "\u10d2\u10d0\u10d3\u10d0\u10d1\u10d0\u10e0",
        "\u10d0\u10e0\u10d3\u10d0\u10d3\u10d4\u10d2",
        "\u10e3\u10e5\u10db\u10d4",
        "\u10e1\u10d0\u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0",
        "\u10e1\u10d0\u10db\u10d0\u10d2\u10d8\u10e1\u10e2\u10e0",
        "\u10d4\u10e0\u10d7\u10e1\u10d0\u10e4\u10d4\u10ee\u10e3\u10e0",
    ]
    english_exclusion_terms = [
        "requirement",
        "requirements",
        "admission",
        "admissions",
        "eligibility",
        "documents",
        "document",
        "needed documents",
        "procedure",
        "rule",
        "rules",
        "policy",
        "how to register",
        "application requirements",
    ]
    georgian_exclusion_terms = [
        "\u10db\u10dd\u10d7\u10ee\u10dd\u10d5\u10dc\u10d0",
        "\u10db\u10dd\u10d7\u10ee\u10dd\u10d5\u10dc\u10d4\u10d1\u10d8",
        "\u10db\u10d8\u10e6\u10d4\u10d1\u10d0",
        "\u10e9\u10d0\u10e0\u10d8\u10ea\u10ee\u10d5\u10d0",
        "\u10e1\u10d0\u10d1\u10e3\u10d7\u10d4\u10d1\u10d8",
        "\u10d3\u10dd\u10d9\u10e3\u10db\u10d4\u10dc\u10e2\u10d4\u10d1\u10d8",
        "\u10e1\u10d0\u10ed\u10d8\u10e0\u10dd \u10d3\u10dd\u10d9\u10e3\u10db\u10d4\u10dc\u10e2\u10d4\u10d1\u10d8",
        "\u10de\u10e0\u10dd\u10ea\u10d4\u10d3\u10e3\u10e0\u10d0",
        "\u10ec\u10d4\u10e1\u10d8",
        "\u10ec\u10d4\u10e1\u10d4\u10d1\u10d8",
        "\u10de\u10dd\u10da\u10d8\u10e2\u10d8\u10d9\u10d0",
        "\u10e0\u10dd\u10d2\u10dd\u10e0 \u10d3\u10d0\u10d5\u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d8\u10e0\u10d3\u10d4",
        "\u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d8\u10e1 \u10db\u10dd\u10d7\u10ee\u10dd\u10d5\u10dc\u10d4\u10d1\u10d8",
    ]
    has_explicit_context = has_english_word_marker(lowered, english_explicit_calendar_context) or any(marker in lowered for marker in georgian_explicit_calendar_context)
    has_date_time = has_english_word_marker(lowered, english_date_time_markers) or any(marker in lowered for marker in georgian_date_time_markers)
    has_calendar_topic = has_english_word_marker(lowered, english_calendar_topics) or any(marker in lowered for marker in georgian_calendar_topics)
    has_exclusion = has_english_word_marker(lowered, english_exclusion_terms) or any(marker in lowered for marker in georgian_exclusion_terms)
    if has_exclusion and not has_explicit_context and not has_date_time:
        return False
    return (has_explicit_context or has_date_time) and has_calendar_topic


def is_registration_policy_question(lowered: str) -> bool:
    has_registration = has_english_word_marker(lowered, ["registration", "register"]) or any(
        marker in lowered for marker in ["რეგისტრ", "დარეგისტრ"]
    )
    has_policy = has_english_word_marker(
        lowered,
        [
            "requirement",
            "requirements",
            "admission",
            "admissions",
            "eligibility",
            "documents",
            "document",
            "needed documents",
            "procedure",
            "rule",
            "rules",
            "policy",
            "how to register",
            "application requirements",
        ],
    ) or any(
        marker in lowered
        for marker in [
            "მოთხოვ",
            "მიღება",
            "ჩარიცხ",
            "საბუთ",
            "დოკუმენტ",
            "პროცედურ",
            "წეს",
            "პოლიტიკ",
            "როგორ დავრეგისტრირდე",
        ]
    )
    return has_registration and has_policy and not is_academic_calendar_priority_question(lowered)


def is_exam_rule_like_question(lowered: str) -> bool:
    has_exam = any(marker in lowered for marker in ["exam", "retake", "make-up", "assessment", "\u10d2\u10d0\u10db\u10dd\u10ea\u10d3", "\u10d2\u10d0\u10d3\u10d0\u10d1\u10d0\u10e0", "\u10d3\u10d0\u10e1\u10d9\u10d5\u10dc\u10d8\u10d7"])
    has_rule = any(marker in lowered for marker in ["rule", "admission", "allowed", "mean", "means", "\u10ec\u10d4\u10e1", "\u10d3\u10d0\u10e8\u10d5", "\u10e0\u10dd\u10d2\u10dd\u10e0"])
    if any(marker in lowered for marker in ["fx", "gpa"]) and has_rule:
        return True
    asks_when = any(marker in lowered for marker in ["when", "date", "calendar", "\u10e0\u10dd\u10d3\u10d8\u10e1"])
    return has_exam and has_rule and not asks_when


def forced_source_group(lowered: str) -> str | None:
    lowered = " ".join((lowered or "").lower().split())
    if is_academic_registration_deadline_question(lowered):
        return "academic_calendar_2025_2026"
    if is_academic_calendar_priority_question(lowered):
        return "academic_calendar_2025_2026"
    if has_tuition_marker(lowered) and not is_program_catalog_explicit_scope(lowered):
        return "finance_sources"
    if is_registration_policy_question(lowered):
        return "admissions_rules"
    if is_program_catalog_question(lowered):
        return "program_catalog_sources"
    if is_admission_without_exams_question(lowered):
        return "admissions_rules"
    if is_english_program_requirements_question(lowered):
        return "international_admissions_sources"
    if any(marker in lowered for marker in ["fx", "retake", "make-up exam", "gpa", "grading rule"]) and any(
        marker in lowered for marker in ["exam", "assessment", "grade", "student"]
    ):
        return "exams_and_assessment"
    if any(marker in lowered for marker in ["bachelor admission", "master admission", "admission document", "enrollment"]):
        return "admissions_rules"
    if is_credit_volume_question(lowered) or is_teaching_language_question(lowered):
        return "official_academic_rules"
    if any(marker in lowered for marker in ["student status", "status suspension", "status restoration", "status termination", "mobility", "credit recognition"]):
        return "student_status_and_mobility"
    if any(marker in lowered for marker in ["library", "ბიბლიოთეკ", "databases", "database", "books", "book", "electronic resources"]):
        return "library_sources"
    if any(marker in lowered for marker in ["emis", "student portal", "login", "password", "technical access", "it დახმარ"]):
        return "it_support_sources"
    if any(marker in lowered for marker in ["international student", "foreign applicant", "foreign education", "iro"]):
        return "international_admissions_sources"
    if any(marker in lowered for marker in ["finance", "financial", "tuition", "payment", "scholarship", "grant", "dean's list", "გრანტ", "დაფინანს", "სოციალური პროგრამ"]):
        return "finance_sources"
    if any(marker in lowered for marker in ["ომბუდსმენ", "უფლებ", "სპეციალური საჭირო", "სსმ", "პლაგიატ", "კეთილსინდისიერ", "სანქცი", "edi", "მდგრად"]):
        return "official_academic_rules"
    if any(marker in lowered for marker in ["career", "internship", "employment", "job"]):
        return "career_sources"
    return None


def is_program_catalog_question(lowered: str) -> bool:
    if has_tuition_marker(lowered) and not is_program_catalog_explicit_scope(lowered):
        return False
    if (is_credit_volume_question(lowered) or is_teaching_language_question(lowered)) and not is_program_catalog_explicit_scope(lowered):
        return False
    if is_academic_calendar_priority_question(lowered):
        return False
    if is_calendar_date_or_schedule_question(lowered):
        return False
    if any(
        marker in lowered
        for marker in [
            "ბიბლიოთეკ",
            "library",
            "book",
            "books",
            "database",
            "databases",
            "electronic resource",
            "მიღებ",
            "საბუთ",
            "ჩარიცხვ",
            "admission",
            "enrollment",
            "document",
            "გრანტ",
            "დაფინანს",
            "finance",
            "financial",
            "scholarship",
            "grant",
            "it დახმარ",
            "emis",
            "portal",
            "technical support",
        ]
    ):
        return False
    catalog_markers = [
        "program catalog",
        "higher education program catalog",
        "პროგრამების კატალოგ",
    ]
    if any(marker in lowered for marker in catalog_markers):
        return True
    if "კატალოგ" in lowered and any(marker in lowered for marker in ["პროგრამ", "საგანმანათლებლო"]):
        return True
    list_or_count_markers = [
        "how many programs",
        "number of programs",
        "programs in total",
        "total programs",
        "bachelor programs",
        "master programs",
        "one-cycle programs",
        "list bachelor",
        "list master",
        "program list",
        "რამდენი საგანმანათლებლო პროგრამა",
        "რამდენი პროგრამა",
        "პროგრამები სულ",
        "საბაკალავრო პროგრამები",
        "სამაგისტრო პროგრამები",
        "ერთსაფეხურიანი პროგრამები",
    ]
    if any(marker in lowered for marker in list_or_count_markers):
        return True
    if "ჩამომითვალე" in lowered and any(
        marker in lowered
        for marker in [
            "პროგრამ",
            "საგანმანათლებლო",
            "საბაკალავრო",
            "სამაგისტრო",
            "ერთსაფეხურ",
            "კვალიფიკაცია",
            "სამართლის",
            "კომპიუტერული მეცნიერების",
        ]
    ):
        return True
    qualification_markers = [
        "program qualification",
        "qualification does",
        "law bachelor qualification",
        "law master qualification",
        "რა კვალიფიკაციას",
        "სამართლის საბაკალავრო",
        "სამართლის სამაგისტრო",
        "პროგრამის კვალიფიკაცია",
    ]
    if any(marker in lowered for marker in qualification_markers):
        return True
    language_markers = [
        "computer science geo eng",
        "computer science language",
        "computer science languages",
        "languages is computer science",
        "კომპიუტერული მეცნიერების პროგრამა",
    ]
    if "computer science" in lowered and any(marker in lowered for marker in ["language", "languages"]) and any(marker in lowered for marker in ["catalog", "program"]):
        return True
    if any(marker in lowered for marker in language_markers) and any(
        marker in lowered for marker in ["language", "languages", "ენა", "ენებზე", "geo", "eng"]
    ):
        return True
    distribution_markers = [
        "distributed by level",
        "distribution by level",
        "levels distribution",
        "საფეხურების მიხედვით",
        "როგორ ნაწილდება",
    ]
    return any(marker in lowered for marker in distribution_markers)


def is_program_catalog_explicit_scope(lowered: str) -> bool:
    if "catalog" in lowered and any(marker in lowered for marker in ["program", "computer science", "bachelor", "master", "one-cycle", "one cycle"]):
        return True
    return any(
        marker in lowered
        for marker in [
            "program catalog",
            "higher education program catalog",
            "პროგრამების კატალოგ",
            "კატალოგის მიხედვით",
            "კატალოგში",
        ]
    )


def is_credit_volume_question(lowered: str) -> bool:
    has_credit = any(marker in lowered for marker in ["ects", "how many credits", "credit", "credits", "კრედიტ"])
    has_level = any(
        marker in lowered
        for marker in [
            "bachelor",
            "master",
            "medicine",
            "dentistry",
            "one-cycle",
            "one cycle",
            "საბაკალავრო",
            "ბაკალავრიატ",
            "სამაგისტრო",
            "მაგისტრატურ",
            "მედიცინ",
            "სტომატოლოგ",
            "ერთსაფეხურ",
        ]
    )
    return has_credit and has_level


def is_calendar_date_or_schedule_question(lowered: str) -> bool:
    has_time = any(marker in lowered for marker in ["when", "date", "schedule", "calendar", "როდის", "თარიღ", "განრიგ", "კალენდ"])
    has_calendar_topic = any(marker in lowered for marker in ["exam", "final", "midterm", "retake", "გამოცდ", "დასკვნით", "შუალედ", "გადაბარ"])
    return has_time and has_calendar_topic


def is_teaching_language_question(lowered: str) -> bool:
    return any(
        marker in lowered
        for marker in [
            "teaching language",
            "language of instruction",
            "სწავლების ენა",
            "რა ენაზე",
        ]
    )


def is_admission_without_exams_question(lowered: str) -> bool:
    without_markers = [
        "without national exams",
        "without exams",
        "admission without exams",
        "apply without exams",
        "exam-free admission",
        "გამოცდების გარეშე",
        "ეროვნული გამოცდების გარეშე",
    ]
    admission_markers = [
        "admission",
        "apply",
        "enroll",
        "enrollment",
        "ჩაბარ",
        "მიღებ",
        "ჩარიცხ",
        "ჩავირიცხ",
    ]
    return any(marker in lowered for marker in without_markers) and any(marker in lowered for marker in admission_markers)


def is_english_program_requirements_question(lowered: str) -> bool:
    english_program_markers = [
        "english-language program",
        "english language program",
        "english-taught program",
        "english taught program",
        "english program",
    ]
    requirement_markers = [
        "requirement",
        "requirements",
        "required",
        "proof",
        "proficiency",
        "ielts",
        "toefl",
        "admission",
        "applicant",
        "international",
        "foreign",
    ]
    if any(marker in lowered for marker in english_program_markers) and any(marker in lowered for marker in requirement_markers):
        return True
    english_proficiency = any(marker in lowered for marker in ["english proficiency", "ielts", "toefl"])
    international_context = any(marker in lowered for marker in ["international applicant", "international applicants", "foreign applicant", "foreign applicants", "english-taught", "english taught"])
    return english_proficiency and international_context


def department_for_source_group(source_group: str) -> str:
    return {
        "official_academic_rules": "programs",
        "program_catalog_sources": "programs",
        "academic_calendar_2025_2026": "academic_calendar",
        "admissions_rules": "admissions",
        "student_status_and_mobility": "study_process",
        "exams_and_assessment": "study_process",
        "finance_sources": "finance",
        "library_sources": "library",
        "it_support_sources": "it_support",
        "international_admissions_sources": "international_admissions",
        "career_sources": "career",
    }.get(source_group, "admissions")


def department_for_unsupported(lowered: str) -> str:
    if has_unsupported_calendar_year(lowered):
        return "academic_calendar"
    if any(marker in lowered for marker in ["program", "პროგრამ"]) and any(marker in lowered for marker in ["consultant", "კონსულტანტ", "ტელეფონ"]):
        return "programs"
    if any(marker in lowered for marker in ["scholarship", "tuition", "price", "fee", "grant"]):
        return "finance"
    if "library" in lowered or "manuscript" in lowered:
        return "library"
    if any(marker in lowered for marker in ["emis", "portal", "password", "login"]):
        return "it_support"
    return "admissions"


def department_for_operator_request(lowered: str) -> str:
    if any(marker in lowered for marker in ["finance", "financial", "payment", "tuition", "\u10e4\u10d8\u10dc\u10d0\u10dc\u10e1", "\u10d2\u10d0\u10d3\u10d0\u10ee\u10d3"]):
        return "finance"
    if any(marker in lowered for marker in ["admission", "apply", "enroll", "\u10db\u10d8\u10e6\u10d4\u10d1", "\u10e9\u10d0\u10d1\u10d0\u10e0", "\u10e9\u10d0\u10e0\u10d8\u10ea\u10ee"]):
        return "admissions"
    if any(marker in lowered for marker in ["library", "\u10d1\u10d8\u10d1\u10da\u10d8\u10dd\u10d7\u10d4\u10d9"]):
        return "library"
    if any(marker in lowered for marker in ["it", "emis", "login", "portal", "password", "\u10de\u10d0\u10e0\u10dd\u10da", "\u10e8\u10d4\u10d5\u10d3\u10d8\u10d5\u10d0\u10e0"]):
        return "it_support"
    if any(marker in lowered for marker in ["medicine", " md", "md ", "\u10db\u10d4\u10d3\u10d8\u10ea\u10d8\u10dc"]):
        return "medicine_md"
    return "human_operator"

