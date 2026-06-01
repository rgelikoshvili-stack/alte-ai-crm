from __future__ import annotations

from pathlib import Path

from app.services.department_routing_service import resolve_department
from app.services.claude_intent_router_service import fallback_intent_route, forced_source_group, validate_router_payload


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"


def route_payload(groups: list[str]) -> dict:
    return {
        "intent": "information_request",
        "language": "en",
        "department": "Programs",
        "public_department_label": "Programs",
        "topic": "phase_9ax",
        "needs_clarification": False,
        "clarification_question": None,
        "clarification_options": [],
        "source_groups_to_search": groups,
        "search_terms": ["phase_9ax"],
        "operator_needed": False,
        "operator_reason": None,
        "unsupported_likely": False,
        "confidence": 0.9,
    }


def test_admission_without_exams_ka_routes_to_admissions_not_exams():
    route = validate_router_payload(
        route_payload(["official_academic_rules"]),
        message="ეროვნული გამოცდების გარეშე როგორ ჩავირიცხო?",
    )
    assert route.source_groups_to_search[0] == "admissions_rules"
    assert route.department == "admissions"
    assert "exams_and_assessment" not in route.source_groups_to_search


def test_admission_without_exams_georgian_variants_route_to_admissions():
    for question in [
        "გამოცდების გარეშე ჩაბარება როგორ ხდება?",
        "ჩარიცხვა გამოცდების გარეშე შესაძლებელია?",
    ]:
        route = fallback_intent_route(question)
        assert route.source_groups_to_search[0] == "admissions_rules"
        assert route.department == "admissions"


def test_english_admission_without_exams_routes_to_admissions():
    assert forced_source_group("how can i apply without national exams?") == "admissions_rules"
    assert forced_source_group("admission without exams") == "admissions_rules"


def test_exam_rule_routing_preserved():
    for question in [
        "დასკვნით გამოცდაზე დაშვების წესი როგორია?",
        "დამატებით ან გადაბარების გამოცდაზე რა წესი მოქმედებს?",
    ]:
        route = fallback_intent_route(question)
        assert route.source_groups_to_search[0] == "exams_and_assessment"


def test_exam_date_routing_preserved():
    route = fallback_intent_route("დასკვნითი გამოცდები როდის არის?")
    assert route.source_groups_to_search[0] == "academic_calendar_2025_2026"


def test_english_program_requirements_routes_to_international_not_programs():
    route = validate_router_payload(
        route_payload(["official_academic_rules"]),
        message="What are the requirements for English-language programs?",
    )
    assert route.source_groups_to_search[0] == "international_admissions_sources"
    assert route.department == "international_admissions"
    assert route.department != "programs"


def test_english_program_requirements_department_resolver_routes_to_international():
    routing = resolve_department(
        message_text="What are the English-language program requirements if they are in the approved source?",
        ai_intent="information_request",
        ai_confidence=0.9,
        source_domain="join.alte.edu.ge",
        selected_department="international",
        selected_topic=None,
        risk_flags=[],
        used_sources=["approved international admissions source"],
        language="en",
        ai_department="International Admissions",
    )
    assert routing.department_key == "international"
    assert routing.department == "International Admissions"


def test_english_program_requirements_variants_route_to_international():
    for question in [
        "What English proficiency proof is required for international applicants?",
        "Do I need IELTS or TOEFL for English-taught programs?",
    ]:
        route = fallback_intent_route(question)
        assert route.source_groups_to_search[0] == "international_admissions_sources"
        assert route.department == "international_admissions"


def test_generic_program_question_does_not_become_international_admissions():
    route = fallback_intent_route("What programs do you offer?")
    assert route.department != "international_admissions"
    assert route.source_groups_to_search[:1] != ["international_admissions_sources"]


def test_mandatory_9at_controls_still_route_safely():
    assert forced_source_group("How many ECTS credits are required for bachelor completion?") == "official_academic_rules"
    assert forced_source_group("How many credits are required for a master program?") == "official_academic_rules"
    assert forced_source_group("How many years can student status be suspended?") == "student_status_and_mobility"


def test_explicit_operator_still_handover_without_source_group():
    route = fallback_intent_route("I want an operator")
    assert route.operator_needed is True
    assert route.source_groups_to_search == []


def test_public_launch_remains_no_go():
    assert "NO-GO" in PUBLIC_LAUNCH.read_text(encoding="utf-8", errors="ignore")
