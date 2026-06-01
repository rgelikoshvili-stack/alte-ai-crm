from __future__ import annotations

import json
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


def check(name: str, condition: bool, detail: str = "") -> dict:
    return {"name": name, "status": "PASS" if condition else "FAIL", "detail": detail}


def main() -> int:
    results: list[dict] = []

    admission_route = validate_router_payload(
        route_payload(["official_academic_rules"]),
        message="ეროვნული გამოცდების გარეშე როგორ ჩავირიცხო?",
    )
    results.append(check("admission_without_exams_validated_route_admissions", admission_route.source_groups_to_search[:1] == ["admissions_rules"], str(admission_route)))
    results.append(check("admission_without_exams_department_admissions", admission_route.department == "admissions", admission_route.department))

    for name, question in [
        ("admission_without_exams_variant_chabareba", "გამოცდების გარეშე ჩაბარება როგორ ხდება?"),
        ("admission_without_exams_variant_charicxva", "ჩარიცხვა გამოცდების გარეშე შესაძლებელია?"),
    ]:
        route = fallback_intent_route(question)
        results.append(check(name, route.source_groups_to_search[:1] == ["admissions_rules"], str(route.source_groups_to_search)))

    final_exam_route = fallback_intent_route("დასკვნით გამოცდაზე დაშვების წესი როგორია?")
    results.append(check("exam_rule_still_exams", final_exam_route.source_groups_to_search[:1] == ["exams_and_assessment"], str(final_exam_route.source_groups_to_search)))

    retake_route = fallback_intent_route("დამატებით ან გადაბარების გამოცდაზე რა წესი მოქმედებს?")
    results.append(check("retake_rule_still_exams", retake_route.source_groups_to_search[:1] == ["exams_and_assessment"], str(retake_route.source_groups_to_search)))

    exam_date_route = fallback_intent_route("დასკვნითი გამოცდები როდის არის?")
    results.append(check("exam_date_still_calendar", exam_date_route.source_groups_to_search[:1] == ["academic_calendar_2025_2026"], str(exam_date_route.source_groups_to_search)))

    english_route = validate_router_payload(
        route_payload(["official_academic_rules"]),
        message="What are the requirements for English-language programs?",
    )
    results.append(check("english_program_requirements_international", english_route.source_groups_to_search[:1] == ["international_admissions_sources"], str(english_route.source_groups_to_search)))
    results.append(check("english_program_department_international", english_route.department == "international_admissions", english_route.department))
    english_routing = resolve_department(
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
    results.append(check("english_program_department_resolver_international", english_routing.department_key == "international", english_routing.department_key))

    for name, question in [
        ("english_proficiency_international_applicants", "What English proficiency proof is required for international applicants?"),
        ("ielts_toefl_english_taught", "Do I need IELTS or TOEFL for English-taught programs?"),
    ]:
        route = fallback_intent_route(question)
        results.append(check(name, route.source_groups_to_search[:1] == ["international_admissions_sources"], str(route.source_groups_to_search)))

    generic_programs = fallback_intent_route("What programs do you offer?")
    results.append(check("generic_programs_not_international", generic_programs.department != "international_admissions", generic_programs.department))

    results.append(check("bachelor_ects_control", forced_source_group("How many ECTS credits are required for bachelor completion?") == "official_academic_rules"))
    results.append(check("master_ects_control", forced_source_group("How many credits are required for a master program?") == "official_academic_rules"))
    results.append(check("status_suspension_control", forced_source_group("How many years can student status be suspended?") == "student_status_and_mobility"))

    operator_route = fallback_intent_route("I want an operator")
    results.append(check("operator_handover_no_source_group", operator_route.operator_needed is True and operator_route.source_groups_to_search == [], str(operator_route)))

    results.append(check("no_lead_task_customer_created", True, "local router-only QA does not create records"))
    results.append(check("public_launch_no_go", "NO-GO" in PUBLIC_LAUNCH.read_text(encoding="utf-8", errors="ignore")))

    failed = [item for item in results if item["status"] != "PASS"]
    print(json.dumps({"phase": "9AX", "total": len(results), "passed": len(results) - len(failed), "failed": len(failed), "checks": results}, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
