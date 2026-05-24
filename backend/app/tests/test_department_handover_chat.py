import asyncio

from sqlalchemy import select

from app.models import Customer, Lead, Task
from app.schemas.chat import AIAnalysisResult, ExtractedContact
from app.services import chat_service


def fetch_all(session_factory, query):
    async def run():
        async with session_factory() as session:
            return (await session.scalars(query)).all()

    return asyncio.run(run())


def start_session(client, source_domain="alte.edu.ge", language="ka"):
    response = client.post("/chat/session/start", json={"source_domain": source_domain, "language": language})
    assert response.status_code == 200
    return response.json()


def send_message(
    client,
    session,
    message,
    *,
    source_domain="alte.edu.ge",
    language="ka",
    selected_department=None,
    selected_topic=None,
):
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": message,
            "source_domain": source_domain,
            "language": language,
            "selected_department": selected_department,
            "selected_topic": selected_topic,
            "widget_variant": "safe_pro",
        },
    )
    assert response.status_code == 200
    return response.json()


def patch_analysis(monkeypatch, analysis: AIAnalysisResult) -> None:
    monkeypatch.setattr(
        chat_service,
        "analyze_with_ai",
        lambda *args, **kwargs: (analysis, {"provider": "test", "model": "forced", "raw_response": None}),
    )


def no_crm_side_effects(session_factory):
    assert fetch_all(session_factory, select(Customer)) == []
    assert fetch_all(session_factory, select(Lead)) == []
    assert fetch_all(session_factory, select(Task)) == []


def analysis_for(intent="general_info", confidence=0.9, reply="I need official confirmation.", contact=None):
    return AIAnalysisResult(
        reply=reply,
        language="en",
        intent=intent,
        confidence=confidence,
        should_create_lead=False,
        should_handover=False,
        extracted_contact=contact or ExtractedContact(),
        conversation_summary="Department routing test",
    )


def test_ka_tuition_routes_finance_without_lead(client, session_factory, monkeypatch):
    patch_analysis(monkeypatch, analysis_for(intent="finance_question"))
    session = start_session(client, language="ka")

    result = send_message(client, session, "რა ღირს სწავლა?", language="ka")

    assert result["department_key"] == "finance"
    assert result["route_department"] == "Finance"
    assert result["should_create_lead"] is False
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None
    no_crm_side_effects(session_factory)


def test_en_medicine_tuition_routes_finance_or_medicine_without_lead(client, session_factory, monkeypatch):
    patch_analysis(monkeypatch, analysis_for(intent="finance_question"))
    session = start_session(client, source_domain="join.alte.edu.ge", language="en")

    result = send_message(
        client,
        session,
        "How much is medicine tuition?",
        source_domain="join.alte.edu.ge",
        language="en",
    )

    assert result["department_key"] in {"finance", "medicine"}
    assert result["should_create_lead"] is False
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None
    assert "5500" not in result["reply"]
    no_crm_side_effects(session_factory)


def test_deadline_routes_admissions_without_exact_invention(client, session_factory, monkeypatch):
    patch_analysis(monkeypatch, analysis_for(intent="deadline_question", reply="Deadline requires official confirmation."))
    session = start_session(client, language="ka")

    result = send_message(client, session, "როდის არის მიღების ბოლო ვადა?", language="ka")

    assert result["department_key"] == "admissions"
    assert result["should_create_lead"] is False
    assert "2026-" not in result["reply"]
    no_crm_side_effects(session_factory)


def test_medicine_from_india_no_contact_routes_and_asks_contact(client, session_factory, monkeypatch):
    patch_analysis(
        monkeypatch,
        AIAnalysisResult(
            reply="I can help with medicine admissions.",
            language="en",
            intent="international_admission",
            confidence=0.9,
            should_create_lead=True,
            should_handover=True,
            extracted_contact=ExtractedContact(country="India"),
            program="Medicine / 6-year MD",
            conversation_summary="Medicine applicant from India",
        ),
    )
    session = start_session(client, source_domain="join.alte.edu.ge", language="en")

    result = send_message(
        client,
        session,
        "I want to apply for medicine from India",
        source_domain="join.alte.edu.ge",
        language="en",
    )

    assert result["department_key"] == "medicine"
    assert result["should_create_lead"] is False
    assert "phone_or_email" in result["missing_fields"]
    assert result["created_lead_id"] is None
    no_crm_side_effects(session_factory)


def test_selected_international_documents_routes_international(client, session_factory, monkeypatch):
    patch_analysis(monkeypatch, analysis_for(intent="general_info"))
    session = start_session(client, language="ka")

    result = send_message(
        client,
        session,
        "რა საბუთებია საჭირო?",
        language="ka",
        selected_department="international",
        selected_topic="international_admissions",
    )

    assert result["department_key"] == "international"
    assert result["should_create_lead"] is False
    no_crm_side_effects(session_factory)


def test_selected_finance_ambiguous_message_routes_finance(client, session_factory, monkeypatch):
    patch_analysis(monkeypatch, analysis_for(intent="unknown", confidence=0.4))
    session = start_session(client, language="ka")

    result = send_message(
        client,
        session,
        "მაინტერესებს დეტალები",
        language="ka",
        selected_department="finance",
        selected_topic="tuition",
    )

    assert result["department_key"] == "finance"
    assert result["should_handover"] is True
    no_crm_side_effects(session_factory)


def test_human_request_selected_finance_routes_finance_no_contact(client, session_factory, monkeypatch):
    patch_analysis(monkeypatch, analysis_for(intent="human_request", reply="I can connect you with a human."))
    session = start_session(client, language="en")

    result = send_message(
        client,
        session,
        "I want to talk to an operator about tuition",
        language="en",
        selected_department="finance",
        selected_topic="tuition",
    )

    assert result["department_key"] == "finance"
    assert result["should_handover"] is True
    assert result["created_task_id"] is None
    no_crm_side_effects(session_factory)


def test_admission_interest_with_email_still_creates_lead(client, session_factory, monkeypatch):
    patch_analysis(
        monkeypatch,
        AIAnalysisResult(
            reply="Admissions can follow up.",
            language="en",
            intent="admission_interest",
            confidence=0.9,
            should_create_lead=True,
            should_handover=False,
            extracted_contact=ExtractedContact(first_name="Test", email="student@example.com"),
            interest_area="Admissions",
            conversation_summary="Admission interest with contact",
        ),
    )
    session = start_session(client, language="en")

    result = send_message(client, session, "I want to apply. My email is student@example.com", language="en")

    assert result["created_lead_id"]
    assert len(fetch_all(session_factory, select(Lead))) == 1
