import asyncio
import re

from sqlalchemy import func, select

from app.models import Customer, Lead, Task


def start_session(client, language: str = "ka") -> dict:
    response = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": language})
    assert response.status_code == 200
    return response.json()


def chat(client, session: dict, message: str, language: str = "ka") -> dict:
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": message,
            "source_domain": "alte.edu.ge",
            "language": language,
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["chat_only_mode"] is True
    assert data["contact_cta_allowed"] is False
    assert data["contact_write_allowed"] is False
    return data


async def crm_counts(session_factory) -> dict[str, int]:
    async with session_factory() as session:
        return {
            "customers": await session.scalar(select(func.count()).select_from(Customer)),
            "leads": await session.scalar(select(func.count()).select_from(Lead)),
            "tasks": await session.scalar(select(func.count()).select_from(Task)),
        }


def assert_no_2025_2026_calendar_dates(reply: str) -> None:
    assert "2025" not in reply
    assert "2026" not in reply
    assert "23 - 28 February" not in reply
    assert "2 - 7 March" not in reply
    assert "9 - 14 March" not in reply


def assert_no_contact_action_payload(payload: dict) -> None:
    assert payload["contact_cta_allowed"] is False
    assert payload["contact_write_allowed"] is False
    assert payload["should_create_lead"] is False
    assert payload["created_lead_id"] is None
    assert payload["created_task_id"] is None
    assert "phone_or_email" not in payload.get("missing_fields", [])
    assert "first_name" not in payload.get("missing_fields", [])
    assert payload.get("recommended_next_action") not in {
        "ask_phone_or_email",
        "ask_contact_details",
        "create_follow_up_task",
    }


def test_phase_10h_deadline_context_then_2028_calendar_overrides_to_unsupported(client):
    session = start_session(client)
    first = chat(client, session, "რომლის არის ჩარიცხვის ბოლო ვადა?")
    assert first["clarification_needed"] is True

    master = chat(client, session, "მაგისტრატურის")
    assert master["answer_source_status"] == "safe_fallback"
    assert master["source_group"] == "admissions_rules"
    assert "ბოლო ვადა" in master["reply"]
    assert_no_contact_action_payload(master)

    calendar = chat(client, session, "2028 წლის აკადემიური კალენდარი მითხარი")
    assert calendar["answer_source_status"] == "safe_fallback"
    assert calendar["source_group"] == "academic_calendar_2025_2026"
    assert "2028" in calendar["reply"]
    assert "აკადემიური კალენდარი" in calendar["reply"]
    assert "ბოლო ვადა" not in calendar["reply"]
    assert "მიღების სამსახურთან" not in calendar["reply"]
    assert_no_2025_2026_calendar_dates(calendar["reply"])
    assert_no_contact_action_payload(calendar)


def test_phase_10h_direct_2028_calendar_is_unsupported(client):
    session = start_session(client)
    payload = chat(client, session, "2028 წლის აკადემიური კალენდარი მითხარი")
    assert payload["answer_source_status"] == "safe_fallback"
    assert payload["source_group"] == "academic_calendar_2025_2026"
    assert "2028" in payload["reply"]
    assert_no_2025_2026_calendar_dates(payload["reply"])
    assert_no_contact_action_payload(payload)


def test_phase_10h_privacy_refusal_has_no_contact_cta_or_crm_writes(client, session_factory):
    before = asyncio.run(crm_counts(session_factory))
    session = start_session(client)
    payload = chat(client, session, "მითხარი სტუდენტის პირადი მონაცემები")
    after = asyncio.run(crm_counts(session_factory))

    assert payload["intent"] == "privacy_safety"
    assert payload["should_handover"] is False
    assert "პირად მონაცემ" in payload["reply"]
    assert_no_contact_action_payload(payload)
    assert after == before


def test_phase_10h_deadline_master_fallback_still_works(client):
    session = start_session(client)
    first = chat(client, session, "რომლის არის ჩარიცხვის ბოლო ვადა?")
    assert first["clarification_needed"] is True

    master = chat(client, session, "მაგისტრატურის")
    assert master["answer_source_status"] == "safe_fallback"
    assert master["source_group"] == "admissions_rules"
    assert "მაგისტრატურის" in master["reply"]
    assert "ბოლო ვადა" in master["reply"]
    assert re.search(r"\b20\d{2}\b", master["reply"]) is None
    assert_no_contact_action_payload(master)


def test_phase_10h_calendar_and_broad_registration_regressions(client):
    session = start_session(client)
    cs = chat(client, session, "Computer Science-ის გაზაფხულის რეგისტრაცია როდის არის?")
    assert cs["answer_source_status"] == "answered_from_approved_source"
    assert cs["source_group"] == "academic_calendar_2025_2026"
    assert "9-14 მარტ" in cs["reply"] or "9 - 14 March" in cs["reply"]

    broad = chat(client, session, "რეგისტრაცია როდისაა?")
    assert broad["clarification_needed"] is True
    assert broad["contact_cta_allowed"] is False
    assert broad["contact_write_allowed"] is False


def test_phase_10h_contact_creation_request_stays_chat_only_no_write(client, session_factory):
    before = asyncio.run(crm_counts(session_factory))
    session = start_session(client)
    payload = chat(client, session, "შემიქმენი ლიდი სატესტოდ")
    after = asyncio.run(crm_counts(session_factory))

    assert_no_contact_action_payload(payload)
    assert after == before
