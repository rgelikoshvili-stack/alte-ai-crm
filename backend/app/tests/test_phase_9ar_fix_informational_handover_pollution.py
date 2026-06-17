from __future__ import annotations

import asyncio
from pathlib import Path

from sqlalchemy import select

from app.models import Conversation, Customer, Lead, Task
from app.schemas.chat import AIAnalysisResult, ExtractedContact
from app.services import chat_service


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"


BACHELOR_ECTS_QUESTION = "რამდენი ECTS კრედიტია საჭირო საბაკალავრო პროგრამის დასასრულებლად?"
MASTER_ECTS_QUESTION = "რამდენი კრედიტია სამაგისტრო პროგრამა ალტე უნივერსიტეტში?"
UNSUPPORTED_QUESTION = "2031 წლის კოსმოსური კამპუსის სტიპენდია როგორ მივიღო?"


def fetch_all(session_factory, query):
    async def run():
        async with session_factory() as session:
            return (await session.scalars(query)).all()

    return asyncio.run(run())


def start_session(client, language: str = "ka") -> dict:
    response = client.post("/chat/session/start", json={"source_domain": "join.alte.edu.ge", "language": language})
    assert response.status_code == 200
    return response.json()


def send_message(client, session: dict, message: str, language: str = "ka") -> dict:
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": message,
            "source_domain": "join.alte.edu.ge",
            "language": language,
            "widget_variant": "pro_v2_safe",
        },
    )
    assert response.status_code == 200
    return response.json()


def seed_official_ects_rules(client) -> None:
    source = client.post(
        "/knowledge/sources",
        json={
            "source_key": "phase_9ar_official_academic_rules",
            "title": "Phase 9AR official academic rules",
            "source_type": "pdf",
            "status": "approved",
            "language": "ka",
            "source_domain": "official_academic_rules",
            "category": "academic_rules",
            "sensitivity": "official academic rule",
        },
    )
    assert source.status_code == 200
    source_payload = source.json()
    snippets = [
        (
            "Bachelor ECTS",
            "საბაკალავრო პროგრამის დასასრულებლად საჭიროა არანაკლებ 240 ECTS კრედიტის დაგროვება.",
            "საბაკალავრო ბაკალავრიატი bachelor ECTS კრედიტი 240 პროგრამის დასასრულებლად",
        ),
        (
            "Master ECTS",
            "სამაგისტრო პროგრამისთვის საჭიროა არანაკლებ 120 ECTS კრედიტის დაგროვება.",
            "სამაგისტრო მაგისტრატურა master ECTS კრედიტი 120",
        ),
    ]
    for title, content, keywords in snippets:
        response = client.post(
            "/knowledge/snippets",
            json={
                "source_id": source_payload["id"],
                "source_key": source_payload["source_key"],
                "title": title,
                "content": content,
                "category": "academic_rules",
                "source_domain": "official_academic_rules",
                "sensitivity": "official academic rule",
                "keywords": keywords,
                "status": "approved",
                "language": "ka",
            },
        )
        assert response.status_code == 200


def patch_analysis(monkeypatch, *, intent: str, reply: str, confidence: float = 0.92, should_handover: bool = False) -> None:
    monkeypatch.setattr(
        chat_service,
        "analyze_with_ai",
        lambda *args, **kwargs: (
            AIAnalysisResult(
                reply=reply,
                language="ka",
                intent=intent,
                confidence=confidence,
                should_create_lead=False,
                should_handover=should_handover,
                extracted_contact=ExtractedContact(),
                conversation_summary="Phase 9AR regression",
            ),
            {"provider": "test", "model": "forced", "raw_response": None},
        ),
    )


def assert_no_crm_records(session_factory) -> None:
    assert fetch_all(session_factory, select(Customer)) == []
    assert fetch_all(session_factory, select(Lead)) == []
    assert fetch_all(session_factory, select(Task)) == []


def conversation_by_id(session_factory, conversation_id: str) -> Conversation:
    rows = fetch_all(session_factory, select(Conversation).where(Conversation.id == conversation_id))
    assert len(rows) == 1
    return rows[0]


