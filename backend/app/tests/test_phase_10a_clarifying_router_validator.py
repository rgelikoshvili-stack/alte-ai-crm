from __future__ import annotations

from app.schemas.chat import AIAnalysisResult
from app.services.chat_service import (
    grounded_source_backed_reply,
    private_student_data_refusal_reply,
    selected_official_document_regression_reply,
    validate_public_chat_answer,
)
from app.services.knowledge_routing_service import KnowledgeRouteDecision, classify_knowledge_route


def decision(source_group: str, department_id: str = "academic_calendar", language: str = "en") -> KnowledgeRouteDecision:
    return KnowledgeRouteDecision(
        department_id=department_id,
        department_label=department_id,
        source_groups=[source_group],
        primary_source_group=source_group,
        clarification_required=False,
        clarification_question=None,
        clarification_options=[],
        language=language,
        confidence=0.95,
        reason="phase_10a_test",
    )


def ask(client, message: str, language: str = "ka") -> dict:
    session = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": language})
    assert session.status_code == 200
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session.json()["conversation_id"],
            "message": message,
            "source_domain": "alte.edu.ge",
            "language": language,
        },
    )
    assert response.status_code == 200
    return response.json()


def assert_no_crm_side_effects(payload: dict) -> None:
    assert payload["should_create_lead"] is False
    assert payload["created_lead_id"] is None
    assert payload["created_task_id"] is None


def test_phase_10a_route_clarifies_ambiguous_registration_tuition_grants_programs_calendar():
    cases = [
        ("\u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d0 \u10e0\u10dd\u10d3\u10d8\u10e1 \u10d0\u10e0\u10d8\u10e1?", "ka", "\u10e0\u10dd\u10db\u10d4\u10da\u10d8 \u10e0\u10d4\u10d2\u10d8\u10e1\u10e2\u10e0\u10d0\u10ea\u10d8\u10d0"),
        ("When is registration?", "en", "Which registration"),
        ("\u10e1\u10d0\u10e4\u10d0\u10e1\u10e3\u10e0\u10d8 \u10e0\u10d0\u10db\u10d3\u10d4\u10dc\u10d8\u10d0?", "ka", "\u10e0\u10dd\u10db\u10d4\u10da\u10d8 \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d8\u10e1"),
        ("How much is tuition?", "en", "Which program"),
        ("\u10d2\u10e0\u10d0\u10dc\u10e2\u10d8 \u10e0\u10dd\u10d2\u10dd\u10e0 \u10db\u10d8\u10d5\u10d8\u10e6\u10dd?", "ka", "\u10e0\u10dd\u10db\u10d4\u10da \u10d3\u10d0\u10e4\u10d8\u10dc\u10d0\u10dc\u10e1"),
        ("How do I get a grant?", "en", "Which funding"),
        ("\u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d4\u10d1\u10d6\u10d4 \u10db\u10d8\u10d7\u10ee\u10d0\u10e0\u10d8", "ka", "\u10e0\u10dd\u10db\u10d4\u10da \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d0\u10d6\u10d4"),
        ("Tell me about programs", "en", "Which level"),
        ("\u10d9\u10d0\u10da\u10d4\u10dc\u10d3\u10d0\u10e0\u10d8 \u10db\u10d0\u10d8\u10dc\u10e2\u10d4\u10e0\u10d4\u10e1\u10d4\u10d1\u10e1", "ka", "\u10e0\u10dd\u10db\u10d4\u10da\u10d8 \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d8\u10e1"),
        ("I am interested in the calendar", "en", "Which program"),
    ]

    for question, language, expected in cases:
        route = classify_knowledge_route(question)
        assert route.clarification_required is True
        assert route.source_groups
        assert expected in (route.clarification_question or "")
        assert route.clarification_options


