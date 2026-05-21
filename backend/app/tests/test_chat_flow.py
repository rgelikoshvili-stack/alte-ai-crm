import asyncio

from sqlalchemy import select

from app.models import Lead, Message, Task


def fetch_all(session_factory, query):
    async def run():
        async with session_factory() as session:
            return (await session.scalars(query)).all()

    return asyncio.run(run())


def start_session(client, source_domain="alte.edu.ge"):
    response = client.post("/chat/session/start", json={"source_domain": source_domain, "language": "ka"})
    assert response.status_code == 200
    return response.json()


def send_message(client, conversation_id, message, source_domain="alte.edu.ge"):
    response = client.post(
        "/chat/message",
        json={"conversation_id": conversation_id, "message": message, "source_domain": source_domain},
    )
    assert response.status_code == 200
    return response.json()


def test_chat_session_start_creates_conversation(client):
    session = start_session(client)

    assert session["conversation_id"]
    assert session["session_id"]
    assert session["source_domain"] == "alte.edu.ge"


def test_general_contact_question_returns_reply_without_lead(client, session_factory):
    session = start_session(client)
    result = send_message(client, session["conversation_id"], "სად მდებარეობს უნივერსიტეტი?")

    assert result["intent"] == "general_info"
    assert result["created_lead_id"] is None
    leads = fetch_all(session_factory, select(Lead))
    assert leads == []


def test_admission_interest_without_contact_asks_for_missing_fields(client, session_factory):
    session = start_session(client)
    result = send_message(client, session["conversation_id"], "მაინტერესებს ბიზნესის პროგრამაზე ჩარიცხვა")

    assert result["intent"] == "admission_interest"
    assert result["created_lead_id"] is None
    assert "phone_or_email" in result["missing_fields"]
    leads = fetch_all(session_factory, select(Lead))
    assert leads == []


def test_admission_interest_with_contact_creates_customer_lead_and_task(client, session_factory):
    session = start_session(client)
    result = send_message(
        client,
        session["conversation_id"],
        "ნინო ბერიძე, +995599000000, nino@example.com მაინტერესებს ბიზნესის პროგრამა",
    )

    assert result["intent"] == "admission_interest"
    assert result["created_lead_id"]
    assert result["created_task_id"]
    tasks = fetch_all(session_factory, select(Task))
    assert len(tasks) == 1


def test_join_alte_international_medicine_flow(client, session_factory):
    session = start_session(client, source_domain="join.alte.edu.ge")
    result = send_message(
        client,
        session["conversation_id"],
        "I want to apply for medicine from India, my email is test@example.com",
        source_domain="join.alte.edu.ge",
    )

    assert result["intent"] == "international_admission"
    assert result["created_lead_id"]
    leads = fetch_all(session_factory, select(Lead))
    assert len(leads) == 1
    assert leads[0].priority == "high"
    assert leads[0].is_international_priority is True
    assert leads[0].medical_track is True


def test_human_request_asks_for_contact_and_sets_handover(client):
    session = start_session(client)
    result = send_message(client, session["conversation_id"], "ადამიანს დამალაპარაკეთ")

    assert result["intent"] == "human_request"
    assert result["should_handover"] is True
    assert "phone_or_email" in result["missing_fields"]


def test_finance_question_uses_consultant_reply_without_invented_price(client):
    session = start_session(client)
    result = send_message(client, session["conversation_id"], "რა ღირს სწავლა?")

    assert result["intent"] == "finance_question"
    assert result["created_lead_id"] is None
    assert "დაგიდასტურებთ" in result["reply"]


def test_student_service_does_not_create_admissions_lead(client, session_factory):
    session = start_session(client)
    result = send_message(client, session["conversation_id"], "ბიბლიოთეკის ბაზებზე როგორ შევიდე?")

    assert result["intent"] == "student_service"
    assert result["created_lead_id"] is None
    leads = fetch_all(session_factory, select(Lead))
    assert leads == []


def test_chat_message_saves_user_and_ai_messages(client, session_factory):
    session = start_session(client)
    send_message(client, session["conversation_id"], "სად ხართ?")

    messages = fetch_all(session_factory, select(Message).order_by(Message.created_at.asc()))
    assert [message.sender_type for message in messages] == ["user", "ai"]
