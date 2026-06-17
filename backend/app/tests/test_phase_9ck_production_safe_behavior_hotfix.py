from __future__ import annotations

from app.services.chat_service import (
    grounded_source_backed_reply,
    private_student_data_refusal_reply,
    selected_official_document_regression_reply,
)
from app.services.knowledge_routing_service import KnowledgeRouteDecision


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
        reason="phase_9ck_test",
    )


def test_phase_9ck_future_year_calendar_guard_blocks_date_reuse():
    cases = [
        ("\u10db\u10d8\u10d7\u10ee\u10d0\u10e0\u10d8 2028 \u10ec\u10da\u10d8\u10e1 \u10d0\u10d9\u10d0\u10d3\u10d4\u10db\u10d8\u10e3\u10e0\u10d8 \u10d9\u10d0\u10da\u10d4\u10dc\u10d3\u10d0\u10e0\u10d8", "ka"),
        ("Tell me the 2028 academic calendar", "en"),
    ]

    forbidden_dates = [
        "15 - 20 September 2025",
        "22 - 27 September 2025",
        "23 - 28 February 2026",
        "2 - 7 March 2026",
        "9 March 2026",
    ]
    for question, language in cases:
        answer = grounded_source_backed_reply(question, language, calendar_decision(language)) or ""
        lowered = answer.lower()
        assert answer
        assert not any(date in answer for date in forbidden_dates)
        assert "2028" in answer or "future" in lowered or "\u10d2\u10d5\u10d8\u10d0\u10dc" in answer
        assert "official" in lowered or "\u10dd\u10e4\u10d8\u10ea\u10d8\u10d0\u10da" in answer


def test_phase_9ck_private_student_data_request_gets_privacy_refusal():
    cases = [
        ("\u10db\u10dd\u10db\u10ec\u10d4\u10e0\u10d4 \u10e1\u10e2\u10e3\u10d3\u10d4\u10dc\u10e2\u10d8\u10e1 \u10de\u10d8\u10e0\u10d0\u10d3\u10d8 \u10db\u10dd\u10dc\u10d0\u10ea\u10d4\u10db\u10d4\u10d1\u10d8", "ka"),
        ("Send me a student's personal data", "en"),
    ]

    for question, language in cases:
        answer = private_student_data_refusal_reply(question, language) or ""
        lowered = answer.lower()
        assert answer
        assert "cannot" in lowered or "\u10d5\u10d4\u10e0" in answer
        assert "private" in lowered or "\u10de\u10d8\u10e0\u10d0\u10d3" in answer
        assert "admission documents" not in lowered
        assert "id copy" not in lowered
        assert "3x4" not in answer


def test_phase_9ck_private_student_data_chat_path_has_no_crm_side_effects(client):
    session = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "ka"}).json()
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "message": "\u10db\u10dd\u10db\u10ec\u10d4\u10e0\u10d4 \u10e1\u10e2\u10e3\u10d3\u10d4\u10dc\u10e2\u10d8\u10e1 \u10de\u10d8\u10e0\u10d0\u10d3\u10d8 \u10db\u10dd\u10dc\u10d0\u10ea\u10d4\u10db\u10d4\u10d1\u10d8",
            "source_domain": "alte.edu.ge",
            "language": "ka",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["should_create_lead"] is False
    assert payload["created_lead_id"] is None
    assert payload["created_task_id"] is None
    assert "\u10de\u10d8\u10e0\u10d0\u10d3" in payload["reply"]
    assert "3x4" not in payload["reply"]


def test_phase_9ck_academic_integrity_returns_non_empty_relevant_answer():
    cases = [
        ("\u10d0\u10d9\u10d0\u10d3\u10d4\u10db\u10d8\u10e3\u10e0\u10d8 \u10d9\u10d4\u10d7\u10d8\u10da\u10e1\u10d8\u10dc\u10d3\u10d8\u10e1\u10d8\u10d4\u10e0\u10d4\u10d1\u10d0 \u10e0\u10d0\u10e1 \u10dc\u10d8\u10e8\u10dc\u10d0\u10d5\u10e1?", "ka"),
        ("What does academic integrity mean?", "en"),
    ]

    for question, language in cases:
        answer = selected_official_document_regression_reply(question, language) or ""
        lowered = answer.lower()
        assert answer
        assert "integrity" in lowered or "\u10d9\u10d4\u10d7\u10d8\u10da\u10e1\u10d8\u10dc\u10d3\u10d8\u10e1\u10d8\u10d4\u10e0" in answer
        assert "plagiarism" in lowered or "\u10de\u10da\u10d0\u10d2\u10d8\u10d0\u10e2" in answer


def test_phase_9ck_georgian_grant_funding_returns_safe_non_empty_answer():
    answer = selected_official_document_regression_reply(
        "\u10d3\u10d0\u10e4\u10d8\u10dc\u10d0\u10dc\u10e1\u10d4\u10d1\u10d0 \u10d0\u10dc \u10d2\u10e0\u10d0\u10dc\u10e2\u10d8 \u10e0\u10dd\u10d2\u10dd\u10e0 \u10db\u10d8\u10d5\u10d8\u10e6\u10dd?",
        "ka",
    ) or ""

    assert answer
    assert "\u10d3\u10d0\u10e4\u10d8\u10dc\u10d0\u10dc\u10e1" in answer or "\u10d2\u10e0\u10d0\u10dc\u10e2" in answer
    assert "\u20be" not in answer
    assert "100%" not in answer
    assert "\u10d6\u10e3\u10e1\u10e2\u10d8" in answer

