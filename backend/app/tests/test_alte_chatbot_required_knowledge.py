import importlib
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
KB_DIR = PROJECT_ROOT / "backend" / "app" / "knowledge_seed" / "alte_chatbot_required_knowledge"
JSONL_PATH = KB_DIR / "alte_chatbot_required_knowledge.jsonl"
MD_PATH = KB_DIR / "alte_chatbot_required_knowledge.md"
SOURCES_PATH = KB_DIR / "alte_chatbot_required_sources.md"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_alte_chatbot_required_knowledge_scripts_importable():
    assert hasattr(importlib.import_module("app.scripts.build_alte_chatbot_required_knowledge"), "main")
    assert hasattr(importlib.import_module("app.scripts.verify_alte_chatbot_required_knowledge"), "run_checks")


def test_alte_chatbot_required_knowledge_outputs_exist():
    assert JSONL_PATH.exists()
    assert MD_PATH.exists()
    assert SOURCES_PATH.exists()


def test_alte_chatbot_required_knowledge_has_expected_topics_and_sources():
    rows = load_jsonl(JSONL_PATH)
    assert len(rows) >= 300
    topics = {row["topic"] for row in rows}
    assert "საგანმანათლებლო პროგრამები" in topics
    assert "აკადემიური კალენდარი" in topics
    assert "ფინანსური მხარდაჭერა" in topics
    assert "დეკანის გრანტი" in topics
    assert "გენერაციული AI" in topics
    assert "ეთიკა" in topics
    assert len({row["source_title"] for row in rows}) >= 22


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
