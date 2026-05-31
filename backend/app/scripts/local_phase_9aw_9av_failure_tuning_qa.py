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
        "topic": "phase_9aw",
        "needs_clarification": False,
        "clarification_question": None,
        "clarification_options": [],
        "source_groups_to_search": groups,
        "search_terms": ["phase_9aw"],
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
        reason="phase_9aw_local_qa",
    )


def check(name: str, condition: bool, detail: str = "") -> dict:
    return {"name": name, "status": "PASS" if condition else "FAIL", "detail": detail}


def main() -> int:
    results: list[dict] = []

    status_route = validate_router_payload(route_payload(["official_academic_rules"]), message="How many years can student status be suspended?")
    results.append(check("status_route_specialized", status_route.source_groups_to_search == ["student_status_and_mobility"], str(status_route.source_groups_to_search)))

    exam_route = validate_router_payload(route_payload(["official_academic_rules"]), message="What does FX mean and when can a student retake an exam?")
    results.append(check("exam_route_specialized", exam_route.source_groups_to_search == ["exams_and_assessment"], str(exam_route.source_groups_to_search)))

    georgian_final_exam_route = validate_router_payload(
        route_payload(["official_academic_rules"]),
        message="დასკვნით გამოცდაზე დაშვების წესი როგორია?",
    )
    results.append(check("georgian_final_exam_route_specialized", georgian_final_exam_route.source_groups_to_search == ["exams_and_assessment"], str(georgian_final_exam_route.source_groups_to_search)))

    georgian_retake_route = validate_router_payload(
        route_payload(["official_academic_rules"]),
        message="დამატებით ან გადაბარების გამოცდაზე რა წესი მოქმედებს?",
    )
    results.append(check("georgian_retake_exam_route_specialized", georgian_retake_route.source_groups_to_search == ["exams_and_assessment"], str(georgian_retake_route.source_groups_to_search)))

    georgian_exam_date_route = validate_router_payload(
        route_payload(["official_academic_rules"]),
        message="დასკვნითი გამოცდები როდის არის?",
    )
    results.append(check("georgian_exam_date_route_stays_calendar", georgian_exam_date_route.source_groups_to_search == ["academic_calendar_2025_2026"], str(georgian_exam_date_route.source_groups_to_search)))

    fallback_final_exam_route = fallback_intent_route("დასკვნით გამოცდაზე დაშვების წესი როგორია?")
    results.append(check("fallback_georgian_final_exam_primary_exams", fallback_final_exam_route.source_groups_to_search[:1] == ["exams_and_assessment"], str(fallback_final_exam_route.source_groups_to_search)))

    fallback_retake_route = fallback_intent_route("დამატებით ან გადაბარების გამოცდაზე რა წესი მოქმედებს?")
    results.append(check("fallback_georgian_retake_primary_exams", fallback_retake_route.source_groups_to_search[:1] == ["exams_and_assessment"], str(fallback_retake_route.source_groups_to_search)))

    fallback_exam_date_route = fallback_intent_route("დასკვნითი გამოცდები როდის არის?")
    results.append(check("fallback_georgian_exam_date_primary_calendar", fallback_exam_date_route.source_groups_to_search[:1] == ["academic_calendar_2025_2026"], str(fallback_exam_date_route.source_groups_to_search)))

    intl_route = validate_router_payload(
        route_payload(["official_academic_rules"]),
        message="What are the English-language program requirements for international applicants?",
    )
    results.append(check("international_route_specialized", intl_route.source_groups_to_search == ["international_admissions_sources"], str(intl_route.source_groups_to_search)))

    invalid_route = validate_router_payload(route_payload(["fake_group"]), message="How does credit recognition work?")
    results.append(check("invalid_group_not_specialized", invalid_route.source_groups_to_search == [], str(invalid_route.source_groups_to_search)))

    credit_reply = grounded_source_backed_reply("How does credit recognition work?", "en", decision("student_status_and_mobility")) or ""
    results.append(check("credit_reply_mentions_credit", "Credit recognition" in credit_reply and "credits" in credit_reply, credit_reply))

    retake_reply = grounded_source_backed_reply("When can a student retake an exam?", "en", decision("exams_and_assessment")) or ""
    results.append(check("retake_reply_mentions_exam", "exam" in retake_reply.lower(), retake_reply))

    stripped = reply_body_for_token_checks("სტატუსის შეჩერება შესაძლებელია მაქსიმუმ 5 წლით.\n\nწყარო: page 10.")
    results.append(check("georgian_source_marker_stripped", "10" not in stripped and "5 წლით" in stripped, stripped))

    finance_reply = build_operator_request_reply("ka", "Finance")
    results.append(check("finance_operator_localized", "ფინანს" in finance_reply and "ოპერატორ" in finance_reply, finance_reply))

    chat_service_source = (PROJECT_ROOT / "backend" / "app" / "services" / "chat_service.py").read_text(encoding="utf-8", errors="ignore")
    operator_function = chat_service_source.split("def build_operator_request_reply", 1)[1].split("def is_ambiguous_program_question", 1)[0]
    results.append(check("operator_reply_duplicate_removed", operator_function.count("return (") == 1 and operator_function.count('return f"I can route this') == 1))

    data = {item["id"]: item for item in json.loads(QA_DATASET.read_text(encoding="utf-8"))}
    stale_ids = [
        "routing_finance_operator_ka",
        "unsupported_tuition_price_ka",
        "unsupported_library_rules_en",
        "unsupported_it_details_en",
        "operator_finance_handover_en",
    ]
    results.append(check("route_only_unsupported_expected_groups_null", all(data[item_id]["expected_source_group"] is None for item_id in stale_ids)))
    results.append(check("international_medicine_no_handover_expected", data["routing_international_medicine_en"]["should_handover_expected"] is False))
    results.append(check("foreign_recognition_expected_international_group", data["foreign_education_recognition_en"]["expected_source_group"] == "international_admissions_sources"))
    results.append(check("public_launch_no_go", "NO-GO" in PUBLIC_LAUNCH.read_text(encoding="utf-8", errors="ignore")))

    failed = [item for item in results if item["status"] != "PASS"]
    print(json.dumps({"phase": "9AW", "total": len(results), "passed": len(results) - len(failed), "failed": len(failed), "checks": results}, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
