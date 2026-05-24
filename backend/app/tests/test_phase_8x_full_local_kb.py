import csv
import json

from app.scripts import build_full_alte_local_kb_reviewer_csv
from app.scripts import import_full_alte_local_kb_to_database
from app.scripts import normalize_full_alte_local_kb
from app.scripts import verify_full_alte_local_kb_import
from app.scripts import verify_phase_8x_full_local_kb
from app.scripts import apply_official_content_review


def test_full_local_kb_scripts_importable():
    assert normalize_full_alte_local_kb.SOURCE_JSONL.name == "alte_knowledge_base_ka.jsonl"
    assert import_full_alte_local_kb_to_database.SEED_PATH.name == "full_alte_local_kb_normalized.jsonl"
    assert build_full_alte_local_kb_reviewer_csv.OUTPUT_CSV.name == "full_alte_local_kb_reviewer_decision_queue.csv"
    assert verify_full_alte_local_kb_import.NORMALIZED_JSONL.exists()
    assert verify_phase_8x_full_local_kb.RESULT_DOC.exists()


def test_normalized_full_local_kb_exists_and_has_expected_counts():
    records = [
        json.loads(line)
        for line in normalize_full_alte_local_kb.NORMALIZED_JSONL.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(records) >= 600
    assert sum(1 for item in records if item["sensitivity"] == "high") > 0
    assert sum(1 for item in records if item["review_required"]) > 0


def test_sensitive_full_local_kb_records_remain_review_required():
    records = [
        json.loads(line)
        for line in normalize_full_alte_local_kb.NORMALIZED_JSONL.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    sensitive = {
        "finance_tuition",
        "deadlines_calendar",
        "required_documents",
        "international_admissions",
        "medicine_md",
        "dentistry",
        "visa_relocation",
    }

    assert all(item["review_required"] is True for item in records if item["category"] in sensitive)
    assert all(item["public_answer_allowed"] is False for item in records if item["category"] in sensitive)


def test_full_local_kb_reviewer_csv_decision_not_prefilled():
    with build_full_alte_local_kb_reviewer_csv.OUTPUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) >= 600
    assert "decision" in rows[0]
    assert all(row["decision"] == "" for row in rows)
    assert any(row["recommended_review_action"] for row in rows)


def test_full_local_kb_no_forbidden_secret_patterns():
    text = "\n".join(
        [
            normalize_full_alte_local_kb.NORMALIZED_JSONL.read_text(encoding="utf-8"),
            build_full_alte_local_kb_reviewer_csv.OUTPUT_CSV.read_text(encoding="utf-8"),
            verify_phase_8x_full_local_kb.RESULT_DOC.read_text(encoding="utf-8"),
        ]
    )

    assert "sk-ant-" not in text
    assert "postgresql+asyncpg://" not in text
    assert "DB_PASSWORD" not in text


def test_apply_script_prefers_full_local_kb_reviewer_csv():
    assert apply_official_content_review.select_review_csv_path().name == "full_alte_local_kb_reviewer_decision_queue.csv"
