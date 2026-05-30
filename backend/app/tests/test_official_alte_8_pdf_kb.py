import importlib
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
KB_DIR = PROJECT_ROOT / "backend" / "app" / "knowledge_seed" / "official_alte_8_pdf_kb"
JSONL_PATH = KB_DIR / "official_alte_8_pdf_kb_normalized.jsonl"
QUESTION_PATH = KB_DIR / "official_alte_8_pdf_supported_questions.jsonl"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_official_alte_8_pdf_script_importability():
    assert hasattr(importlib.import_module("app.scripts.build_official_alte_8_pdf_kb"), "main")
    assert hasattr(importlib.import_module("app.scripts.verify_official_alte_8_pdf_kb"), "run_checks")
    assert hasattr(importlib.import_module("app.scripts.apply_official_alte_8_pdf_kb"), "main")
    assert hasattr(importlib.import_module("app.scripts.apply_official_alte_8_pdf_kb_cloudsql"), "main")


def test_official_alte_8_pdf_normalized_jsonl_exists_and_has_8_sources():
    rows = load_jsonl(JSONL_PATH)
    assert rows
    assert len({row["source_file"] for row in rows}) == 8
    for row in rows:
        assert row["source_id"]
        assert row["page_start"] >= 1
        assert row["department"]
        assert row["topic"]
        assert row["content"]
        assert row["answer_policy"]


def test_official_alte_8_pdf_high_risk_documents_are_review_required():
    rows = load_jsonl(JSONL_PATH)
    risky_files = {
        "03_financial_support_mechanisms_2026_04_07.pdf",
        "04_state_social_grants.pdf",
        "07_ects_credit_recognition.pdf",
        "08_study_process_regulation.pdf",
    }
    risky_rows = [row for row in rows if row["source_file"] in risky_files]
    assert risky_rows
    assert all(row["review_required"] is True for row in risky_rows)
    assert all(row["answer_policy"] in {"conservative", "handover_if_uncertain", "handover_only"} for row in risky_rows)


def test_official_alte_8_pdf_question_bank_has_ka_and_en():
    questions = load_jsonl(QUESTION_PATH)
    assert any(row["language"] == "ka" for row in questions)
    assert any(row["language"] == "en" for row in questions)
    assert any(row["expected_topic"] == "finance" for row in questions)
    assert any(row["expected_topic"] == "academic_calendar" for row in questions)


def test_official_alte_8_pdf_policy_files_exist():
    assert (KB_DIR / "topic_taxonomy.json").exists()
    assert (KB_DIR / "official_alte_8_pdf_answer_policy.json").exists()
    assert (PROJECT_ROOT / "backend" / "reports" / "official_alte_8_pdf_kb_reviewer_queue.csv").exists()
    assert (PROJECT_ROOT / "docs" / "knowledge_evidence" / "official_alte_8_pdf_kb" / "OFFICIAL_ALTE_8_PDF_SOURCE_MANIFEST.md").exists()
    apply_result = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9T_OFFICIAL_ALTE_8_PDF_KB_APPLY_RESULT.md"
    assert apply_result.exists()
    assert "PHASE_9T_OFFICIAL_ALTE_8_PDF_KB_APPLY_STATUS=APPLIED_TO_PRODUCTION_KB_SINGLE_SMOKE_PASSED" in apply_result.read_text(encoding="utf-8")


def test_official_alte_8_pdf_generated_files_have_no_secrets():
    text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in [
            JSONL_PATH,
            QUESTION_PATH,
            KB_DIR / "topic_taxonomy.json",
            KB_DIR / "official_alte_8_pdf_answer_policy.json",
        ]
    )
    for forbidden in ["ANTHROPIC_API_KEY", "sk" + "-ant", "api.anthropic.com"]:
        assert forbidden not in text
