from __future__ import annotations

import asyncio
import importlib
import subprocess
from pathlib import Path

from sqlalchemy import select

from app.models import Customer, Lead, Task
from app.schemas.chat import AIAnalysisResult, ExtractedContact
from app.services import chat_service
from app.services.knowledge_routing_service import classify_knowledge_route


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEPARTMENT_MAP = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "department_topic_source_map.json"
SOURCE_GROUPS = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "source_groups.json"
TEST_STRINGS = PROJECT_ROOT / "test_site" / "variants" / "pro-v2-strings.jsx"
TEST_MODALS = PROJECT_ROOT / "test_site" / "variants" / "pro-v2-modals.jsx"
WIDGET_STRINGS = PROJECT_ROOT / "widget" / "variants" / "pro-v2-strings.jsx"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
MOJIBAKE_MARKER = "\u00e1\u0192"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fetch_all(session_factory, query):
    async def run():
        async with session_factory() as session:
            return (await session.scalars(query)).all()

    return asyncio.run(run())


def start_session(client):
    response = client.post(
        "/chat/session/start",
        json={"source_domain": "join.alte.edu.ge", "language": "ka", "widget_variant": "pro_v2_safe"},
    )
    assert response.status_code == 200
    return response.json()


def send(client, session, message: str, *, language: str = "ka"):
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


def patch_analysis(monkeypatch, *, intent: str = "general_info", reply: str = "Official answer"):
    analysis = AIAnalysisResult(
        reply=reply,
        language="ka",
        intent=intent,
        confidence=0.9,
        should_create_lead=False,
        should_handover=False,
        extracted_contact=ExtractedContact(),
        conversation_summary="Phase 9AI routing regression",
    )
    monkeypatch.setattr(
        chat_service,
        "analyze_with_ai",
        lambda *args, **kwargs: (analysis, {"provider": "test", "model": "forced", "raw_response": None}),
    )


def test_phase_9ai_map_files_exist_and_contain_required_groups():
    text = read(DEPARTMENT_MAP) + read(SOURCE_GROUPS)
    assert "admissions" in text
    assert "programs" in text
    assert "finance_sources" in text
    assert "library_sources" in text
    assert "it_support_sources" in text
    assert "official_academic_rules" in text
    assert "academic_calendar_2025_2026" in text
    assert "stale_allowed" in text


def test_phase_9ai_bachelor_ects_routes_to_official_academic_rules():
    decision = classify_knowledge_route("რამდენი ECTS კრედიტია საჭირო საბაკალავრო პროგრამის დასასრულებლად?")
    answer = chat_service.official_academic_rules_regression_reply(
        "რამდენი ECTS კრედიტია საჭირო საბაკალავრო პროგრამის დასასრულებლად?",
        "ka",
    )

    assert decision.clarification_required is False
    assert decision.primary_source_group == "official_academic_rules"
    assert answer and "240" in answer
    assert "180" not in answer


def test_phase_9ai_master_ects_and_status_rules_still_have_deterministic_answers():
    master = chat_service.official_academic_rules_regression_reply("რამდენი კრედიტია სამაგისტრო პროგრამა?", "ka")
    status = chat_service.official_academic_rules_regression_reply("რამდენი წლით შეიძლება სტუდენტის სტატუსის შეჩერება?", "ka")

    assert master and "120" in master
    assert status and "5" in status


def test_phase_9ai_generic_study_question_asks_clarification(client):
    session = start_session(client)
    result = send(client, session, "სწავლა მაინტერესებს")

    assert result["clarification_needed"] is True
    assert "ზუსტად რომ გიპასუხოთ" in result["reply"]
    assert {"მიღება", "პროგრამები", "სწავლის საფასური", "სტუდენტის სტატუსი"}.issubset(set(result["clarification_options"]))
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None


def test_phase_9ai_programs_question_asks_program_level_clarification(client):
    session = start_session(client)
    result = send(client, session, "პროგრამები მაინტერესებს")

    assert result["clarification_needed"] is True
    assert "რომელ პროგრამაზე" in result["reply"]
    assert {"ბაკალავრიატი", "მაგისტრატურა", "მედიცინა / MD", "საერთაშორისო მიღება"}.issubset(
        set(result["clarification_options"])
    )


def test_phase_9ai_finance_broad_question_clarifies_and_never_routes_international(client):
    session = start_session(client)
    result = send(client, session, "გადახდებზე მაინტერესებს")

    assert result["clarification_needed"] is True
    assert "გადახდებზე" in result["reply"]
    assert result["department_key"] == "finance"
    assert result["department_key"] != "international"
    assert "ფინანსურ დეპარტამენტთან დაკავშირება" in result["clarification_options"]


