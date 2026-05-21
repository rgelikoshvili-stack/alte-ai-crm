import asyncio

from sqlalchemy import select

from app.models import Customer, Lead


def fetch_all(session_factory, query):
    async def run():
        async with session_factory() as session:
            return (await session.scalars(query)).all()

    return asyncio.run(run())


def start_session(client):
    response = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "ka"})
    assert response.status_code == 200
    return response.json()


def send_message(client, conversation_id, message, source_domain="alte.edu.ge"):
    response = client.post(
        "/chat/message",
        json={"conversation_id": conversation_id, "message": message, "source_domain": source_domain},
    )
    assert response.status_code == 200
    return response.json()


def test_georgian_message_extracts_name_phone_email_and_program(client, session_factory):
    session = start_session(client)
    result = send_message(
        client,
        session["conversation_id"],
        "გიორგი მაისურაძე, +995599111222, gio@example.com მაინტერესებს ბიზნესის პროგრამა",
    )

    assert result["created_lead_id"]
    assert result["lead_score"] >= 60
    customers = fetch_all(session_factory, select(Customer))
    leads = fetch_all(session_factory, select(Lead))
    assert customers[0].first_name == "გიორგი"
    assert customers[0].phone == "+995599111222"
    assert leads[0].program == "Business"
    assert leads[0].qualification_status in {"qualified", "hot"}


def test_english_message_extracts_qualification_intent_and_program(client, session_factory):
    session = start_session(client)
    result = send_message(
        client,
        session["conversation_id"],
        "John Smith, 599111333, john@example.com I want computer science admission requirements",
    )

    assert result["created_lead_id"]
    leads = fetch_all(session_factory, select(Lead))
    assert leads[0].program == "IT / Computer Science"
    assert leads[0].qualification_intent == "admission_requirements"


def test_high_urgency_creates_hot_lead(client, session_factory):
    session = start_session(client)
    result = send_message(
        client,
        session["conversation_id"],
        "Nino Beridze, +995599123456, nino.hot@example.com I want to apply now for MBA",
    )

    assert result["qualification_status"] == "hot"
    assert result["handover_reason"] == "high_intent_lead"
    leads = fetch_all(session_factory, select(Lead))
    assert leads[0].lead_score >= 80
    assert leads[0].handover_required is True


def test_human_request_triggers_handover_reason(client):
    session = start_session(client)
    result = send_message(client, session["conversation_id"], "ადამიანს დამალაპარაკეთ")

    assert result["should_handover"] is True
    assert result["qualification_status"] == "needs_human"
    assert result["handover_reason"] == "human_requested"


def test_low_info_message_stays_new_or_researching(client):
    session = start_session(client)
    result = send_message(client, session["conversation_id"], "გამარჯობა")

    assert result["lead_score"] <= 25
    assert result["qualification_status"] in {"new", "researching"}
    assert result["created_lead_id"] is None


def test_repeated_message_updates_same_conversation_lead(client, session_factory):
    session = start_session(client)
    first = send_message(
        client,
        session["conversation_id"],
        "Ana Smith, 599222333, ana@example.com I want bachelor program information",
    )
    second = send_message(
        client,
        session["conversation_id"],
        "I want to apply now for bachelor",
    )

    assert first["created_lead_id"]
    assert second["created_lead_id"] == first["created_lead_id"]
    leads = fetch_all(session_factory, select(Lead))
    assert len(leads) == 1
    assert leads[0].qualification_status == "hot"


def test_no_real_api_key_required_for_mock_qualification(client):
    session = start_session(client)
    result = send_message(client, session["conversation_id"], "რა ღირს სწავლა?")

    assert result["intent"] == "finance_question"
    assert result["created_lead_id"] is None
