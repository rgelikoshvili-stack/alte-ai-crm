from __future__ import annotations

import importlib
from pathlib import Path

from app.services.knowledge_routing_service import classify_knowledge_route


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AI_CHATGPT_STYLE_KB_CLARIFICATION_OPERATOR_RESULT.md"
QA_REPORT = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AI_CHATGPT_STYLE_ROUTING_QA_RESULT.md"
DEPARTMENT_MAP = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "department_topic_source_map.json"
SOURCE_GROUPS = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "source_groups.json"
TEST_STRINGS = PROJECT_ROOT / "test_site" / "variants" / "pro-v2-strings.jsx"
TEST_MODALS = PROJECT_ROOT / "test_site" / "variants" / "pro-v2-modals.jsx"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
MOJIBAKE_MARKER = "\u00e1\u0192"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_9ai_chatgpt_style_artifacts_exist():
    assert RESULT_DOC.exists()
    assert QA_REPORT.exists()
    assert DEPARTMENT_MAP.exists()
    assert SOURCE_GROUPS.exists()


def test_phase_9ai_chatgpt_style_modules_importable():
    verifier = importlib.import_module("app.scripts.verify_phase_9ai_chatgpt_style_kb_clarification_operator")
    smoke = importlib.import_module("app.scripts.production_phase_9ai_chatgpt_style_routing_qa")
    assert hasattr(verifier, "run_checks")
    assert hasattr(smoke, "main")


def test_phase_9ai_chatgpt_style_clear_questions_are_not_clarified():
    bachelor = classify_knowledge_route("რამდენი ECTS კრედიტია საჭირო საბაკალავრო პროგრამის დასასრულებლად?")
    master = classify_knowledge_route("რამდენი კრედიტია სამაგისტრო პროგრამა?")
    status = classify_knowledge_route("რამდენი წლით შეიძლება სტუდენტის სტატუსის შეჩერება?")

    assert bachelor.clarification_required is False
    assert bachelor.primary_source_group == "official_academic_rules"
    assert master.clarification_required is False
    assert master.primary_source_group == "official_academic_rules"
    assert status.clarification_required is False
    assert status.primary_source_group in {"official_academic_rules", "student_status_and_mobility"}


def test_phase_9ai_chatgpt_style_broad_questions_ask_clarification():
    generic = classify_knowledge_route("სწავლა მაინტერესებს")
    programs = classify_knowledge_route("პროგრამები მაინტერესებს")
    finance = classify_knowledge_route("გადახდებზე მაინტერესებს")
    status = classify_knowledge_route("სტატუსზე მაქვს კითხვა")

    assert generic.clarification_required is True
    assert {"მიღება", "პროგრამები", "სწავლის საფასური", "სტუდენტის სტატუსი"}.issubset(set(generic.clarification_options))
    assert programs.clarification_required is True
    assert {"ბაკალავრიატი", "მაგისტრატურა", "მედიცინა / MD", "საერთაშორისო მიღება"}.issubset(set(programs.clarification_options))
    assert finance.clarification_required is True
    assert finance.department_id == "finance"
    assert status.clarification_required is True
    assert {"შეჩერება", "აღდგენა", "შეწყვეტა", "მობილობა"}.issubset(set(status.clarification_options))


def test_phase_9ai_chatgpt_style_routing_guards():
    admissions = classify_knowledge_route("როგორ ჩავირიცხო ბაკალავრიატზე?")
    library = classify_knowledge_route("ბიბლიოთეკის რესურსები როგორ გამოვიყენო?")
    finance = classify_knowledge_route("მინდა ფინანსურ დეპარტამენტთან დაკავშირება")
    international = classify_knowledge_route("I am an international student and want to apply to Medicine")
    local_join = classify_knowledge_route("მედიცინაზე ჩაბარება მინდა", source_domain="join.alte.edu.ge")

    assert admissions.department_id == "admissions"
    assert library.department_id == "library"
    assert finance.department_id == "finance"
    assert international.department_id in {"international_admissions", "medicine_md"}
    assert local_join.department_id != "international_admissions"


def test_phase_9ai_chatgpt_style_contact_wait_labels_and_safety():
    text = read(TEST_STRINGS) + read(TEST_MODALS) + read(RESULT_DOC)
    public_text = read(PUBLIC_LAUNCH).lower()

    assert "თქვენი კითხვა / შეტყობინება" in text
    assert "Your question / message" in text
    assert "დაელოდე ოპერატორს" in text
    assert "Wait for operator" in text
    assert MOJIBAKE_MARKER not in text
    assert "public_launch_decision=go" not in public_text
    assert "no-go" in public_text


def test_phase_9ai_chatgpt_style_result_doc_status():
    text = read(RESULT_DOC)
    assert "PHASE_9AI_STATUS=PASSED_PENDING_PRIVACY_CONTACT_APPROVAL" in text
    assert "BACKEND_DEPLOYED_CHATGPT_STYLE_KB_ROUTING_OPERATOR_READY_PENDING_PRIVACY_CONTACT_APPROVAL" in text
    assert "REAL_CONTACT_DATA_SENT=NO" in text
    assert "LEAD_TASK_CUSTOMER_CREATED=NO" in text
