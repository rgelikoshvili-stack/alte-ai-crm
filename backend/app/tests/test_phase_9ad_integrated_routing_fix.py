import asyncio

from sqlalchemy import select

from app.models import Customer, Lead, Task
from app.schemas.chat import AIAnalysisResult, ExtractedContact
from app.services import chat_service
from app.services.department_routing_service import resolve_department


def _resolve(message: str, *, intent: str = "general_info", source_domain: str = "join.alte.edu.ge"):
    return resolve_department(
        message_text=message,
        ai_intent=intent,
        ai_confidence=0.9,
        source_domain=source_domain,
        selected_department=None,
        selected_topic=None,
        risk_flags=[],
        used_sources=[],
        language="ka",
    )


def _fetch_all(session_factory, query):
    async def run():
        async with session_factory() as session:
            return (await session.scalars(query)).all()

    return asyncio.run(run())


def _assert_no_crm_side_effects(session_factory):
    assert _fetch_all(session_factory, select(Customer)) == []
    assert _fetch_all(session_factory, select(Lead)) == []
    assert _fetch_all(session_factory, select(Task)) == []


def _start_session(client):
    response = client.post(
        "/chat/session/start",
        json={"source_domain": "join.alte.edu.ge", "language": "ka", "widget_variant": "pro_v2_safe"},
    )
    assert response.status_code == 200
    return response.json()


def _send(client, session, message: str, *, language: str = "ka"):
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": message,
            "source_domain": "join.alte.edu.ge",
            "language": language,
            "widget_variant": "pro_v2_safe",
        },
    )
    assert response.status_code == 200
    return response.json()


def _patch_analysis(monkeypatch, *, intent: str, reply: str = "Official confirmation is required."):
    analysis = AIAnalysisResult(
        reply=reply,
        language="ka",
        intent=intent,
        confidence=0.9,
        should_create_lead=False,
        should_handover=intent == "human_request",
        extracted_contact=ExtractedContact(),
        conversation_summary="Phase 9AD routing regression",
    )
    monkeypatch.setattr(
        chat_service,
        "analyze_with_ai",
        lambda *args, **kwargs: (analysis, {"provider": "test", "model": "forced", "raw_response": None}),
    )


def test_phase_9ad_admissions_question_routes_to_admissions_not_programs():
    result = _resolve("როგორ ჩავირიცხო ბაკალავრიატზე?")

    assert result.department_key == "admissions"
    assert result.department_key != "programs"


def test_phase_9ad_library_question_routes_to_library_not_international():
    result = _resolve("ბიბლიოთეკის რესურსები როგორ გამოვიყენო?")

    assert result.department_key == "library"
    assert result.department == "Library"
    assert result.department_key != "international"


def test_phase_9ad_finance_handover_routes_to_finance_not_international():
    result = _resolve("მინდა ფინანსურ დეპარტამენტთან დაკავშირება სწავლის საფასურზე", intent="human_request")

    assert result.department_key == "finance"
    assert result.department == "Finance"
    assert result.department_key != "international"
    assert result.handover_required is True


def test_phase_9ad_international_medicine_control_still_routes_correctly():
    result = resolve_department(
        message_text="I am an international student and want to apply to Medicine.",
        ai_intent="international_admission",
        ai_confidence=0.9,
        source_domain="join.alte.edu.ge",
        selected_department=None,
        selected_topic=None,
        risk_flags=[],
        used_sources=[],
        language="en",
    )

    assert result.department_key in {"medicine", "international"}
    assert result.department_key != "finance"


def test_phase_9ad_broad_program_question_routes_to_supported_department():
    result = _resolve("რა პროგრამები გაქვთ და რომელზე შემიძლია ჩაბარება?")

    assert result.department_key in {"programs", "admissions"}
    assert result.department_key != "international"


def test_phase_9ad_unsupported_2031_scholarship_returns_no_source_without_crm(client, session_factory, monkeypatch):
    _patch_analysis(monkeypatch, intent="finance_question")
    session = _start_session(client)

    result = _send(client, session, "2031 წლის კოსმოსური კამპუსის სტიპენდია როგორ მივიღო?")

    assert result["answer_source_status"] == "no_approved_source_found"
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None
    assert result["should_create_lead"] is False
    _assert_no_crm_side_effects(session_factory)


def test_phase_9ad_handover_copy_does_not_request_contact_details(client, session_factory, monkeypatch):
    _patch_analysis(monkeypatch, intent="human_request", reply="ოპერატორთან დაკავშირება შესაძლებელია თანხმობის შემდეგ.")
    session = _start_session(client)

    result = _send(client, session, "მინდა ფინანსურ დეპარტამენტთან დაკავშირება სწავლის საფასურზე")
    reply = result["reply"].lower()

    forbidden = [
        "type your phone",
        "enter your email",
        "send your full name",
        "provide your whatsapp",
        "მომწერეთ ტელეფონი",
        "შეიყვანეთ ელფოსტა",
    ]
    assert not any(pattern in reply for pattern in forbidden)
    assert result["department_key"] == "finance"
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None
    _assert_no_crm_side_effects(session_factory)
