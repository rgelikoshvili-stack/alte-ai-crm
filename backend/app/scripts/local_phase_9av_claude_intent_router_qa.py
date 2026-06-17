from __future__ import annotations

import json
import inspect
from pathlib import Path
from types import SimpleNamespace

from app.services import claude_intent_router_service
from app.services.claude_intent_router_service import (
    allowed_source_group_ids,
    fallback_intent_route,
    load_source_group_descriptions,
    route_decision_from_intent,
    validate_router_payload,
)
from app.services import chat_service
from app.services.knowledge_routing_service import classify_knowledge_route


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
MOJIBAKE_MARKERS = ["\u00e1\u0192", "\u00e2", "\u00c3", "\ufffd"]


def fake_retrieval_item(*, source_key: str, title: str, category: str, source_domain: str | None = None):
    source = SimpleNamespace(
        source_key=source_key,
        title=title,
        category=category,
        source_domain=source_domain,
        source_path=None,
        document_id=None,
    )
    snippet = SimpleNamespace(
        id=f"snippet-{source_key}",
        source_key=source_key,
        title=title,
        category=category,
        source_domain=source_domain,
        keywords="",
        source_path=None,
        document_id=None,
    )
    return SimpleNamespace(source=source, snippet=snippet, score=1.0)


CASES = [
    {
        "id": "clarification_study",
        "message": "სწავლა მაინტერესებს",
        "expect_clarification": True,
        "expected_group": None,
        "operator_needed": False,
    },
    {
        "id": "bachelor_ects",
        "message": "How many ECTS credits are required to complete a bachelor program?",
        "expect_clarification": False,
        "expected_group": "official_academic_rules",
        "operator_needed": False,
    },
    {
        "id": "master_ects",
        "message": "How many credits are required for a master's program at Alte University?",
        "expect_clarification": False,
        "expected_group": "official_academic_rules",
        "operator_needed": False,
    },
    {
        "id": "cs_spring_registration",
        "message": "When does Computer Science spring semester registration start?",
        "expect_clarification": False,
        "expected_group": "academic_calendar_2025_2026",
        "operator_needed": False,
    },
    {
        "id": "admission_documents",
        "message": "Which documents are needed for bachelor admission?",
        "expect_clarification": False,
        "expected_group": "admissions_rules",
        "operator_needed": False,
    },
    {
        "id": "library",
        "message": "How can I use library resources and databases?",
        "expect_clarification": False,
        "expected_group": "library_sources",
        "operator_needed": False,
    },
    {
        "id": "it_emis",
        "message": "I cannot log in to EMIS, who can help?",
        "expect_clarification": False,
        "expected_group": "it_support_sources",
        "operator_needed": False,
    },
    {
        "id": "unsupported_fake",
        "message": "How do I get the 2031 space campus scholarship?",
        "expect_clarification": False,
        "expected_group": None,
        "operator_needed": False,
        "unsupported_likely": True,
    },
    {
        "id": "operator",
        "message": "I want to talk to a human operator",
        "expect_clarification": False,
        "expected_group": None,
        "operator_needed": True,
    },
]


