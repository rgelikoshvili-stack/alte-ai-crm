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


def send_message(client, session, message, source_domain="alte.edu.ge", language="ka"):
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": message,
            "source_domain": source_domain,
            "language": language,
        },
    )
    assert response.status_code == 200
    return response.json()


def forced_analysis(
    *,
    intent="finance_question",
    language="en",
    reply="Exact tuition must be confirmed by Finance or Admissions.",
    contact: ExtractedContact | None = None,
    should_create_lead=True,
    should_handover=True,
) -> AIAnalysisResult:
    return AIAnalysisResult(
        reply=reply,
        language=language,
        intent=intent,
        confidence=0.94,
        should_create_lead=should_create_lead,
        should_handover=should_handover,
        department="Finance",
        priority="normal",
        missing_fields=["phone_or_email"] if should_create_lead else [],
        extracted_contact=contact or ExtractedContact(),
        interest_area="Finance",
        source_domain="alte.edu.ge",
        conversation_summary="User asked about tuition or finance without contact.",
    )


def patch_analysis(monkeypatch, analysis: AIAnalysisResult) -> None:
    monkeypatch.setattr(
        chat_service,
        "analyze_with_ai",
        lambda *args, **kwargs: (analysis, {"provider": "test", "model": "forced", "raw_response": None}),
    )


def assert_no_crm_side_effects(session_factory):
    assert fetch_all(session_factory, select(Customer)) == []
    assert fetch_all(session_factory, select(Lead)) == []
    assert fetch_all(session_factory, select(Task)) == []


def test_ka_tuition_without_contact_does_not_create_lead_task_or_customer(client, session_factory, monkeypatch):
    patch_analysis(monkeypatch, forced_analysis(language="ka"))
    session = start_session(client, language="ka")

    result = send_message(client, session, "რა ღირს სწავლა?", language="ka")

    assert result["intent"] == "finance_question"
    assert result["should_create_lead"] is False
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None
    assert "phone_or_email" not in result["missing_fields"]
    assert "finance" in result["reply"].lower() or "admissions" in result["reply"].lower()
    assert_no_crm_side_effects(session_factory)


def test_en_tuition_without_contact_does_not_create_lead_task_or_customer(client, session_factory, monkeypatch):
    patch_analysis(monkeypatch, forced_analysis())
    session = start_session(client, language="en")

    result = send_message(client, session, "How much is tuition?", language="en")

    assert result["should_create_lead"] is False
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None
    assert_no_crm_side_effects(session_factory)


def test_medicine_tuition_without_contact_remains_conservative_and_no_lead(client, session_factory, monkeypatch):
    patch_analysis(
        monkeypatch,
        forced_analysis(reply="Medicine tuition must be confirmed by an official Finance or Admissions source."),
    )
    session = start_session(client, source_domain="join.alte.edu.ge", language="en")

    result = send_message(
        client,
        session,
        "How much is medicine tuition?",
        source_domain="join.alte.edu.ge",
        language="en",
    )

    assert result["should_create_lead"] is False
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None
    assert "5500" not in result["reply"]
    assert_no_crm_side_effects(session_factory)


def test_scholarship_without_contact_does_not_create_lead_task_or_customer(client, session_factory, monkeypatch):
    patch_analysis(monkeypatch, forced_analysis(reply="Scholarship and grant details require official confirmation."))
    session = start_session(client, language="en")

    result = send_message(client, session, "Do you have scholarship or grant details?", language="en")

    assert result["should_create_lead"] is False
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None
    assert_no_crm_side_effects(session_factory)


def test_deadline_without_contact_does_not_create_lead_task_or_customer(client, session_factory, monkeypatch):
    patch_analysis(
        monkeypatch,
        forced_analysis(intent="deadline_question", reply="Admission deadlines require official confirmation."),
    )
    session = start_session(client, language="en")

    result = send_message(client, session, "When is the admission deadline?", language="en")

    assert result["should_create_lead"] is False
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None
    assert_no_crm_side_effects(session_factory)


def test_finance_question_with_contact_preserves_existing_task_policy(client, session_factory, monkeypatch):
    patch_analysis(
        monkeypatch,
        forced_analysis(
            contact=ExtractedContact(first_name="Test", email="finance-test@example.com"),
            should_create_lead=False,
        ),
    )
    session = start_session(client, language="en")

    result = send_message(client, session, "How much is tuition? My email is finance-test@example.com", language="en")

    assert result["intent"] == "finance_question"
    assert result["should_create_lead"] is False
    assert result["created_lead_id"] is None
    assert result["created_task_id"]
    assert fetch_all(session_factory, select(Lead)) == []
    assert len(fetch_all(session_factory, select(Task))) == 1


def test_human_request_without_contact_policy_unchanged(client, session_factory, monkeypatch):
    patch_analysis(
        monkeypatch,
        AIAnalysisResult(
            reply="I can connect you with a human. Please share a phone or email.",
            language="en",
            intent="human_request",
            confidence=0.95,
            should_create_lead=False,
            should_handover=True,
            department="Admissions",
            missing_fields=["phone_or_email"],
            extracted_contact=ExtractedContact(),
            conversation_summary="User requested human handover without contact.",
        ),
    )
    session = start_session(client, language="en")

    result = send_message(client, session, "I want to speak with a human", language="en")

    assert result["intent"] == "human_request"
    assert result["should_handover"] is True
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None
    assert_no_crm_side_effects(session_factory)
