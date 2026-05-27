import importlib
import json
import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
KB_DIR = PROJECT_ROOT / "backend" / "app" / "knowledge_seed" / "alte_chatbot_required_knowledge"
JSONL_PATH = KB_DIR / "alte_chatbot_required_knowledge.jsonl"
MD_PATH = KB_DIR / "alte_chatbot_required_knowledge.md"
SOURCES_PATH = KB_DIR / "alte_chatbot_required_sources.md"
SMOKE_QUESTIONS_PATH = KB_DIR / "alte_chatbot_required_smoke_questions.jsonl"
REVIEW_SUMMARY_PATH = KB_DIR / "alte_chatbot_required_review_summary.md"
REVIEWER_CSV_PATH = PROJECT_ROOT / "backend" / "reports" / "alte_chatbot_required_knowledge_reviewer_queue.csv"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_alte_chatbot_required_knowledge_scripts_importable():
    assert hasattr(importlib.import_module("app.scripts.build_alte_chatbot_required_knowledge"), "main")
    assert hasattr(importlib.import_module("app.scripts.verify_alte_chatbot_required_knowledge"), "run_checks")
    assert hasattr(importlib.import_module("app.scripts.apply_alte_chatbot_required_knowledge"), "main")


def test_alte_chatbot_required_knowledge_outputs_exist():
    assert JSONL_PATH.exists()
    assert MD_PATH.exists()
    assert SOURCES_PATH.exists()
    assert SMOKE_QUESTIONS_PATH.exists()
    assert REVIEW_SUMMARY_PATH.exists()
    assert REVIEWER_CSV_PATH.exists()


def test_alte_chatbot_required_knowledge_has_expected_topics_and_sources():
    rows = load_jsonl(JSONL_PATH)
    assert len(rows) >= 300
    topics = {row["topic"] for row in rows}
    assert "საგანმანათლებლო პროგრამები" in topics
    assert "აკადემიური კალენდარი" in topics
    assert "ფინანსური მხარდაჭერა" in topics
    assert "სახელმწიფო და სოციალური გრანტები" in topics
    assert "ფინანსური საკითხების დეპარტამენტი" in topics
    assert "დეკანის გრანტი" in topics
    assert "საერთაშორისო სტუდენტები და ურთიერთობები" in topics
    assert "IT მხარდაჭერა" in topics
    assert "ფორმალური კომუნიკაცია და განცხადებები" in topics
    assert "გენერაციული AI" in topics
    assert "ეთიკა" in topics
    assert len({row["source_title"] for row in rows}) >= 30


def test_alte_chatbot_required_knowledge_is_georgian_and_student_facing():
    rows = load_jsonl(JSONL_PATH)
    for row in rows:
        assert row["language"] == "ka"
        assert row["student_facing"] is True
        assert row["question"]
        assert row["answer"]
        assert "áƒ" not in row["question"]
        assert "áƒ" not in row["answer"][:500]


def test_alte_chatbot_required_knowledge_finance_and_registry_are_cautious():
    rows = load_jsonl(JSONL_PATH)
    cautious = [row for row in rows if row["department"] in {"finance", "academic_registry"}]
    assert cautious
    assert all(row["answer_policy"] != "direct_general" or row["handover_recommended"] for row in cautious)


def test_alte_chatbot_required_knowledge_has_no_forbidden_secret_patterns():
    text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in [JSONL_PATH, MD_PATH, SOURCES_PATH])
    for forbidden in ["ANTHROPIC_API_KEY", "sk" + "-ant", "api.anthropic.com", "DATABASE_URL"]:
        assert forbidden not in text


def test_alte_chatbot_required_knowledge_reviewer_queue_matches_jsonl_and_is_blank():
    rows = load_jsonl(JSONL_PATH)
    with REVIEWER_CSV_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        reviewer_rows = list(csv.DictReader(handle))
    assert len(reviewer_rows) == len(rows)
    assert all(row["reviewer_decision"] == "" for row in reviewer_rows)


def test_alte_chatbot_required_knowledge_smoke_questions_cover_core_topics():
    smoke_rows = load_jsonl(SMOKE_QUESTIONS_PATH)
    assert len(smoke_rows) >= 20
    topics = {row["expected_topic"] for row in smoke_rows}
    assert "ფინანსური მხარდაჭერა" in topics
    assert "სახელმწიფო და სოციალური გრანტები" in topics
    assert "ბაკალავრიატი" in topics
    assert "მაგისტრატურა" in topics
    assert "IT მხარდაჭერა" in topics
    assert all(row["no_contact_details"] is True for row in smoke_rows)


def test_alte_chatbot_required_knowledge_apply_script_defaults_to_dry_run_text():
    script_text = (PROJECT_ROOT / "backend" / "app" / "scripts" / "apply_alte_chatbot_required_knowledge.py").read_text(encoding="utf-8")
    assert "--apply" in script_text
    assert "--approve-for-chatbot" in script_text
    assert "dry-run" in script_text
    assert '"would_write": False' in script_text
    assert "approve_for_chatbot" in script_text
