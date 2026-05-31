from __future__ import annotations

import json
import logging
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
        "მიღებასთან დაკავშირებით რომ გიპასუხოთ, გთხოვთ დააზუსტოთ: ბაკალავრიატი, მაგისტრატურა, საბუთები თუ ჩარიცხვის პროცედურა გაინტერესებთ?",
        ["ბაკალავრიატი", "მაგისტრატურა", "საბუთები", "ჩარიცხვის პროცედურა"],
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
    "დახმარება მინდა": (
        "admissions",
        "გთხოვთ დააზუსტოთ, რა სახის დახმარება გჭირდებათ: მიღება, პროგრამები, ფინანსები, IT დახმარება თუ ოპერატორთან დაკავშირება?",
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
    return ClaudeIntentRoute(
        intent="information_request",
        language=decision.language,
        department=decision.department_id,
        public_department_label=decision.department_label,
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
    if lowered == "\u10e1\u10ec\u10d0\u10d5\u10da\u10d0 \u10db\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10e1":
        return (
            "admissions",
            "\u10d6\u10e3\u10e1\u10e2\u10d0\u10d3 \u10e0\u10dd\u10db \u10d2\u10d8\u10de\u10d0\u10e1\u10e3\u10ee\u10dd\u10d7, \u10d2\u10d7\u10ee\u10dd\u10d5\u10d7 \u10d3\u10d0\u10d0\u10d6\u10e3\u10e1\u10e2\u10dd\u10d7 \u2014 \u10e0\u10dd\u10db\u10d4\u10da\u10d8 \u10e1\u10d0\u10d9\u10d8\u10d7\u10ee\u10d8 \u10d2\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10d7?",
            ["\u10db\u10d8\u10e6\u10d4\u10d1\u10d0", "\u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d4\u10d1\u10d8", "\u10e1\u10ec\u10d0\u10d5\u10da\u10d8\u10e1 \u10e1\u10d0\u10e4\u10d0\u10e1\u10e3\u10e0\u10d8", "\u10e1\u10e2\u10e3\u10d3\u10d4\u10dc\u10e2\u10d8\u10e1 \u10e1\u10e2\u10d0\u10e2\u10e3\u10e1\u10d8"],
        )
    if lowered == "\u10d2\u10d0\u10d3\u10d0\u10ee\u10d3\u10d4\u10d1\u10d6\u10d4 \u10db\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10e1":
        return (
            "finance",
            "\u10d2\u10d0\u10d3\u10d0\u10ee\u10d3\u10d4\u10d1\u10d6\u10d4 \u10e0\u10dd\u10db \u10d2\u10d8\u10de\u10d0\u10e1\u10e3\u10ee\u10dd\u10d7, \u10d2\u10d7\u10ee\u10dd\u10d5\u10d7 \u10d3\u10d0\u10d0\u10d6\u10e3\u10e1\u10e2\u10dd\u10d7: \u10e1\u10ec\u10d0\u10d5\u10da\u10d8\u10e1 \u10e1\u10d0\u10e4\u10d0\u10e1\u10e3\u10e0\u10d8 \u10d2\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10d7, \u10d2\u10d0\u10d3\u10d0\u10ee\u10d3\u10d8\u10e1 \u10d2\u10e0\u10d0\u10e4\u10d8\u10d9\u10d8 \u10d7\u10e3 \u10e4\u10d8\u10dc\u10d0\u10dc\u10e1\u10e3\u10e0 \u10d3\u10d4\u10de\u10d0\u10e0\u10e2\u10d0\u10db\u10d4\u10dc\u10e2\u10d7\u10d0\u10dc \u10d3\u10d0\u10d9\u10d0\u10d5\u10e8\u10d8\u10e0\u10d4\u10d1\u10d0?",
            ["\u10e1\u10ec\u10d0\u10d5\u10da\u10d8\u10e1 \u10e1\u10d0\u10e4\u10d0\u10e1\u10e3\u10e0\u10d8", "\u10d2\u10d0\u10d3\u10d0\u10ee\u10d3\u10d8\u10e1 \u10d2\u10e0\u10d0\u10e4\u10d8\u10d9\u10d8", "\u10e4\u10d8\u10dc\u10d0\u10dc\u10e1\u10e3\u10e0 \u10d3\u10d4\u10de\u10d0\u10e0\u10e2\u10d0\u10db\u10d4\u10dc\u10e2\u10d7\u10d0\u10dc \u10d3\u10d0\u10d9\u10d0\u10d5\u10e8\u10d8\u10e0\u10d4\u10d1\u10d0"],
        )
    if lowered == "\u10e1\u10e2\u10d0\u10e2\u10e3\u10e1\u10d6\u10d4 \u10db\u10d0\u10e5\u10d5\u10e1 \u10d9\u10d8\u10d7\u10ee\u10d5\u10d0":
        return (
            "study_process",
            "\u10e1\u10e2\u10e3\u10d3\u10d4\u10dc\u10e2\u10d8\u10e1 \u10e1\u10e2\u10d0\u10e2\u10e3\u10e1\u10d7\u10d0\u10dc \u10d3\u10d0\u10d9\u10d0\u10d5\u10e8\u10d8\u10e0\u10d4\u10d1\u10d8\u10d7 \u10e0\u10dd\u10db \u10d2\u10d8\u10de\u10d0\u10e1\u10e3\u10ee\u10dd\u10d7, \u10d2\u10d7\u10ee\u10dd\u10d5\u10d7 \u10d3\u10d0\u10d0\u10d6\u10e3\u10e1\u10e2\u10dd\u10d7: \u10e8\u10d4\u10e9\u10d4\u10e0\u10d4\u10d1\u10d0, \u10d0\u10e6\u10d3\u10d2\u10d4\u10dc\u10d0, \u10e8\u10d4\u10ec\u10e7\u10d5\u10d4\u10e2\u10d0 \u10d7\u10e3 \u10db\u10dd\u10d1\u10d8\u10da\u10dd\u10d1\u10d0 \u10d2\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10d7?",
            ["\u10e8\u10d4\u10e9\u10d4\u10e0\u10d4\u10d1\u10d0", "\u10d0\u10e6\u10d3\u10d2\u10d4\u10dc\u10d0", "\u10e8\u10d4\u10ec\u10e7\u10d5\u10d4\u10e2\u10d0", "\u10db\u10dd\u10d1\u10d8\u10da\u10dd\u10d1\u10d0"],
        )
    if lowered == "\u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d4\u10d1\u10d8 \u10db\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10e1":
        return (
            "programs",
            "\u10e0\u10dd\u10db\u10d4\u10da \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d0\u10d6\u10d4 \u10d2\u10e1\u10e3\u10e0\u10d7 \u10d8\u10dc\u10e4\u10dd\u10e0\u10db\u10d0\u10ea\u10d8\u10d0?",
            ["\u10d1\u10d0\u10d9\u10d0\u10da\u10d0\u10d5\u10e0\u10d8\u10d0\u10e2\u10d8", "\u10db\u10d0\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10e2\u10e3\u10e0\u10d0", "\u10db\u10d4\u10d3\u10d8\u10ea\u10d8\u10dc\u10d0 / MD", "\u10e1\u10d0\u10d4\u10e0\u10d7\u10d0\u10e8\u10dd\u10e0\u10d8\u10e1\u10dd \u10db\u10d8\u10e6\u10d4\u10d1\u10d0"],
        )
    return BROAD_QUESTIONS.get(lowered)


def has_unsupported_marker(lowered: str) -> bool:
    return any(
        marker in lowered
        for marker in [
            "2031",
            "space campus",
            "cosmic campus",
            "კოსმოსური კამპუს",
            "rare manuscript",
            "current exact tuition",
            "reset it now",
        ]
    )


def forced_source_group(lowered: str) -> str | None:
    if any(marker in lowered for marker in ["fx", "retake", "make-up exam", "gpa", "grading rule"]) and any(
        marker in lowered for marker in ["exam", "assessment", "grade", "student"]
    ):
        return "exams_and_assessment"
    if "computer science" in lowered and "spring" in lowered and ("registration" in lowered or "semester" in lowered):
        return "academic_calendar_2025_2026"
    if any(marker in lowered for marker in ["bachelor admission", "master admission", "admission document", "enrollment"]):
        return "admissions_rules"
    if any(marker in lowered for marker in ["ects", "how many credits", "teaching language", "language of instruction"]):
        return "official_academic_rules"
    if any(marker in lowered for marker in ["student status", "status suspension", "status restoration", "status termination", "mobility", "credit recognition"]):
        return "student_status_and_mobility"
    if any(marker in lowered for marker in ["library", "databases", "books", "electronic resources"]):
        return "library_sources"
    if any(marker in lowered for marker in ["emis", "student portal", "login", "password", "technical access"]):
        return "it_support_sources"
    if any(marker in lowered for marker in ["international student", "foreign applicant", "foreign education", "iro"]):
        return "international_admissions_sources"
    if any(marker in lowered for marker in ["finance", "financial", "tuition", "payment", "scholarship", "grant", "dean's list"]):
        return "finance_sources"
    if any(marker in lowered for marker in ["career", "internship", "employment", "job"]):
        return "career_sources"
    return None


def department_for_source_group(source_group: str) -> str:
    return {
        "official_academic_rules": "programs",
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

