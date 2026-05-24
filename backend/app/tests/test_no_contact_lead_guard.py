import asyncio

from sqlalchemy import select

from app.models import Lead, Task
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
    intent: str,
    source_domain: str = "alte.edu.ge",
    contact: ExtractedContact | None = None,
    program: str | None = None,
    priority: str = "high",
) -> AIAnalysisResult:
    return AIAnalysisResult(
        reply="I can help with admissions.",
        language="en" if source_domain == "join.alte.edu.ge" else "ka",
        intent=intent,
        confidence=0.95,
        should_create_lead=True,
        should_handover=True,
        department="International Admissions" if intent == "international_admission" else "Admissions",
        priority=priority,
        missing_fields=[],
        extracted_contact=contact or ExtractedContact(country="India"),
        interest_area="International admission" if intent == "international_admission" else "Admissions",
        program=program,
        source_domain=source_domain,
        conversation_summary="Medicine admission interest from India",
    )


def patch_analysis(monkeypatch, analysis: AIAnalysisResult) -> None:
    monkeypatch.setattr(
        chat_service,
        "analyze_with_ai",
        lambda *args, **kwargs: (analysis, {"provider": "test", "model": "forced", "raw_response": None}),
    )


def assert_no_leads_or_tasks(session_factory):
    assert fetch_all(session_factory, select(Lead)) == []
    assert fetch_all(session_factory, select(Task)) == []


def test_forced_admission_interest_without_contact_does_not_create_lead_or_task(client, session_factory, monkeypatch):
    patch_analysis(monkeypatch, forced_analysis(intent="admission_interest"))
    session = start_session(client)

    result = send_message(client, session, "I want to apply")

    assert result["intent"] == "admission_interest"
    assert result["should_create_lead"] is False
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None
    assert "phone_or_email" in result["missing_fields"]
    assert_no_leads_or_tasks(session_factory)


def test_forced_international_without_contact_does_not_create_lead_or_task(client, session_factory, monkeypatch):
    patch_analysis(monkeypatch, forced_analysis(intent="international_admission", source_domain="join.alte.edu.ge"))
    session = start_session(client, source_domain="join.alte.edu.ge", language="en")

    result = send_message(client, session, "I want to apply from India", source_domain="join.alte.edu.ge", language="en")

    assert result["intent"] == "international_admission"
    assert result["should_create_lead"] is False
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None
    assert "phone_or_email" in result["missing_fields"]
    assert_no_leads_or_tasks(session_factory)


def test_forced_medicine_without_contact_does_not_create_lead_or_task(client, session_factory, monkeypatch):
    patch_analysis(
        monkeypatch,
        forced_analysis(
            intent="international_admission",
            source_domain="join.alte.edu.ge",
            program="Medicine / 6-year MD",
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

    assert result["should_create_lead"] is False
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None
    assert "phone_or_email" in result["missing_fields"]
    assert_no_leads_or_tasks(session_factory)


def test_forced_join_alte_no_contact_interest_does_not_create_lead_or_task(client, session_factory, monkeypatch):
    patch_analysis(monkeypatch, forced_analysis(intent="admission_interest", source_domain="join.alte.edu.ge"))
    session = start_session(client, source_domain="join.alte.edu.ge", language="en")

    result = send_message(client, session, "What programs can I apply to?", source_domain="join.alte.edu.ge", language="en")

    assert result["should_create_lead"] is False
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None
    assert_no_leads_or_tasks(session_factory)


def test_forced_medicine_with_email_creates_medical_lead_and_task(client, session_factory, monkeypatch):
    patch_analysis(
        monkeypatch,
        forced_analysis(
            intent="international_admission",
            source_domain="join.alte.edu.ge",
            contact=ExtractedContact(first_name="Test", email="student@example.com", country="India"),
            program="Medicine / 6-year MD",
        ),
    )
    session = start_session(client, source_domain="join.alte.edu.ge", language="en")

    result = send_message(
        client,
        session,
        "I want to apply for medicine from India. My email is student@example.com",
        source_domain="join.alte.edu.ge",
        language="en",
    )

    assert result["created_lead_id"]
    assert result["created_task_id"]
    leads = fetch_all(session_factory, select(Lead))
    tasks = fetch_all(session_factory, select(Task))
    assert len(leads) == 1
    assert len(tasks) == 1
    assert leads[0].priority == "high"
    assert leads[0].is_international_priority is True
    assert leads[0].medical_track is True


def test_forced_international_with_phone_creates_high_priority_lead_and_task(client, session_factory, monkeypatch):
    patch_analysis(
        monkeypatch,
        forced_analysis(
            intent="international_admission",
            source_domain="join.alte.edu.ge",
            contact=ExtractedContact(first_name="Test", phone="+995599000000", country="India"),
        ),
    )
    session = start_session(client, source_domain="join.alte.edu.ge", language="en")

    result = send_message(
        client,
        session,
        "I want to apply from India. My phone is +995599000000",
        source_domain="join.alte.edu.ge",
        language="en",
    )

    assert result["created_lead_id"]
    assert result["created_task_id"]
    leads = fetch_all(session_factory, select(Lead))
    tasks = fetch_all(session_factory, select(Task))
    assert len(leads) == 1
    assert len(tasks) == 1
    assert leads[0].priority == "high"
    assert leads[0].is_international_priority is True


def test_human_request_chat_policy_still_requires_contact_for_task(client, session_factory, monkeypatch):
    patch_analysis(
        monkeypatch,
        AIAnalysisResult(
            reply="I will connect you with a human. Please share your phone or email.",
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
    assert_no_leads_or_tasks(session_factory)
