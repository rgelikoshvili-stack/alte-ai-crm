from sqlalchemy import select

from app.models import Customer, Lead, Task
from app.schemas.chat import AIAnalysisResult, ExtractedContact
from app.services import chat_service
from app.services.department_routing_service import is_ambiguous_message, resolve_department


def route(message, selected_department=None, *, selected_topic=None, intent="general_info", confidence=0.4, source_domain="alte.edu.ge", language="ka"):
    return resolve_department(
        message_text=message,
        ai_intent=intent,
        ai_confidence=confidence,
        source_domain=source_domain,
        selected_department=selected_department,
        selected_topic=selected_topic,
        risk_flags=[],
        used_sources=[],
        language=language,
        ai_department="Admissions",
    )


def test_selected_finance_wins_for_ambiguous_ka_details():
    result = route("მაინტერესებს დეტალები", "finance", selected_topic="tuition")

    assert is_ambiguous_message("მაინტერესებს დეტალები", "ka") is True
    assert result.department_key == "finance"
    assert result.reason == "sidebar_context_for_ambiguous_message"


def test_selected_medicine_wins_for_ambiguous_ka_details():
    result = route("დეტალები მაინტერესებს", "medicine", selected_topic="medicine")

    assert result.department_key == "medicine"
    assert result.reason == "sidebar_context_for_ambiguous_message"


def test_selected_international_wins_for_ambiguous_en_details():
    result = route("details please", "international", selected_topic="international", language="en")

    assert result.department_key == "international"
    assert result.reason == "sidebar_context_for_ambiguous_message"


def test_selected_it_support_wins_for_ambiguous_help():
    result = route("help please", "it_support", selected_topic="it_support", language="en")

    assert result.department_key == "it_support"
    assert result.reason == "sidebar_context_for_ambiguous_message"


def test_selected_student_services_wins_for_ambiguous_more_info():
    result = route("მეტი ინფორმაცია მინდა", "student_services", selected_topic="student_services")

    assert result.department_key == "student_services"
    assert result.reason == "sidebar_context_for_ambiguous_message"


def test_strong_it_keyword_overrides_selected_finance():
    result = route("პორტალში ვერ შევდივარ", "finance", selected_topic="tuition")

    assert result.department_key == "it_support"
    assert result.reason == "strong_message_keyword"


def test_strong_finance_keyword_overrides_selected_medicine():
    result = route("სტიპენდია მაინტერესებს", "medicine", selected_topic="medicine")

    assert result.department_key == "finance"
    assert result.reason == "strong_message_keyword"


def test_human_request_uses_selected_finance():
    result = route("მინდა ოპერატორთან საუბარი", "finance", selected_topic="human_operator", intent="human_request")

    assert result.department_key == "finance"
    assert result.reason == "human_request_selected_or_inferred_department"


def test_unknown_without_selected_department_falls_back_to_admissions():
    result = route("unclear question", None, language="en")

    assert result.department_key == "admissions"


def fetch_all(session_factory, query):
    import asyncio

    async def run():
        async with session_factory() as session:
            return (await session.scalars(query)).all()

    return asyncio.run(run())


def patch_analysis(monkeypatch, analysis: AIAnalysisResult) -> None:
    monkeypatch.setattr(
        chat_service,
        "analyze_with_ai",
        lambda *args, **kwargs: (analysis, {"provider": "test", "model": "forced", "raw_response": None}),
    )


def test_sidebar_ambiguous_chat_has_no_crm_side_effects(client, session_factory, monkeypatch):
    patch_analysis(
        monkeypatch,
        AIAnalysisResult(
            reply="I need more detail.",
            language="ka",
            intent="general_info",
            confidence=0.4,
            should_create_lead=True,
            should_handover=True,
            department="Admissions",
            extracted_contact=ExtractedContact(),
            conversation_summary="Ambiguous sidebar context",
        ),
    )
    session_response = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "ka"})
    assert session_response.status_code == 200
    session = session_response.json()

    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": "მაინტერესებს დეტალები",
            "source_domain": "alte.edu.ge",
            "language": "ka",
            "selected_department": "finance",
            "selected_topic": "tuition",
            "widget_variant": "safe_pro_sidebar",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["department_key"] == "finance"
    assert payload["should_create_lead"] is False
    assert payload["created_lead_id"] is None
    assert payload["created_task_id"] is None
    assert fetch_all(session_factory, select(Customer)) == []
    assert fetch_all(session_factory, select(Lead)) == []
    assert fetch_all(session_factory, select(Task)) == []
