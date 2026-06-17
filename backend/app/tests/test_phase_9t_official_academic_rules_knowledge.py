from __future__ import annotations

import importlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs" / "knowledge_evidence" / "official_academic_rules"
EXTRACTED = EVIDENCE / "extracted"
QA_PATH = ROOT / "backend" / "app" / "data" / "evaluation" / "alte_official_academic_rules_20_qa.json"
QA_30_PATH = ROOT / "backend" / "app" / "data" / "evaluation" / "alte_official_academic_rules_30_qa.json"
KNOWLEDGE_PATH = ROOT / "backend" / "app" / "data" / "knowledge" / "official_academic_rules_ka_en.json"
FULL_CHUNKS_PATH = ROOT / "backend" / "app" / "data" / "knowledge" / "official_academic_rules_full_chunks.json"
STRUCTURED_2025_PATH = ROOT / "backend" / "app" / "data" / "knowledge" / "official_academic_rules_2025_2026.json"
CALENDAR_PATH = ROOT / "backend" / "app" / "data" / "knowledge" / "academic_calendar_2025_2026_structured.json"
ANSWER_KEY = ROOT / "docs" / "evaluation" / "ALTE_OFFICIAL_ACADEMIC_RULES_20_QA_EXPECTED_ANSWER_KEY.md"


def load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase_9t_scripts_importable():
    assert callable(importlib.import_module("app.scripts.evaluate_official_academic_rules_20_qa").main)
    assert callable(importlib.import_module("app.scripts.evaluate_official_academic_rules_30_qa").main)
    assert callable(importlib.import_module("app.scripts.prepare_official_academic_rules_30_qa").main)
    assert callable(importlib.import_module("app.scripts.build_official_academic_rules_full_chunks").main)
    assert callable(importlib.import_module("app.scripts.verify_phase_9t_official_academic_rules_knowledge").main)
    assert callable(importlib.import_module("app.scripts.apply_official_academic_rules_knowledge").main)


def test_manifest_extractions_summary_and_answer_key_exist():
    assert (EVIDENCE / "OFFICIAL_ACADEMIC_RULES_MANIFEST.md").exists()
    assert (EVIDENCE / "OFFICIAL_ACADEMIC_RULES_SUMMARY.md").exists()
    for name in [
        "academic_rules_extracted.txt",
        "bachelor_regulation_extracted.txt",
        "master_regulation_extracted.txt",
        "academic_calendar_geo_extracted.txt",
        "academic_calendar_eng_extracted.txt",
        "bakalavriatis_debuleba_2_extracted.txt",
        "sastsavlo_procesis_maregulirebeli_wesi_extracted.txt",
        "magistraturis_debuleba_extracted.txt",
        "academic_calendar_geo_2025_2026_extracted.txt",
        "academic_calendar_eng_2025_2026_extracted.txt",
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


def test_qa_dataset_has_exactly_30_items_and_expected_fields():
    qa = load_json(QA_30_PATH)
    assert len(qa) == 30
    required = {
        "id",
        "question",
        "language",
        "expected_status",
        "expected_source_documents",
        "expected_source_pages_or_articles",
        "expected_answer_summary",
        "required_exact_values",
        "forbidden_hallucinations",
        "should_handover_if_uncertain",
        "must_not_request_contact_details",
    }
    assert [item["id"] for item in qa] == [f"Q{index:02d}" for index in range(1, 31)]
    for item in qa:
        assert required.issubset(item)
        assert item["expected_status"] in {"ANSWERABLE", "PARTIALLY_ANSWERABLE", "NEEDS_ADDITIONAL_OFFICIAL_SOURCE"}
        assert item["expected_source_documents"]
        assert item["required_exact_values"]
        assert item["should_handover_if_uncertain"] is True
        assert item["must_not_request_contact_details"] is True


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


def test_structured_kb_and_calendar_exist_with_required_values():
    rows = load_json(STRUCTURED_2025_PATH)
    assert len(rows) >= 30
    text = STRUCTURED_2025_PATH.read_text(encoding="utf-8")
    for expected in ["240 ECTS", "360 ECTS", "300 ECTS", "120 ECTS", "5 years", "GPA = (X - 50) * 0.06 + 1"]:
        assert expected in text
    for row in rows:
        assert row["official"] is True
        assert row["stale"] is False
        assert row["public_answer_allowed"] is True
        assert row["answer_policy"] == "conservative_official_source_only"
        assert row["requires_exact_source"] is True
        assert row["handover_if_uncertain"] is True
    calendar = json.loads(CALENDAR_PATH.read_text(encoding="utf-8"))
    assert set(calendar) == {
        "bachelor_except_computer_science",
        "computer_science_geo_eng",
        "master_programs",
        "one_cycle_programs",
        "first_year_one_cycle_english_programs",
    }
    assert "17-22 November" in calendar["bachelor_except_computer_science"]["midterm_exams"]
    assert "9-14 March" in calendar["computer_science_geo_eng"]["academic_registration"]
    assert "16 March" in calendar["master_programs"]["spring_semester_dates"]
    assert "20-31 July" in calendar["one_cycle_programs"]["final_exams"]


def test_full_chunk_artifact_covers_all_five_official_files():
    rows = load_json(FULL_CHUNKS_PATH)
    assert len(rows) >= 100
    assert len({row["document_title"] for row in rows}) == 5
    for row in rows:
        assert row["source_id"].startswith("official_academic_rules_full_")
        assert row["document_title"]
        assert row["normalized_file_path"]
        assert row["page_article_reference"]
        assert row["text"]
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
        + QA_30_PATH.read_text(encoding="utf-8")
        + "\n"
        + KNOWLEDGE_PATH.read_text(encoding="utf-8")
        + "\n"
        + STRUCTURED_2025_PATH.read_text(encoding="utf-8")
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