def test_phase_9ai_status_broad_question_clarifies(client):
    session = start_session(client)
    result = send(client, session, "სტატუსზე მაქვს კითხვა")

    assert result["clarification_needed"] is True
    assert "სტუდენტის სტატუსთან" in result["reply"]
    assert {"შეჩერება", "აღდგენა", "შეწყვეტა", "მობილობა"}.issubset(set(result["clarification_options"]))


def test_phase_9ai_help_question_clarifies_without_hallucination(client):
    session = start_session(client)
    result = send(client, session, "დახმარება მინდა")

    assert result["clarification_needed"] is True
    assert result["should_handover"] is False
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None


def test_phase_9ai_library_routes_to_library_no_international(monkeypatch, client, session_factory):
    patch_analysis(monkeypatch, intent="student_service")
    session = start_session(client)
    result = send(client, session, "ბიბლიოთეკის რესურსები როგორ გამოვიყენო?")

    assert result["department_key"] == "library"
    assert result["answer_source_status"] in {"no_approved_source_found", "answered_from_approved_source"}
    if result["answer_source_status"] == "no_approved_source_found":
        assert "დამტკიცებულ წყაროში" in result["reply"]
    else:
        assert "ბიბლიოთეკ" in result["reply"]
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None
    assert fetch_all(session_factory, select(Customer)) == []
    assert fetch_all(session_factory, select(Lead)) == []
    assert fetch_all(session_factory, select(Task)) == []


def test_phase_9ai_it_support_routes_to_it_support():
    decision = classify_knowledge_route("emis.alte.edu.ge-ში ვერ შევდივარ")
    assert decision.department_id == "it_support"


def test_phase_9ai_finance_handover_routes_to_finance_not_international():
    decision = classify_knowledge_route("მინდა ფინანსურ დეპარტამენტთან დაკავშირება")
    assert decision.department_id == "finance"
    assert decision.department_id != "international_admissions"


def test_phase_9ai_international_medicine_requires_explicit_international_context():
    international = classify_knowledge_route("I am an international student and want to apply to Medicine")
    local_medicine = classify_knowledge_route("მედიცინაზე ჩაბარება მინდა", source_domain="join.alte.edu.ge")

    assert international.department_id in {"international_admissions", "medicine_md"}
    assert local_medicine.department_id != "international_admissions"


def test_phase_9ai_unsupported_2031_scholarship_no_hallucination(monkeypatch, client, session_factory):
    patch_analysis(monkeypatch, intent="finance_question")
    session = start_session(client)
    result = send(client, session, "2031 წლის კოსმოსური კამპუსის სტიპენდია როგორ მივიღო?")

    assert result["answer_source_status"] == "no_approved_source_found"
    assert "კოსმოსური" not in result["reply"]
    assert result["created_lead_id"] is None
    assert result["created_task_id"] is None
    assert fetch_all(session_factory, select(Customer)) == []
    assert fetch_all(session_factory, select(Lead)) == []
    assert fetch_all(session_factory, select(Task)) == []


def test_phase_9ai_contact_and_wait_operator_ui_still_present():
    text = read(TEST_STRINGS) + read(TEST_MODALS) + read(WIDGET_STRINGS)
    assert "თქვენი კითხვა / შეტყობინება" in text
    assert "Your question / message" in text
    assert "დაელოდე ოპერატორს" in text
    assert "Wait for operator" in text


def test_phase_9ai_safety_public_launch_no_go_no_mojibake_and_no_secret_frontend():
    text = "\n".join(
        read(path)
        for path in [
            DEPARTMENT_MAP,
            SOURCE_GROUPS,
            TEST_STRINGS,
            TEST_MODALS,
            PUBLIC_LAUNCH,
        ]
    )
    assert MOJIBAKE_MARKER not in text
    assert "api.anthropic.com" not in text
    assert "ANTHROPIC_API_KEY" not in text
    assert "sk-ant" not in text
    assert "public_launch_decision=go" not in read(PUBLIC_LAUNCH).lower()
    assert "no-go" in read(PUBLIC_LAUNCH).lower()


def test_phase_9ai_verifier_and_production_script_importability():
    verifier = importlib.import_module("app.scripts.verify_phase_9ai_knowledge_routing_clarification_operator")
    smoke = importlib.import_module("app.scripts.production_phase_9ai_clarification_routing_qa")
    assert hasattr(verifier, "run_checks")
    assert hasattr(smoke, "main")


def test_phase_9ai_env_and_local_secrets_not_tracked():
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    tracked = result.stdout.splitlines()
    assert not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]
