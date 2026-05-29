from __future__ import annotations

import importlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs" / "knowledge_evidence" / "official_academic_rules"
EXTRACTED = EVIDENCE / "extracted"
QA_PATH = ROOT / "backend" / "app" / "data" / "evaluation" / "alte_official_academic_rules_20_qa.json"
KNOWLEDGE_PATH = ROOT / "backend" / "app" / "data" / "knowledge" / "official_academic_rules_ka_en.json"
ANSWER_KEY = ROOT / "docs" / "evaluation" / "ALTE_OFFICIAL_ACADEMIC_RULES_20_QA_EXPECTED_ANSWER_KEY.md"


def load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase_9t_scripts_importable():
    assert callable(importlib.import_module("app.scripts.evaluate_official_academic_rules_20_qa").main)
    assert callable(importlib.import_module("app.scripts.verify_phase_9t_official_academic_rules_knowledge").main)


def test_manifest_extractions_summary_and_answer_key_exist():
    assert (EVIDENCE / "OFFICIAL_ACADEMIC_RULES_MANIFEST.md").exists()
    assert (EVIDENCE / "OFFICIAL_ACADEMIC_RULES_SUMMARY.md").exists()
    for name in [
        "academic_rules_extracted.txt",
        "bachelor_regulation_extracted.txt",
        "master_regulation_extracted.txt",
        "academic_calendar_geo_extracted.txt",
        "academic_calendar_eng_extracted.txt",
    ]:
        text = (EXTRACTED / name).read_text(encoding="utf-8")
        assert "===== PAGE " in text
    assert ANSWER_KEY.exists()


def test_qa_dataset_has_exactly_20_items_and_expected_classifications():
    qa = load_json(QA_PATH)
    assert len(qa) == 20
    statuses = {item["id"]: item["expected_status"] for item in qa}
    for qid in [f"Q{index:02d}" for index in range(1, 16)] + ["Q18", "Q19"]:
        assert statuses[qid] == "ANSWERABLE"
    assert statuses["Q16"] == "PARTIALLY_ANSWERABLE"
    assert statuses["Q17"] == "NEEDS_ADDITIONAL_OFFICIAL_SOURCE"
    assert statuses["Q20"] == "NEEDS_ADDITIONAL_OFFICIAL_SOURCE"


def test_official_knowledge_items_have_source_refs():
    rows = load_json(KNOWLEDGE_PATH)
    assert rows
    for row in rows:
        assert row["source_id"]
        assert row["document_title"]
        assert row["normalized_file_path"]
        assert row["page_article_reference"]
        assert row["official"] is True
        assert row["requires_exact_source"] is True


def test_no_public_launch_complete_and_no_forbidden_frontend_patterns():
    docs_text = (
        (EVIDENCE / "OFFICIAL_ACADEMIC_RULES_MANIFEST.md").read_text(encoding="utf-8")
        + "\n"
        + (EVIDENCE / "OFFICIAL_ACADEMIC_RULES_SUMMARY.md").read_text(encoding="utf-8")
    )
    assert "Public launch: NO-GO" in docs_text
    assert "PUBLIC_LAUNCH_DECISION=GO" not in docs_text
    assert "PUBLIC_LAUNCH_STATUS=COMPLETE" not in docs_text

    frontend_text = (ROOT / "test_site" / "alte-ai-chat-widget.js").read_text(encoding="utf-8") + "\n" + (
        ROOT / "dist" / "widget" / "alte-ai-chat-widget.js"
    ).read_text(encoding="utf-8")
    assert "/chat/session/start" in frontend_text
    assert "/chat/message" in frontend_text
    for forbidden in ["/api/chat", "api.anthropic.com", "ANTHROPIC_API_KEY", "sk-ant-"]:
        assert forbidden not in frontend_text


def test_no_contact_details_request_in_phase_9t_artifacts():
    text = (
        QA_PATH.read_text(encoding="utf-8")
        + "\n"
        + KNOWLEDGE_PATH.read_text(encoding="utf-8")
        + "\n"
        + ANSWER_KEY.read_text(encoding="utf-8")
    ).lower()
    for forbidden in ["share your phone", "share your email", "phone number", "contact details"]:
        assert forbidden not in text


def test_local_secret_paths_not_tracked():
    result = subprocess.run(
        ["git", "ls-files", "--", ".local-secrets", ".env"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert result.stdout.strip() == ""