def test_bachelor_ects_source_backed_does_not_mark_handover(client, session_factory, monkeypatch):
    seed_official_ects_rules(client)
    patch_analysis(monkeypatch, intent="human_request", reply="გადავამისამართებ ოპერატორთან.", should_handover=True)
    session = start_session(client)

    payload = send_message(client, session, BACHELOR_ECTS_QUESTION)

    assert payload["answer_source_status"] == "answered_from_approved_source"
    assert "240" in payload["reply"]
    assert payload["should_handover"] is False
    assert payload["handover_reason"] is None
    assert payload["department_key"] == "programs"
    assert payload["route_department"] == "Programs"
    assert payload["created_lead_id"] is None
    assert payload["created_task_id"] is None
    assert conversation_by_id(session_factory, session["conversation_id"]).human_handover is False
    assert_no_crm_records(session_factory)


def test_master_ects_source_backed_does_not_mark_handover(client, session_factory, monkeypatch):
    seed_official_ects_rules(client)
    patch_analysis(monkeypatch, intent="general_info", reply="სამაგისტრო კრედიტებზე გიპასუხებთ.", should_handover=True)
    session = start_session(client)

    payload = send_message(client, session, MASTER_ECTS_QUESTION)

    assert payload["answer_source_status"] == "answered_from_approved_source"
    assert "120" in payload["reply"]
    assert payload["should_handover"] is False
    assert payload["department_key"] == "programs"
    assert conversation_by_id(session_factory, session["conversation_id"]).human_handover is False
    assert_no_crm_records(session_factory)


def test_clarification_still_does_not_mark_handover(client, session_factory):
    session = start_session(client)

    payload = send_message(client, session, "სწავლა მაინტერესებს")

    assert payload["clarification_needed"] is True
    assert payload["should_handover"] is False
    assert conversation_by_id(session_factory, session["conversation_id"]).human_handover is False
    assert_no_crm_records(session_factory)


def test_unsupported_still_allows_operator_fallback(client, session_factory, monkeypatch):
    patch_analysis(monkeypatch, intent="finance_question", reply="ზუსტი წყარო ვერ ვიპოვე.", should_handover=False)
    session = start_session(client)

    payload = send_message(client, session, UNSUPPORTED_QUESTION)

    assert payload["answer_source_status"] == "no_approved_source_found"
    assert payload["should_handover"] is True
    assert "კოსმოსური კამპუსის სტიპენდია არის" not in payload["reply"]
    assert payload["created_lead_id"] is None
    assert payload["created_task_id"] is None
    assert conversation_by_id(session_factory, session["conversation_id"]).human_handover is True
    assert_no_crm_records(session_factory)


def test_explicit_operator_request_still_marks_handover(client, session_factory, monkeypatch):
    patch_analysis(monkeypatch, intent="human_request", reply="ოპერატორთან დაგაკავშირებთ.", should_handover=True)
    session = start_session(client)

    payload = send_message(client, session, "მინდა ოპერატორთან დაკავშირება")

    assert payload["should_handover"] is True
    assert conversation_by_id(session_factory, session["conversation_id"]).human_handover is True
    assert payload["created_lead_id"] is None
    assert payload["created_task_id"] is None
    assert_no_crm_records(session_factory)


def test_finance_operator_request_still_marks_handover(client, session_factory, monkeypatch):
    patch_analysis(monkeypatch, intent="human_request", reply="ფინანსურ დეპარტამენტთან დაგაკავშირებთ.", should_handover=True)
    session = start_session(client)

    payload = send_message(client, session, "მინდა ფინანსურ დეპარტამენტთან დაკავშირება")

    assert payload["department_key"] == "finance"
    assert payload["should_handover"] is True
    assert conversation_by_id(session_factory, session["conversation_id"]).human_handover is True
    assert payload["created_lead_id"] is None
    assert payload["created_task_id"] is None
    assert_no_crm_records(session_factory)


def test_wait_for_operator_action_still_marks_waiting(client, session_factory):
    session = start_session(client)
    response = client.post(
        f"/chat/handover/{session['conversation_id']}",
        json={
            "session_id": session["session_id"],
            "selected_department": "programs",
            "reason": "wait_for_operator",
            "mode": "waiting_for_operator",
            "message": "მინდა ოპერატორს დაველოდო",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "waiting_for_operator"
    conversation = conversation_by_id(session_factory, session["conversation_id"])
    assert conversation.status == "waiting_for_operator"
    assert conversation.human_handover is True
    assert_no_crm_records(session_factory)


def test_phase_9ar_safety_no_public_launch_or_real_contact_data():
    public = PUBLIC_LAUNCH.read_text(encoding="utf-8").lower()

    assert "public_launch_decision=go" not in public
    assert "no-go" in public
