from __future__ import annotations

import json
from pathlib import Path

from app.scripts import verify_phase_9as_full_knowledge_operator_verification


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATASET = PROJECT_ROOT / "backend" / "app" / "data" / "evaluation" / "phase_9as_full_knowledge_qa.json"
INVENTORY_DOC = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AS_ACTIVE_KNOWLEDGE_INVENTORY.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AS_FULL_KNOWLEDGE_AND_OPERATOR_VERIFICATION_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"


REQUIRED_CATEGORIES = {
    "official_academic_facts",
    "academic_calendar",
    "admissions",
    "clarification",
    "routing",
    "unsupported",
    "operator_handover",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def dataset() -> list[dict]:
    return json.loads(read(DATASET))


def test_phase_9as_verifier_importable():
    assert callable(verify_phase_9as_full_knowledge_operator_verification.main)


def test_phase_9as_dataset_structure_and_size():
    items = dataset()

    assert len(items) >= 50
    for item in items:
        assert item["id"]
        assert item["question"]
        assert item["language"] in {"ka", "en"}
        assert item["expected_status"] in {"ANSWERABLE", "CLARIFICATION_REQUIRED", "UNSUPPORTED_OPERATOR", "ROUTE_ONLY"}
        assert "should_handover_expected" in item
        assert item["should_create_lead_task_customer_expected"] is False


def test_phase_9as_required_categories_present():
    categories = {item["category"] for item in dataset()}

    assert REQUIRED_CATEGORIES.issubset(categories)


def test_phase_9as_inventory_documents_source_groups():
    text = read(INVENTORY_DOC)

    for group in [
        "official_academic_rules",
        "academic_calendar_2025_2026",
        "admissions_rules",
        "student_status_and_mobility",
        "exams_and_assessment",
        "finance_sources",
        "library_sources",
        "it_support_sources",
    ]:
        assert group in text


def test_phase_9as_result_doc_safety_and_no_go():
    text = read(RESULT_DOC)
    public = read(PUBLIC_LAUNCH).lower()

    assert "PHASE_9AS_FULL_VERIFICATION_STATUS=" in text
    assert "Public launch: NO-GO" in text
    assert "REAL_ALTE_SITE_MODIFIED=NO" in text
    assert "CONTACT_FLOW_EXECUTED=NO" in text
    assert "REAL_CONTACT_DATA_SENT=NO" in text
    assert "LEAD_TASK_CUSTOMER_CREATED=NO" in text
    assert "public_launch_decision=go" not in public


def test_phase_9as_no_secrets_or_real_contact_data_in_new_docs():
    text = "\n".join([read(DATASET), read(INVENTORY_DOC), read(RESULT_DOC)])

    for forbidden in [
        "DATABASE_URL=",
        "ANTHROPIC_API_KEY=",
        "OPENAI_API_KEY=",
        "sk-ant",
        "@gmail.com",
        "+995",
        "555-",
        "599-",
    ]:
        assert forbidden not in text


def test_phase_9as_no_mojibake_in_new_docs():
    text = "\n".join([read(DATASET), read(INVENTORY_DOC), read(RESULT_DOC)])

    for marker in ["áƒ", "â†", "â€¢", "�"]:
        assert marker not in text
