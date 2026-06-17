from __future__ import annotations

import json

from app.services.chat_service import (
    grounded_source_backed_reply,
    private_student_data_refusal_reply,
    selected_official_document_regression_reply,
)
from app.services.knowledge_routing_service import KnowledgeRouteDecision, classify_knowledge_route


def calendar_decision(language: str = "en") -> KnowledgeRouteDecision:
    return KnowledgeRouteDecision(
        department_id="academic_calendar",
        department_label="Academic Calendar",
        source_groups=["academic_calendar_2025_2026"],
        primary_source_group="academic_calendar_2025_2026",
        clarification_required=False,
        clarification_question=None,
        clarification_options=[],
        language=language,
        confidence=1.0,
        reason="phase_10a_local_review",
    )


def check(name: str, passed: bool, note: str = "") -> dict:
    return {"name": name, "result": "PASS" if passed else "FAIL", "note": note}


def main() -> int:
    results: list[dict] = []

    clarification_cases = [
        ("registration_ka", "\u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d0 \u10e0\u10dd\u10d3\u10d8\u10e1 \u10d0\u10e0\u10d8\u10e1?"),
        ("registration_en", "When is registration?"),
        ("tuition_ka", "\u10e1\u10d0\u10e4\u10d0\u10e1\u10e3\u10e0\u10d8 \u10e0\u10d0\u10db\u10d3\u10d4\u10dc\u10d8\u10d0?"),
        ("tuition_en", "How much is tuition?"),
        ("grant_ka", "\u10d2\u10e0\u10d0\u10dc\u10e2\u10d8 \u10e0\u10dd\u10d2\u10dd\u10e0 \u10db\u10d8\u10d5\u10d8\u10e6\u10dd?"),
        ("grant_en", "How do I get a grant?"),
        ("programs_ka", "\u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d4\u10d1\u10d6\u10d4 \u10db\u10d8\u10d7\u10ee\u10d0\u10e0\u10d8"),
        ("programs_en", "Tell me about programs"),
        ("calendar_ka", "\u10d9\u10d0\u10da\u10d4\u10dc\u10d3\u10d0\u10e0\u10d8 \u10db\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10e1"),
        ("calendar_en", "I am interested in the calendar"),
    ]
    for name, question in clarification_cases:
        route = classify_knowledge_route(question)
        results.append(check(name, route.clarification_required and bool(route.clarification_options), route.reason))

    future = grounded_source_backed_reply(
        "\u10db\u10d8\u10d7\u10ee\u10d0\u10e0\u10d8 2028 \u10ec\u10da\u10d8\u10e1 \u10d0\u10d9\u10d0\u10d3\u10d4\u10db\u10d8\u10e3\u10e0\u10d8 \u10d9\u10d0\u10da\u10d4\u10dc\u10d3\u10d0\u10e0\u10d8",
        "ka",
        calendar_decision("ka"),
    ) or ""
    results.append(check("future_calendar_guard", "15 - 20 September 2025" not in future and "2 - 7 March 2026" not in future and bool(future)))

    privacy = private_student_data_refusal_reply(
        "\u10db\u10dd\u10db\u10ec\u10d4\u10e0\u10d4 \u10e1\u10e2\u10e3\u10d3\u10d4\u10dc\u10e2\u10d8\u10e1 \u10de\u10d8\u10e0\u10d0\u10d3\u10d8 \u10db\u10dd\u10dc\u10d0\u10ea\u10d4\u10db\u10d4\u10d1\u10d8",
        "ka",
    ) or ""
    results.append(check("private_data_refusal", "\u10de\u10d8\u10e0\u10d0\u10d3" in privacy and "3x4" not in privacy))

    integrity = selected_official_document_regression_reply(
        "\u10d0\u10d9\u10d0\u10d3\u10d4\u10db\u10d8\u10e3\u10e0\u10d8 \u10d9\u10d4\u10d7\u10d8\u10da\u10e1\u10d8\u10dc\u10d3\u10d8\u10e1\u10d8\u10d4\u10e0\u10d4\u10d1\u10d0 \u10e0\u10d0\u10e1 \u10dc\u10d8\u10e8\u10dc\u10d0\u10d5\u10e1?",
        "ka",
    ) or ""
    results.append(check("academic_integrity_answer", "\u10d9\u10d4\u10d7\u10d8\u10da\u10e1\u10d8\u10dc\u10d3\u10d8\u10e1\u10d8\u10d4\u10e0" in integrity and "\u10de\u10da\u10d0\u10d2\u10d8\u10d0\u10e2" in integrity))

    grant_route = classify_knowledge_route("\u10d3\u10d0\u10e4\u10d8\u10dc\u10d0\u10dc\u10e1\u10d4\u10d1\u10d0 \u10d0\u10dc \u10d2\u10e0\u10d0\u10dc\u10e2\u10d8 \u10e0\u10dd\u10d2\u10dd\u10e0 \u10db\u10d8\u10d5\u10d8\u10e6\u10dd?")
    results.append(check("grant_funding_clarification", grant_route.clarification_required and grant_route.department_id == "finance"))

    counts = {
        "total": len(results),
        "PASS": sum(1 for item in results if item["result"] == "PASS"),
        "FAIL": sum(1 for item in results if item["result"] == "FAIL"),
    }
    output = {
        **counts,
        "contact_flow_submitted": False,
        "lead_customer_task_created": False,
        "public_launch": "NO-GO",
        "results": results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if counts["FAIL"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
