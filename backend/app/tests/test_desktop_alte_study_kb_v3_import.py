from app.scripts import import_desktop_alte_study_kb_v3_to_database
from app.scripts import normalize_desktop_alte_study_kb_v3


def test_desktop_alte_study_kb_v3_scripts_importable():
    assert normalize_desktop_alte_study_kb_v3.SOURCE_FILE.name == "alte_kb_complete_v3.py"
    assert import_desktop_alte_study_kb_v3_to_database.SEED_PATH.name == "alte_kb_complete_v3_normalized.jsonl"


def test_desktop_alte_study_kb_v3_evidence_and_seed_exist():
    assert normalize_desktop_alte_study_kb_v3.SOURCE_FILE.exists()
    assert normalize_desktop_alte_study_kb_v3.NORMALIZED_JSONL.exists()
    assert normalize_desktop_alte_study_kb_v3.SUMMARY_JSON.exists()


def test_desktop_alte_study_kb_v3_records_review_required_for_sensitive_items():
    records = import_desktop_alte_study_kb_v3_to_database.load_records()

    assert len(records) >= 20
    high_records = [record for record in records if record["sensitivity"] == "high"]
    assert high_records
    assert all(record["review_required"] is True for record in high_records)
    assert all(record["public_answer_allowed"] is False for record in high_records)


def test_desktop_alte_study_kb_v3_no_forbidden_secret_patterns():
    paths = [
        normalize_desktop_alte_study_kb_v3.SOURCE_FILE,
        normalize_desktop_alte_study_kb_v3.NORMALIZED_JSONL,
        normalize_desktop_alte_study_kb_v3.SUMMARY_JSON,
    ]
    forbidden = ["sk" + "-ant-", "postgresql" + "+asyncpg://"]

    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert not any(pattern in text for pattern in forbidden)
