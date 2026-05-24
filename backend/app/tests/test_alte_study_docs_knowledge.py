from pathlib import Path

from app.scripts import normalize_alte_study_docs
from app.scripts import seed_alte_study_docs_knowledge
from app.scripts import verify_alte_study_docs_knowledge


def test_study_docs_scripts_importable():
    assert normalize_alte_study_docs.SEED_PATH.name == "alte_study_docs_seed_v1.json"
    assert seed_alte_study_docs_knowledge.SEED_PATH.name == "alte_study_docs_seed_v1.json"


def test_study_docs_seed_exists_and_valid():
    check = verify_alte_study_docs_knowledge.seed_records_valid()

    assert check.passed is True


def test_sensitive_study_docs_are_review_required_in_seed():
    records = seed_alte_study_docs_knowledge.load_records()
    sensitive = {
        "finance_tuition",
        "deadlines_calendar",
        "required_documents",
        "international_admissions",
        "medicine_md",
    }

    assert any(record["category"] == "finance_tuition" for record in records)
    assert all(record["review_required"] is True for record in records if record["category"] in sensitive)


def test_study_docs_seed_has_no_secret_patterns():
    text = seed_alte_study_docs_knowledge.SEED_PATH.read_text(encoding="utf-8")

    assert "sk-ant-" not in text
    assert "postgresql+asyncpg://" not in text
    assert "DB_PASSWORD" not in text


def test_study_docs_evidence_files_exist():
    missing = [
        name
        for name in normalize_alte_study_docs.SOURCE_FILES
        if not (normalize_alte_study_docs.EVIDENCE_DIR / name).exists()
    ]

    assert missing == []


def test_study_docs_import_doc_exists():
    path = Path(__file__).resolve().parents[3] / "docs" / "deployment" / "ALTE_STUDY_DOCS_KNOWLEDGE_IMPORT.md"

    assert path.exists()