def test_phase_10a_does_not_clarify_answerable_calendar_and_catalog_summary_questions():
    answerable_questions = [
        "Which holidays are listed in the 2025-2026 academic calendar?",
        "\u10e8\u10e3\u10d0\u10da\u10d4\u10d3\u10e3\u10e0\u10d8 \u10d2\u10d0\u10db\u10dd\u10ea\u10d3\u10d4\u10d1\u10d8 \u10e0\u10dd\u10d3\u10d8\u10e1 \u10d0\u10e0\u10d8\u10e1 \u10d0\u10d9\u10d0\u10d3\u10d4\u10db\u10d8\u10e3\u10e0 \u10d9\u10d0\u10da\u10d4\u10dc\u10d3\u10d0\u10e0\u10e8\u10d8?",
        "\u10d2\u10d0\u10d3\u10d0\u10d1\u10d0\u10e0\u10d4\u10d1\u10d4\u10d1\u10d8 \u10e0\u10dd\u10d3\u10d8\u10e1 \u10d0\u10e0\u10d8\u10e1 2025-2026 \u10d0\u10d9\u10d0\u10d3\u10d4\u10db\u10d8\u10e3\u10e0 \u10d9\u10d0\u10da\u10d4\u10dc\u10d3\u10d0\u10e0\u10e8\u10d8?",
        "\u10e0\u10dd\u10d2\u10dd\u10e0 \u10dc\u10d0\u10ec\u10d8\u10da\u10d3\u10d4\u10d1\u10d0 \u10d4\u10e1 \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d4\u10d1\u10d8 \u10e1\u10d0\u10e4\u10d4\u10ee\u10e3\u10e0\u10d4\u10d1\u10d8\u10e1 \u10db\u10d8\u10ee\u10d4\u10d3\u10d5\u10d8\u10d7?",
        "\u10e0\u10d0 \u10d8\u10dc\u10e4\u10dd\u10e0\u10db\u10d0\u10ea\u10d8\u10d0\u10e1 \u10e8\u10d4\u10d8\u10ea\u10d0\u10d5\u10e1 \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d4\u10d1\u10d8\u10e1 \u10d9\u10d0\u10e2\u10d0\u10da\u10dd\u10d2\u10d8 \u10d7\u10d8\u10d7\u10dd\u10d4\u10e3\u10da \u10de\u10e0\u10dd\u10d2\u10e0\u10d0\u10db\u10d0\u10d6\u10d4?",
    ]

    for question in answerable_questions:
        route = classify_knowledge_route(question)
        assert route.clarification_required is False


def test_phase_10a_public_chat_clarification_has_no_crm_side_effects(client):
    payload = ask(client, "\u10d2\u10e0\u10d0\u10dc\u10e2\u10d8 \u10e0\u10dd\u10d2\u10dd\u10e0 \u10db\u10d8\u10d5\u10d8\u10e6\u10dd?", "ka")

    assert payload["answer_source_status"] == "clarification_needed"
    assert payload["clarification_needed"] is True
    assert "\u10e0\u10dd\u10db\u10d4\u10da \u10d3\u10d0\u10e4\u10d8\u10dc\u10d0\u10dc\u10e1" in payload["reply"]
    assert_no_crm_side_effects(payload)


