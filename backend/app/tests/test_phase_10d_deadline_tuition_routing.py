from __future__ import annotations

import re

from app.services.claude_intent_router_service import fallback_intent_route


def start_session(client, language: str = "ka") -> dict:
    response = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": language})
    assert response.status_code == 200
    return response.json()


def ask(client, message: str, language: str = "ka") -> dict:
    session = start_session(client, language=language)
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "message": message,
            "source_domain": "alte.edu.ge",
            "language": language,
        },
    )
    assert response.status_code == 200
    return response.json()


def assert_clarification_route(question: str, *, department: str, question_fragment: str) -> None:
    route = fallback_intent_route(question)
    assert route.needs_clarification is True
    assert route.source_groups_to_search == []
    assert route.department == department
    assert question_fragment in (route.clarification_question or "")


def assert_no_invented_dates_or_amounts(text: str) -> None:
    assert not re.search(r"\b20\d{2}\b", text)
    assert not re.search(r"\b\d+(\.\d+)?\s*(gel|lari|₾)\b", text, flags=re.IGNORECASE)
    assert not re.search(r"₾\s*\d+", text)


def test_phase_10d_admissions_deadline_prompts_ask_clarification_not_documents():
    ka_question = "გთხოვთ დამიზუსტოთ, რომელი ჩარიცხვის ბოლო ვადა გაინტერესებთ?"
    for question in [
        "რომლის არის ჩარიცხვის ბოლო ვადა?",
        "ჩარიცხვის ბოლო ვადა როდისაა?",
        "როდის მთავრდება მიღება?",
    ]:
        assert_clarification_route(question, department="admissions", question_fragment=ka_question)
        route = fallback_intent_route(question)
        assert "ბაკალავრიატის მიღება" in route.clarification_options
        assert "აკადემიური/ადმინისტრაციული რეგისტრაცია" in route.clarification_options

    for question in ["When is the admission deadline?", "What is the application deadline?"]:
        assert_clarification_route(question, department="admissions", question_fragment="Please clarify which admission deadline")


def test_phase_10d_admissions_deadline_chat_has_no_generic_docs_or_dates(client):
    payload = ask(client, "რომლის არის ჩარიცხვის ბოლო ვადა?")

    assert payload["answer_source_status"] == "clarification_needed"
    assert payload["clarification_needed"] is True
    assert "გთხოვთ დამიზუსტოთ, რომელი ჩარიცხვის ბოლო ვადა გაინტერესებთ?" in payload["reply"]
    assert "ბაკალავრიატის მიღება" in payload["reply"]
    assert "აკადემიური/ადმინისტრაციული რეგისტრაცია" in payload["reply"]
    assert "პირადობის" not in payload["reply"]
    assert "დიპლომის ასლი" not in payload["reply"]
    assert_no_invented_dates_or_amounts(payload["reply"])
    assert payload["public_source_label"] is None
    assert payload["should_create_lead"] is False
    assert payload["created_lead_id"] is None
    assert payload["created_task_id"] is None


def test_phase_10d_medical_tuition_prompts_ask_finance_clarification():
    ka_question = "გთხოვთ დამიზუსტოთ, რომელი ინფორმაცია გჭირდებათ სამედიცინო პროგრამის საფასურზე?"
    for question in [
        "რა ღირს სამედიცინო სწავლა?",
        "მედიცინის სწავლა რა ღირს?",
        "მედიცინის პროგრამის საფასური რამდენია?",
    ]:
        assert_clarification_route(question, department="finance", question_fragment=ka_question)
        route = fallback_intent_route(question)
        assert "მედიცინის პროგრამის საფასური" in route.clarification_options
        assert "დაფინანსება/გრანტები" in route.clarification_options

    for question in ["What is the Medicine tuition fee?", "How much does the MD program cost?"]:
        assert_clarification_route(question, department="finance", question_fragment="Please clarify which Medicine program fee")


def test_phase_10d_medical_tuition_chat_is_not_program_description(client):
    payload = ask(client, "რა ღირს სამედიცინო სწავლა?")

    assert payload["answer_source_status"] == "clarification_needed"
    assert payload["clarification_needed"] is True
    assert "სამედიცინო პროგრამის საფასურზე" in payload["reply"]
    assert "ზუსტი/current საფასური" in payload["reply"]
    assert "მედიცინის პროგრამის საფასური" in payload["reply"]
    assert "გადახდის პირობები" in payload["reply"]
    assert "360 ECTS" not in payload["reply"]
    assert "ერთსაფეხურიანი პროგრამა" not in payload["reply"]
    assert_no_invented_dates_or_amounts(payload["reply"])
    assert payload["public_source_label"] is None
    assert payload["should_create_lead"] is False
    assert payload["created_lead_id"] is None
    assert payload["created_task_id"] is None


def test_phase_10d_regressions_program_admissions_calendar_and_source_label(client):
    medicine = fallback_intent_route("მითხარი მედიცინის პროგრამაზე")
    assert medicine.needs_clarification is False
    assert medicine.source_groups_to_search[:1] == ["official_academic_rules"]

    docs = fallback_intent_route("რა საბუთებია საჭირო ბაკალავრიატზე ჩასაბარებლად?")
    assert docs.needs_clarification is False
    assert docs.source_groups_to_search[:1] == ["admissions_rules"]

    calendar = fallback_intent_route("ბაკალავრიატის გაზაფხულის რეგისტრაცია როდის არის?")
    assert calendar.needs_clarification is False
    assert calendar.source_groups_to_search[:1] == ["academic_calendar_2025_2026"]

    academic_deadline = fallback_intent_route("აკადემიური რეგისტრაციის ბოლო ვადა როდის არის?")
    assert academic_deadline.needs_clarification is False
    assert academic_deadline.source_groups_to_search[:1] == ["academic_calendar_2025_2026"]

    payload = ask(client, "What is the application deadline?", language="en")
    assert payload["answer_source_status"] == "clarification_needed"
    assert payload["public_source_label"] is None
