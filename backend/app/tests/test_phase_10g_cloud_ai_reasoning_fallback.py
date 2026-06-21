import re


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
    return response.json()


def assert_no_invented_deadline(reply: str) -> None:
    assert not re.search(r"\b20\d{2}\b", reply)
    assert "23 - 28 February" not in reply
    assert "2 - 7 March" not in reply
    assert "9 - 14 March" not in reply


def assert_not_documents_only(reply: str) -> None:
    lowered = reply.lower()
    assert "id copy" not in lowered
    assert "diploma" not in lowered
    assert "პირადობის" not in reply
    assert "დიპლომ" not in reply
    assert "საბუთ" not in reply


def test_phase_10g_master_deadline_clarification_sequence_preserves_intent(client):
    session = start_session(client, language="ka")
    first = chat(client, session, "რომლის არის ჩარიცხვის ბოლო ვადა?")
    assert first["clarification_needed"] is True
    assert "ბოლო ვადა" in first["reply"]

    followup = chat(client, session, "მაგისტრატურის")
    assert followup["clarification_needed"] is False
    assert followup["answer_source_status"] == "safe_fallback"
    assert followup["source_group"] == "admissions_rules"
    assert "მაგისტრატურის" in followup["reply"]
    assert "ბოლო ვადა" in followup["reply"]
    assert "მიღების სამსახურთან" in followup["reply"]
    assert "საერთაშორისო აპლიკანტი" in followup["reply"]
    assert_not_documents_only(followup["reply"])
    assert_no_invented_deadline(followup["reply"])
    assert followup["should_create_lead"] is False
    assert followup["created_lead_id"] is None
    assert followup["created_task_id"] is None


def test_phase_10g_bachelor_deadline_clarification_sequence_preserves_intent(client):
    session = start_session(client, language="ka")
    first = chat(client, session, "ჩარიცხვის ბოლო ვადა როდისაა?")
    assert first["clarification_needed"] is True

    followup = chat(client, session, "ბაკალავრიატის მიღება")
    assert followup["answer_source_status"] == "safe_fallback"
    assert "ბაკალავრიატის" in followup["reply"]
    assert "ბოლო ვადა" in followup["reply"]
    assert_not_documents_only(followup["reply"])
    assert_no_invented_deadline(followup["reply"])


def test_phase_10g_english_deadline_clarification_sequence_preserves_intent(client):
    session = start_session(client, language="en")
    first = chat(client, session, "What is the application deadline?", language="en")
    assert first["clarification_needed"] is True
    assert "deadline" in first["reply"].lower()

    followup = chat(client, session, "Master's admission", language="en")
    assert followup["answer_source_status"] == "safe_fallback"
    assert "master" in followup["reply"].lower()
    assert "deadline" in followup["reply"].lower()
    assert "official admissions page" in followup["reply"].lower()
    assert_not_documents_only(followup["reply"])
    assert_no_invented_deadline(followup["reply"])


def test_phase_10g_medical_tuition_stays_finance_safe(client):
    session = start_session(client, language="ka")
    payload = chat(client, session, "რა ღირს სამედიცინო სწავლა?")
    assert payload["answer_source_status"] == "clarification_needed"
    assert payload["clarification_needed"] is True
    assert "საფასურ" in payload["reply"]
    assert "360 ECTS" not in payload["reply"]
    assert not re.search(r"\d+\s*(GEL|lari|ლარი)|₾\s*\d+", payload["reply"], flags=re.IGNORECASE)
    assert payload["should_create_lead"] is False


def test_phase_10g_clear_medicine_program_info_still_answers_program(client):
    session = start_session(client, language="ka")
    payload = chat(client, session, "მითხარი მედიცინის პროგრამაზე")
    assert payload["answer_source_status"] == "answered_from_approved_source"
    assert "მედიცინა" in payload["reply"] or "Medicine" in payload["reply"]
    assert "360 ECTS" in payload["reply"]
    assert payload["should_create_lead"] is False


def test_phase_10g_knowledge_ask_remains_deterministic_no_claude(client):
    response = client.post("/api/knowledge/ask", json={"question": "რა ღირს სამედიცინო სწავლა?"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["used_claude"] is False
    assert payload["status"] == "clarification_needed"
    assert payload["source_group"] == "finance_sources"