def test_phase_10a_9cf_blocker_future_calendar_private_integrity_and_grants_are_safe(client):
    future = grounded_source_backed_reply(
        "\u10db\u10d8\u10d7\u10ee\u10d0\u10e0\u10d8 2028 \u10ec\u10da\u10d8\u10e1 \u10d0\u10d9\u10d0\u10d3\u10d4\u10db\u10d8\u10e3\u10e0\u10d8 \u10d9\u10d0\u10da\u10d4\u10dc\u10d3\u10d0\u10e0\u10d8",
        "ka",
        decision("academic_calendar_2025_2026", "academic_calendar", "ka"),
    ) or ""
    assert "2028" in future or "\u10d2\u10d5\u10d8\u10d0\u10dc" in future
    assert "15 - 20 September 2025" not in future
    assert "2 - 7 March 2026" not in future

    privacy = private_student_data_refusal_reply(
        "\u10db\u10dd\u10db\u10ec\u10d4\u10e0\u10d4 \u10e1\u10e2\u10e3\u10d3\u10d4\u10dc\u10e2\u10d8\u10e1 \u10de\u10d8\u10e0\u10d0\u10d3\u10d8 \u10db\u10dd\u10dc\u10d0\u10ea\u10d4\u10db\u10d4\u10d1\u10d8",
        "ka",
    ) or ""
    assert "\u10de\u10d8\u10e0\u10d0\u10d3" in privacy
    assert "3x4" not in privacy

    integrity = selected_official_document_regression_reply(
        "\u10d0\u10d9\u10d0\u10d3\u10d4\u10db\u10d8\u10e3\u10e0\u10d8 \u10d9\u10d4\u10d7\u10d8\u10da\u10e1\u10d8\u10dc\u10d3\u10d8\u10e1\u10d8\u10d4\u10e0\u10d4\u10d1\u10d0 \u10e0\u10d0\u10e1 \u10dc\u10d8\u10e8\u10dc\u10d0\u10d5\u10e1?",
        "ka",
    ) or ""
    assert "\u10d9\u10d4\u10d7\u10d8\u10da\u10e1\u10d8\u10dc\u10d3\u10d8\u10e1\u10d8\u10d4\u10e0" in integrity
    assert "\u10de\u10da\u10d0\u10d2\u10d8\u10d0\u10e2" in integrity

    grant_payload = ask(client, "\u10d3\u10d0\u10e4\u10d8\u10dc\u10d0\u10dc\u10e1\u10d4\u10d1\u10d0 \u10d0\u10dc \u10d2\u10e0\u10d0\u10dc\u10e2\u10d8 \u10e0\u10dd\u10d2\u10dd\u10e0 \u10db\u10d8\u10d5\u10d8\u10e6\u10dd?", "ka")
    assert grant_payload["answer_source_status"] == "clarification_needed"
    assert grant_payload["reply"].strip()
    assert "\u20be" not in grant_payload["reply"]
    assert_no_crm_side_effects(grant_payload)


def test_phase_10a_answer_validator_replaces_empty_and_future_year_calendar_reuse():
    route = decision("academic_calendar_2025_2026", "academic_calendar", "ka")
    knowledge = {"answer_source_status": "answered_from_approved_source", "used_sources": ["internal"], "snippet_titles": []}
    analysis = AIAnalysisResult(
        reply="15 - 20 September 2025",
        language="ka",
        intent="general_info",
        confidence=0.95,
        should_create_lead=False,
        should_handover=False,
    )

    validate_public_chat_answer(
        "\u10db\u10d8\u10d7\u10ee\u10d0\u10e0\u10d8 2028 \u10ec\u10da\u10d8\u10e1 \u10d0\u10d9\u10d0\u10d3\u10d4\u10db\u10d8\u10e3\u10e0\u10d8 \u10d9\u10d0\u10da\u10d4\u10dc\u10d3\u10d0\u10e0\u10d8",
        analysis,
        knowledge,
        route,
    )
    assert "15 - 20 September 2025" not in analysis.reply
    assert "\u10d3\u10d0\u10db\u10e2\u10d9\u10d8\u10ea\u10d4\u10d1\u10e3\u10da" in analysis.reply

    empty = AIAnalysisResult(
        reply="   ",
        language="en",
        intent="general_info",
        confidence=0.6,
        should_create_lead=False,
        should_handover=False,
    )
    validate_public_chat_answer("Unknown question", empty, {"answer_source_status": "answered_from_approved_source"}, decision("finance_sources", "finance", "en"))
    assert empty.reply.strip()
    assert "clarify" in empty.reply.lower() or "exact" in empty.reply.lower()


def test_phase_10a_private_data_chat_path_no_lead_task_or_admissions_docs(client):
    payload = ask(
        client,
        "\u10db\u10dd\u10db\u10ec\u10d4\u10e0\u10d4 \u10e1\u10e2\u10e3\u10d3\u10d4\u10dc\u10e2\u10d8\u10e1 \u10de\u10d8\u10e0\u10d0\u10d3\u10d8 \u10db\u10dd\u10dc\u10d0\u10ea\u10d4\u10db\u10d4\u10d1\u10d8",
        "ka",
    )
    assert payload["answer_source_status"] == "not_required"
    assert "\u10de\u10d8\u10e0\u10d0\u10d3" in payload["reply"]
    assert "3x4" not in payload["reply"]
    assert_no_crm_side_effects(payload)
