import asyncio

from sqlalchemy import select

from app.models import Lead, Task
from app.schemas.chat import AIAnalysisResult, ExtractedContact
from app.services import chat_service


FORBIDDEN_CONTACT_REQUESTS = [
    "Please confirm your contact details",
    "name, phone, email",
    "Please share your name",
    "phone or email so",
    "provide your phone",
    "provide your email",
    "გთხოვთ მოგვწეროთ სახელი",
    "გთხოვთ მომწეროთ სახელი",
    "ტელეფონი ან ელფოსტა",
]


def fetch_all(session_factory, query):
    async def run():
        async with session_factory() as session:
            return (await session.scalars(query)).all()

    return asyncio.run(run())


def start_session(client, source_domain="join.alte.edu.ge", language="en"):
    response = client.post(
        "/chat/session/start",
        json={
            "source_domain": source_domain,
            "language": language,
            "channel": "website_chat",
            "widget_variant": "pro_v2_safe",
        },
    )
    assert response.status_code == 200
    return response.json()


def send_message(client, session, message, source_domain="join.alte.edu.ge", language="en"):
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": message,
            "source_domain": source_domain,
            "language": language,
            "widget_variant": "pro_v2_safe",
            "selected_department": "international",
            "selected_topic": "documents",
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


def assert_no_crm_side_effects(result, session_factory):
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None
    assert fetch_all(session_factory, select(Lead)) == []
    assert fetch_all(session_factory, select(Task)) == []


def assert_no_forbidden_contact_request(reply: str):
    lowered = reply.lower()
    for phrase in FORBIDDEN_CONTACT_REQUESTS:
        assert phrase.lower() not in lowered


def test_international_answer_rewrites_premature_contact_request(client, session_factory, monkeypatch):
    patch_analysis(
        monkeypatch,
        AIAnalysisResult(
            reply="Please confirm your contact details (name, phone, email) so an admissions consultant can follow up.",
            language="en",
            intent="international_admission",
            confidence=0.94,
            should_create_lead=True,
            should_handover=True,
            department="International Admissions",
            missing_fields=[],
            extracted_contact=ExtractedContact(country="India"),
            interest_area="International admission",
            source_domain="join.alte.edu.ge",
            conversation_summary="International applicant asked about documents.",
        ),
    )
    session = start_session(client)

    result = send_message(client, session, "What documents do international students need?")

    assert 'If you would like an operator to follow up, click "Yes, contact".' in result["reply"]
    assert_no_forbidden_contact_request(result["reply"])
    assert_no_crm_side_effects(result, session_factory)


def test_human_handover_uses_safe_consent_copy(client, session_factory, monkeypatch):
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
            source_domain="join.alte.edu.ge",
            conversation_summary="User requested operator.",
        ),
    )
    session = start_session(client)

    result = send_message(client, session, "I want to talk to an operator")

    assert result["should_handover"] is True
    assert "Contact details should only be shared after your explicit consent." in result["reply"]
    assert_no_forbidden_contact_request(result["reply"])
    assert_no_crm_side_effects(result, session_factory)


def test_georgian_contact_request_uses_safe_consent_copy(client, session_factory, monkeypatch):
    patch_analysis(
        monkeypatch,
        AIAnalysisResult(
            reply="გთხოვთ მოგვწეროთ სახელი და ტელეფონი ან ელფოსტა, რომ კონსულტანტი დაგიკავშირდეთ.",
            language="ka",
            intent="admission_interest",
            confidence=0.92,
            should_create_lead=True,
            should_handover=True,
            department="Admissions",
            missing_fields=["phone_or_email"],
            extracted_contact=ExtractedContact(),
            source_domain="alte.edu.ge",
            conversation_summary="User asked admissions question without contact.",
        ),
    )
    session = start_session(client, source_domain="alte.edu.ge", language="ka")

    result = send_message(client, session, "მინდა მიღებაზე კონსულტაცია", source_domain="alte.edu.ge", language="ka")

    assert "საკონტაქტო ინფორმაციის გაზიარება მხოლოდ თქვენი მკაფიო თანხმობის შემდეგ უნდა მოხდეს." in result["reply"]
    assert_no_forbidden_contact_request(result["reply"])
    assert_no_crm_side_effects(result, session_factory)


def test_georgian_contact_information_instruction_is_rewritten(client, session_factory, monkeypatch):
    patch_analysis(
        monkeypatch,
        AIAnalysisResult(
            reply="გთხოვთ, მიუთითოთ საკონტაქტო ინფორმაცია (სახელი, ტელეფონი ან ელ. ფოსტა), რათა ჩვენი ოპერატორი დაგიკავშირდეთ.",
            language="ka",
            intent="human_request",
            confidence=0.95,
            should_create_lead=False,
            should_handover=True,
            department="Admissions",
            missing_fields=["phone_or_email"],
            extracted_contact=ExtractedContact(),
            source_domain="join.alte.edu.ge",
            conversation_summary="User requested operator.",
        ),
    )
    session = start_session(client, source_domain="join.alte.edu.ge", language="ka")

    result = send_message(
        client,
        session,
        "მინდა ოპერატორთან დაკავშირება",
        source_domain="join.alte.edu.ge",
        language="ka",
    )

    assert "საკონტაქტო ინფორმაციის გაზიარება მხოლოდ თქვენი მკაფიო თანხმობის შემდეგ უნდა მოხდეს." in result["reply"]
    assert "მიუთითოთ საკონტაქტო ინფორმაცია" not in result["reply"]
    assert "სახელი, ტელეფონი" not in result["reply"]
    assert_no_crm_side_effects(result, session_factory)


def test_georgian_partial_contact_request_fragment_is_removed(client, session_factory, monkeypatch):
    patch_analysis(
        monkeypatch,
        AIAnalysisResult(
            reply="გესაუბრებით! გთხოვთ, მომაწოდოთ თქვენი საკონტაქტო ინფორმაცია, რათა ოპერატორი დაგიკავშირდეთ.",
            language="ka",
            intent="human_request",
            confidence=0.95,
            should_create_lead=False,
            should_handover=True,
            department="Admissions",
            missing_fields=["phone_or_email"],
            extracted_contact=ExtractedContact(),
            source_domain="join.alte.edu.ge",
            conversation_summary="User requested operator.",
        ),
    )
    session = start_session(client, source_domain="join.alte.edu.ge", language="ka")

    result = send_message(
        client,
        session,
        "მინდა ოპერატორთან დაკავშირება",
        source_domain="join.alte.edu.ge",
        language="ka",
    )

    assert "გთხოვთ, მომაწოდოთ თქვენი" not in result["reply"]
    assert "საკონტაქტო ინფორმაციის გაზიარება მხოლოდ თქვენი მკაფიო თანხმობის შემდეგ უნდა მოხდეს." in result["reply"]
    assert_no_crm_side_effects(result, session_factory)


def test_normal_academic_answer_is_not_rewritten():
    analysis = AIAnalysisResult(
        reply="Bachelor programs are listed in the official program catalog.",
        language="en",
        intent="general_info",
        confidence=0.9,
        should_create_lead=False,
        should_handover=False,
        department="Programs",
        missing_fields=[],
        extracted_contact=ExtractedContact(),
        conversation_summary="Program catalog answer.",
    )

    chat_service.sanitize_premature_contact_request(analysis)

    assert analysis.reply == "Bachelor programs are listed in the official program catalog."
