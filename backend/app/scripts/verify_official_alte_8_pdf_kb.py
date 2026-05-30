from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_DIR = PROJECT_ROOT / "docs" / "knowledge_evidence" / "official_alte_8_pdf_kb"
OUTPUT_DIR = PROJECT_ROOT / "backend" / "app" / "knowledge_seed" / "official_alte_8_pdf_kb"
JSONL_PATH = OUTPUT_DIR / "official_alte_8_pdf_kb_normalized.jsonl"
QUESTION_BANK_PATH = OUTPUT_DIR / "official_alte_8_pdf_supported_questions.jsonl"
TAXONOMY_PATH = OUTPUT_DIR / "topic_taxonomy.json"
ANSWER_POLICY_PATH = OUTPUT_DIR / "official_alte_8_pdf_answer_policy.json"
MANIFEST_PATH = EVIDENCE_DIR / "OFFICIAL_ALTE_8_PDF_SOURCE_MANIFEST.md"
REVIEWER_CSV_PATH = PROJECT_ROOT / "backend" / "reports" / "official_alte_8_pdf_kb_reviewer_queue.csv"
APPLY_RESULT_PATH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9T_OFFICIAL_ALTE_8_PDF_KB_APPLY_RESULT.md"

PDFS = [
    "01_program_catalog.pdf",
    "02_academic_calendar_2025_2026.pdf",
    "03_financial_support_mechanisms_2026_04_07.pdf",
    "04_state_social_grants.pdf",
    "05_bachelor_regulation.pdf",
    "06_master_regulation.pdf",
    "07_ects_credit_recognition.pdf",
    "08_study_process_regulation.pdf",
]
SENSITIVE_FILES = {
    "02_academic_calendar_2025_2026.pdf",
    "03_financial_support_mechanisms_2026_04_07.pdf",
    "04_state_social_grants.pdf",
    "07_ects_credit_recognition.pdf",
    "08_study_process_regulation.pdf",
}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def is_tracked(path: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", path],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def run_checks() -> dict:
    for pdf in PDFS:
        require((EVIDENCE_DIR / pdf).exists(), f"Missing PDF: {pdf}")
    for path in [JSONL_PATH, QUESTION_BANK_PATH, TAXONOMY_PATH, ANSWER_POLICY_PATH, MANIFEST_PATH, REVIEWER_CSV_PATH, APPLY_RESULT_PATH]:
        require(path.exists(), f"Missing generated file: {path}")

    rows = load_jsonl(JSONL_PATH)
    require(rows, "JSONL has no rows")
    by_file = Counter(row["source_file"] for row in rows)
    for pdf in PDFS:
        require(by_file[pdf] > 0, f"No chunks for {pdf}")

    required_fields = {
        "source_id",
        "source_file",
        "page_start",
        "page_end",
        "department",
        "topic",
        "content",
        "answer_policy",
        "sensitivity",
        "review_required",
        "public_answer_allowed",
    }
    for row in rows:
        missing = required_fields - row.keys()
        require(not missing, f"Chunk missing fields {missing}: {row.get('source_id')}")
        require(str(row["content"]).strip(), f"Empty content: {row.get('source_id')}")
        if row["source_file"] in SENSITIVE_FILES or row["topic"] in {"finance", "tuition", "academic_calendar", "student_status", "exams", "mobility_and_credit_recognition"}:
            require(row["review_required"] is True, f"Sensitive chunk not review_required: {row['source_id']}")

    questions = load_jsonl(QUESTION_BANK_PATH)
    require(any(row["language"] == "ka" for row in questions), "Question bank missing Georgian questions")
    require(any(row["language"] == "en" for row in questions), "Question bank missing English questions")

    taxonomy = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))
    policy = json.loads(ANSWER_POLICY_PATH.read_text(encoding="utf-8"))
    for topic in ["programs", "finance", "academic_calendar", "study_process", "mobility_and_credit_recognition"]:
        require(topic in taxonomy, f"Taxonomy missing {topic}")
        require(topic in policy, f"Answer policy missing {topic}")

    risky = [row for row in rows if row["topic"] in {"finance", "tuition", "academic_calendar", "student_status", "exams"}]
    require(risky, "No risky topic chunks found")
    require(all(row["answer_policy"] in {"conservative", "handover_if_uncertain", "handover_only"} for row in risky), "Risky topics must use conservative/handover policy")

    with REVIEWER_CSV_PATH.open("r", encoding="utf-8-sig", newline="") as fh:
        csv_rows = list(csv.DictReader(fh))
    require(len(csv_rows) == len(rows), "Reviewer CSV row count must match normalized chunks")

    generated_text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in [JSONL_PATH, QUESTION_BANK_PATH, TAXONOMY_PATH, ANSWER_POLICY_PATH, MANIFEST_PATH])
    for pattern in [r"ANTHROPIC_API_KEY", "sk" + r"-ant", r"api\.anthropic\.com"]:
        require(not re.search(pattern, generated_text, re.IGNORECASE), f"Forbidden generated marker: {pattern}")
    require(not is_tracked(".env"), ".env must not be tracked")
    require(not is_tracked(".local-secrets"), ".local-secrets must not be tracked")
    apply_text = APPLY_RESULT_PATH.read_text(encoding="utf-8", errors="ignore")
    require("PHASE_9T_OFFICIAL_ALTE_8_PDF_KB_APPLY_STATUS=APPLIED_TO_PRODUCTION_KB_SINGLE_SMOKE_PASSED" in apply_text, "Apply result status is not applied")
    require("Public launch: NO-GO" in apply_text, "Public launch must remain NO-GO")

    return {
        "status": "PASS",
        "total_chunks": len(rows),
        "chunks_by_document": dict(by_file),
        "review_required_count": sum(1 for row in rows if row["review_required"]),
    }


def main() -> None:
    print(json.dumps(run_checks(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