def main() -> int:
    failures: list[dict] = []
    descriptions = load_source_group_descriptions()
    allowed = allowed_source_group_ids()
    if len(descriptions) < 10:
        failures.append({"id": "source_group_descriptions", "reason": "less_than_10_descriptions"})
    missing_allowed = set(descriptions) - allowed
    if missing_allowed:
        failures.append({"id": "source_group_descriptions", "reason": f"not_in_source_groups_json:{sorted(missing_allowed)}"})

    for case in CASES:
        route = fallback_intent_route(case["message"], source_domain="join.alte.edu.ge")
        decision = route_decision_from_intent(
            route,
            classify_knowledge_route(case["message"], source_domain="join.alte.edu.ge"),
        )
        if route.needs_clarification != case["expect_clarification"]:
            failures.append({"id": case["id"], "reason": "clarification_mismatch", "route": route.model_dump()})
        if case.get("expected_group") and decision.primary_source_group != case["expected_group"]:
            failures.append(
                {
                    "id": case["id"],
                    "reason": "source_group_mismatch",
                    "expected": case["expected_group"],
                    "actual": decision.primary_source_group,
                    "route": route.model_dump(),
                }
            )
        if route.operator_needed != case["operator_needed"]:
            failures.append({"id": case["id"], "reason": "operator_needed_mismatch", "route": route.model_dump()})
        if case.get("unsupported_likely") and not route.unsupported_likely:
            failures.append({"id": case["id"], "reason": "unsupported_not_flagged", "route": route.model_dump()})

    validated = validate_router_payload(
        {
            "intent": "information_request",
            "language": "en",
            "department": "Programs",
            "public_department_label": "Programs",
            "topic": "credits",
            "needs_clarification": False,
            "clarification_question": None,
            "clarification_options": [],
            "source_groups_to_search": ["official_academic_rules", "fake_group"],
            "search_terms": ["ECTS"],
            "operator_needed": False,
            "operator_reason": None,
            "unsupported_likely": False,
            "confidence": 0.9,
        },
        message="How many ECTS?",
    )
    if validated.source_groups_to_search != ["official_academic_rules"]:
        failures.append({"id": "validator", "reason": "unknown_group_not_removed"})

    invalid_group_route = validate_router_payload(
        {
            "intent": "information_request",
            "language": "en",
            "department": "Admissions",
            "public_department_label": "Admissions",
            "topic": "documents",
            "needs_clarification": False,
            "clarification_question": None,
            "clarification_options": [],
            "source_groups_to_search": ["fake_group"],
            "search_terms": ["admission documents"],
            "operator_needed": False,
            "operator_reason": None,
            "unsupported_likely": False,
            "confidence": 0.9,
        },
        message="Which admission documents are needed?",
    )
    if invalid_group_route.router_validation_status != "invalid_source_groups":
        failures.append({"id": "invalid_source_groups", "reason": "status_not_set"})
    if invalid_group_route.source_groups_to_search:
        failures.append({"id": "invalid_source_groups", "reason": "invalid_group_not_removed"})
    if not chat_service.should_use_legacy_ai_analysis(invalid_group_route):
        pass
    else:
        failures.append({"id": "invalid_source_groups", "reason": "legacy_ai_should_be_skipped"})

    empty_group_route = validate_router_payload(
        {
            "intent": "information_request",
            "language": "en",
            "department": "Library",
            "public_department_label": "Library",
            "topic": "library",
            "needs_clarification": False,
            "clarification_question": None,
            "clarification_options": [],
            "source_groups_to_search": [],
            "search_terms": ["library resources"],
            "operator_needed": False,
            "operator_reason": None,
            "unsupported_likely": False,
            "confidence": 0.9,
        },
        message="How do I use library resources?",
    )
    if empty_group_route.router_validation_status != "empty_source_groups":
        failures.append({"id": "empty_source_groups", "reason": "status_not_set"})
    if chat_service.should_use_legacy_ai_analysis(empty_group_route):
        failures.append({"id": "empty_source_groups", "reason": "legacy_ai_should_be_skipped"})

    source_backed_route = validate_router_payload(
        {
            "intent": "information_request",
            "language": "en",
            "department": "Programs",
            "public_department_label": "Programs",
            "topic": "ECTS",
            "needs_clarification": False,
            "clarification_question": None,
            "clarification_options": [],
            "source_groups_to_search": ["official_academic_rules"],
            "search_terms": ["ECTS"],
            "operator_needed": False,
            "operator_reason": None,
            "unsupported_likely": False,
            "confidence": 0.95,
        },
        message="How many ECTS?",
    )
    if chat_service.should_use_legacy_ai_analysis(source_backed_route):
        failures.append({"id": "call_count", "reason": "source_backed_route_should_skip_legacy_ai"})

    clarification_route = validate_router_payload(
        {
            "intent": "clarification",
            "language": "en",
            "department": "Admissions",
            "public_department_label": "Admissions",
            "topic": "broad",
            "needs_clarification": True,
            "clarification_question": "Please clarify.",
            "clarification_options": ["Admissions"],
            "source_groups_to_search": ["official_academic_rules"],
            "search_terms": [],
            "operator_needed": False,
            "operator_reason": None,
            "unsupported_likely": False,
            "confidence": 0.95,
        },
        message="I need information",
    )
    if clarification_route.source_groups_to_search:
        failures.append({"id": "clarification", "reason": "clarification_kept_source_groups"})
    if chat_service.should_use_legacy_ai_analysis(clarification_route):
        failures.append({"id": "clarification", "reason": "legacy_ai_should_be_skipped"})

    operator_override = validate_router_payload(
        {
            "intent": "information_request",
            "language": "en",
            "department": "Programs",
            "public_department_label": "Programs",
            "topic": "credits",
            "needs_clarification": False,
            "clarification_question": None,
            "clarification_options": [],
            "source_groups_to_search": ["official_academic_rules"],
            "search_terms": ["ECTS"],
            "operator_needed": False,
            "operator_reason": None,
            "unsupported_likely": False,
            "confidence": 0.9,
        },
        message="I want an operator",
    )
    if not operator_override.operator_needed or operator_override.source_groups_to_search:
        failures.append({"id": "operator_override", "reason": "operator_override_failed"})
    if operator_override.deterministic_override_reason != "explicit_operator_request":
        failures.append({"id": "operator_override", "reason": "override_reason_missing"})

    broad_override = validate_router_payload(
        {
            "intent": "information_request",
            "language": "ka",
            "department": "Programs",
            "public_department_label": "Programs",
            "topic": "credits",
            "needs_clarification": False,
            "clarification_question": None,
            "clarification_options": [],
            "source_groups_to_search": ["official_academic_rules"],
            "search_terms": ["ECTS"],
            "operator_needed": False,
            "operator_reason": None,
            "unsupported_likely": False,
            "confidence": 0.9,
        },
        message="სწავლა მაინტერესებს",
    )
    if not broad_override.needs_clarification or broad_override.source_groups_to_search:
        failures.append({"id": "broad_override", "reason": "broad_override_failed"})

    same_category_noise = fake_retrieval_item(
        source_key="unlisted_admissions_policy",
        title="Unlisted admissions policy",
        category="admissions",
        source_domain=None,
    )
    if chat_service.retrieval_result_belongs_to_source_group(
        same_category_noise,
        "admissions_rules",
        {"source_files": ["bachelor admission chunks"], "source_domain": None},
    ):
        failures.append({"id": "strict_membership", "reason": "same_category_noise_accepted"})
    if chat_service.retrieval_result_belongs_to_source_group(
        same_category_noise,
        "admissions_rules",
        {"source_files": ["bachelor admission chunks"], "allow_category_fallback": True, "allowed_categories": ["finance"]},
    ):
        failures.append({"id": "strict_membership", "reason": "wrong_allowed_category_accepted"})
    if not chat_service.retrieval_result_belongs_to_source_group(
        same_category_noise,
        "admissions_rules",
        {"source_files": ["bachelor admission chunks"], "allow_category_fallback": True, "allowed_categories": ["admissions"]},
    ):
        failures.append({"id": "strict_membership", "reason": "explicit_category_fallback_rejected"})

    finance_operator = fallback_intent_route("I want finance operator")
    if not finance_operator.operator_needed or finance_operator.source_groups_to_search or finance_operator.department != "finance":
        failures.append({"id": "fallback_operator_priority", "reason": "finance_operator_routed_to_source"})

    contact_finance = fallback_intent_route("I want to contact finance department")
    if not contact_finance.operator_needed or contact_finance.source_groups_to_search or contact_finance.department != "finance":
        failures.append({"id": "fallback_operator_priority", "reason": "contact_finance_routed_to_source"})

    generic_operator = fallback_intent_route("ცოცხალი ოპერატორი მინდა")
    if not generic_operator.operator_needed or generic_operator.source_groups_to_search or generic_operator.department != "human_operator":
        failures.append({"id": "fallback_operator_priority", "reason": "generic_operator_not_handover"})

    finance_info = fallback_intent_route("გადახდის გრაფიკი მაინტერესებს")
    if finance_info.operator_needed:
        failures.append({"id": "fallback_operator_priority", "reason": "non_operator_finance_marked_operator"})

    validated_finance_operator = validate_router_payload(
        {
            "intent": "information_request",
            "language": "ka",
            "department": "Programs",
            "public_department_label": "Programs",
            "topic": "finance",
            "needs_clarification": False,
            "clarification_question": None,
            "clarification_options": [],
            "source_groups_to_search": ["finance_sources"],
            "search_terms": ["finance"],
            "operator_needed": False,
            "operator_reason": None,
            "unsupported_likely": False,
            "confidence": 0.9,
        },
        message="მინდა ფინანსურ დეპარტამენტთან დაკავშირება",
    )
    if (
        not validated_finance_operator.operator_needed
        or validated_finance_operator.source_groups_to_search
        or validated_finance_operator.department != "finance"
    ):
        failures.append({"id": "operator_department_inference", "reason": "validated_finance_operator_not_finance"})

    for message in ["მიღება მაინტერესებს", "დახმარება მინდა"]:
        route = fallback_intent_route(message)
        output_text = " ".join([route.clarification_question or "", *route.clarification_options])
        if not route.needs_clarification or any(marker in output_text for marker in MOJIBAKE_MARKERS):
            failures.append({"id": "georgian_clarification_encoding", "reason": f"mojibake_or_no_clarification:{message}"})

    descriptions_text = (PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "source_group_descriptions.json").read_text(encoding="utf-8")
    if any(marker in descriptions_text for marker in MOJIBAKE_MARKERS):
        failures.append({"id": "source_group_descriptions_encoding", "reason": "mojibake_marker_found"})

    router_source = inspect.getsource(claude_intent_router_service)
    if router_source.count("def has_operator_request(") != 1:
        failures.append({"id": "operator_detector_cleanup", "reason": "duplicate_has_operator_request"})

    launch_text = PUBLIC_LAUNCH.read_text(encoding="utf-8", errors="ignore")
    if "NO-GO" not in launch_text:
        failures.append({"id": "public_launch", "reason": "NO-GO not documented"})

    result = {
        "phase": "9AV",
        "total_cases": len(CASES) + 18,
        "passed": len(CASES) + 18 - len(failures),
        "failed": len(failures),
        "failures": failures,
        "production_status": "NOT_DEPLOYED_PENDING_APPROVAL",
        "public_launch": "NO-GO",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())


