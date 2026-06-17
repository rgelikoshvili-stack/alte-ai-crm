from __future__ import annotations

import json
from pathlib import Path

from app.scripts.production_phase_9as_full_knowledge_coverage_qa import reply_body_for_token_checks
from app.services.chat_service import build_operator_request_reply, grounded_source_backed_reply
from app.services.claude_intent_router_service import fallback_intent_route, validate_router_payload
from app.services.knowledge_routing_service import KnowledgeRouteDecision


PROJECT_ROOT = Path(__file__).resolve().parents[3]
QA_DATASET = PROJECT_ROOT / "backend" / "app" / "data" / "evaluation" / "phase_9as_full_knowledge_qa.json"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"


def route_payload(groups: list[str]) -> dict:
    return {
        "intent": "information_request",
        "language": "en",
        "department": "Programs",
        "public_department_label": "Programs",
        "topic": "test",
        "needs_clarification": False,
        "clarification_question": None,
        "clarification_options": [],
        "source_groups_to_search": groups,
        "search_terms": ["test"],
        "operator_needed": False,
        "operator_reason": None,
        "unsupported_likely": False,
        "confidence": 0.9,
    }


def decision(group: str) -> KnowledgeRouteDecision:
    return KnowledgeRouteDecision(
        department_id="study_process",
        department_label="Study Process",
        source_groups=[group],
        primary_source_group=group,
        clarification_required=False,
        clarification_question=None,
        clarification_options=[],
        language="en",
        confidence=0.95,
        reason="phase_9aw_test",
    )


def dataset_by_id() -> dict[str, dict]:
    return {item["id"]: item for item in json.loads(QA_DATASET.read_text(encoding="utf-8"))}


def test_valid_official_status_route_specializes_to_student_status_group():
    route = validate_router_payload(
        route_payload(["official_academic_rules"]),
        message="How many years can student status be suspended?",
    )
    assert route.source_groups_to_search == ["student_status_and_mobility"]
    assert route.department == "study_process"


def test_valid_official_exam_route_specializes_to_exams_group():
    route = validate_router_payload(
        route_payload(["official_academic_rules"]),
        message="What does FX mean and when can a student retake an exam?",
    )
    assert route.source_groups_to_search == ["exams_and_assessment"]
    assert route.department == "study_process"


def test_georgian_final_exam_admission_route_specializes_to_exams_group():
    route = validate_router_payload(
        route_payload(["official_academic_rules"]),
        message="დასკვნით გამოცდაზე დაშვების წესი როგორია?",
    )
    assert route.source_groups_to_search == ["exams_and_assessment"]
    assert route.department == "study_process"


def test_georgian_retake_exam_rule_route_specializes_to_exams_group():
    route = validate_router_payload(
        route_payload(["official_academic_rules"]),
        message="დამატებით ან გადაბარების გამოცდაზე რა წესი მოქმედებს?",
    )
    assert route.source_groups_to_search == ["exams_and_assessment"]
    assert route.department == "study_process"


def test_georgian_exam_date_question_stays_calendar():
    route = validate_router_payload(
        route_payload(["official_academic_rules"]),
        message="დასკვნითი გამოცდები როდის არის?",
    )
    assert route.source_groups_to_search == ["academic_calendar_2025_2026"]


def test_fallback_georgian_final_exam_admission_primary_group_is_exams():
    route = fallback_intent_route("დასკვნით გამოცდაზე დაშვების წესი როგორია?")
    assert route.source_groups_to_search[0] == "exams_and_assessment"


def test_fallback_georgian_retake_exam_rule_primary_group_is_exams():
    route = fallback_intent_route("დამატებით ან გადაბარების გამოცდაზე რა წესი მოქმედებს?")
    assert route.source_groups_to_search[0] == "exams_and_assessment"


def test_fallback_georgian_exam_date_primary_group_stays_calendar():
    route = fallback_intent_route("დასკვნითი გამოცდები როდის არის?")
    assert route.source_groups_to_search[0] == "academic_calendar_2025_2026"


def test_valid_official_english_program_route_specializes_to_international_group():
    route = validate_router_payload(
        route_payload(["official_academic_rules"]),
        message="What are the English-language program requirements for international applicants?",
    )
    assert route.source_groups_to_search == ["international_admissions_sources"]
    assert route.department == "international_admissions"


def test_invalid_claude_group_still_does_not_get_filled_by_specialization():
    route = validate_router_payload(
        route_payload(["fake_group"]),
        message="What are the English-language program requirements for international applicants?",
    )
    assert route.router_validation_status == "invalid_source_groups"
    assert route.source_groups_to_search == []


def test_student_status_grounded_reply_contains_expected_fact_without_handover_language():
    reply = grounded_source_backed_reply(
        "How many years can student status be suspended?",
        "en",
        decision("student_status_and_mobility"),
    )
    assert reply is not None
    assert "5 years" in reply
    assert "operator" not in reply.lower()


def test_credit_recognition_grounded_reply_mentions_credit():
    reply = grounded_source_backed_reply(
        "How does credit recognition work?",
        "en",
        decision("student_status_and_mobility"),
    )
    assert reply is not None
    assert "Credit recognition" in reply
    assert "credits" in reply


def test_exam_group_grounded_reply_handles_gpa_and_retakes():
    gpa_reply = grounded_source_backed_reply("How is GPA calculated?", "en", decision("exams_and_assessment"))
    retake_reply = grounded_source_backed_reply("When can a student retake an exam?", "en", decision("exams_and_assessment"))
    assert gpa_reply is not None and "GPA" in gpa_reply and "0" in gpa_reply
    assert retake_reply is not None and "Retake" in retake_reply and "exam" in retake_reply.lower()


def test_token_checks_strip_clean_georgian_source_marker():
    body = "სტატუსის შეჩერება შესაძლებელია მაქსიმუმ 5 წლით.\n\nწყარო: page 10."
    assert reply_body_for_token_checks(body) == "სტატუსის შეჩერება შესაძლებელია მაქსიმუმ 5 წლით."


def test_georgian_finance_operator_reply_uses_localized_department_token():
    reply = build_operator_request_reply("ka", "Finance")
    assert "ფინანს" in reply
    assert "ოპერატორ" in reply


def test_operator_reply_has_single_georgian_return_path():
    source = (PROJECT_ROOT / "backend" / "app" / "services" / "chat_service.py").read_text(encoding="utf-8")
    function_source = source.split("def build_operator_request_reply", 1)[1].split("def is_ambiguous_program_question", 1)[0]
    assert function_source.count("return (") == 1
    assert function_source.count('return f"I can route this') == 1


def test_stale_9as_expectations_updated_for_route_only_and_unsupported_cases():
    data = dataset_by_id()
    for item_id in [
        "routing_finance_operator_ka",
        "unsupported_tuition_price_ka",
        "unsupported_library_rules_en",
        "unsupported_it_details_en",
        "operator_finance_handover_en",
    ]:
        assert data[item_id]["expected_source_group"] is None
    assert data["routing_international_medicine_en"]["should_handover_expected"] is False
    assert data["routing_international_medicine_en"]["human_handover_expected"] is False
    assert data["foreign_education_recognition_en"]["expected_source_group"] == "international_admissions_sources"
    assert data["foreign_applicant_en"]["expected_source_group"] == "international_admissions_sources"


def test_public_launch_remains_no_go():
    assert "NO-GO" in PUBLIC_LAUNCH.read_text(encoding="utf-8", errors="ignore")
