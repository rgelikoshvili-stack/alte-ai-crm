from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs" / "knowledge_evidence" / "official_academic_rules"
EXTRACTED = EVIDENCE / "extracted"
QA_PATH = ROOT / "backend" / "app" / "data" / "evaluation" / "alte_official_academic_rules_20_qa.json"
KNOWLEDGE_PATH = ROOT / "backend" / "app" / "data" / "knowledge" / "official_academic_rules_ka_en.json"
FULL_CHUNKS_PATH = ROOT / "backend" / "app" / "data" / "knowledge" / "official_academic_rules_full_chunks.json"
ANSWER_KEY = ROOT / "docs" / "evaluation" / "ALTE_OFFICIAL_ACADEMIC_RULES_20_QA_EXPECTED_ANSWER_KEY.md"
EVAL_REPORT = ROOT / "docs" / "evaluation" / "ALTE_OFFICIAL_ACADEMIC_RULES_20_QA_EVALUATION_RESULT.md"
RESULT_DOC = ROOT / "docs" / "deployment" / "PHASE_9T_OFFICIAL_ACADEMIC_RULES_IMPORT_RESULT.md"
DB_IMPORT_DOC = ROOT / "docs" / "deployment" / "PHASE_9T_OFFICIAL_ACADEMIC_RULES_DB_IMPORT_RESULT.md"
APPLY_SCRIPT = ROOT / "backend" / "app" / "scripts" / "apply_official_academic_rules_knowledge.py"

EVIDENCE_FILES = [
    "sastsavlo_procesis_maregulirebeli_wesi.pdf",
    "bakalavriatis_debuleba_2.pdf",
    "magistraturis_debuleba.pdf",
    "academic_calendar_geo_2025_2026.pdf",
    "academic_calendar_eng_2025_2026.pdf",
    "phase_9t_import_spec.txt",
]
EXTRACTED_FILES = [
    "academic_rules_extracted.txt",
    "bachelor_regulation_extracted.txt",
    "master_regulation_extracted.txt",
    "academic_calendar_geo_extracted.txt",
    "academic_calendar_eng_extracted.txt",
]
ALLOWED_STATUSES = {
    "ANSWERABLE",
    "PARTIALLY_ANSWERABLE",
    "NEEDS_ADDITIONAL_OFFICIAL_SOURCE",
}
FORBIDDEN_FRONTEND = ["/api/chat", "api.anthropic.com", "ANTHROPIC_API_KEY", "sk-ant-"]
SECRET_PATTERNS = [
    re.compile(r"(?i)\bdatabase_url\s*[:=]\s*\S+"),
    re.compile(r"(?i)\bpassword_hash\b"),
    re.compile(r"(?i)\bpostgres(?:ql)?://"),
    re.compile(r"\bpbkdf2_sha256\$"),
    re.compile(r"\bsk-ant-[A-Za-z0-9_-]+"),
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> list[dict]:
    data = json.loads(read(path))
    if not isinstance(data, list):
        raise AssertionError(f"{path.relative_to(ROOT)} must contain a list")
    return data


def git_ls_files(*paths: str) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--", *paths],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def assert_not_tracked(*paths: str) -> None:
    tracked = git_ls_files(*paths)
    if tracked:
        raise AssertionError(f"Forbidden tracked local secret files: {tracked}")


def main() -> None:
    for name in EVIDENCE_FILES:
        if not (EVIDENCE / name).exists():
            raise AssertionError(f"Missing evidence file: {name}")
    for name in EXTRACTED_FILES:
        path = EXTRACTED / name
        if not path.exists() or "===== PAGE " not in read(path):
            raise AssertionError(f"Missing or invalid extracted file: {name}")
    for path in [
        EVIDENCE / "OFFICIAL_ACADEMIC_RULES_MANIFEST.md",
        EVIDENCE / "OFFICIAL_ACADEMIC_RULES_SUMMARY.md",
        QA_PATH,
        KNOWLEDGE_PATH,
        FULL_CHUNKS_PATH,
        ANSWER_KEY,
        EVAL_REPORT,
        RESULT_DOC,
        DB_IMPORT_DOC,
        APPLY_SCRIPT,
    ]:
        if not path.exists():
            raise AssertionError(f"Missing required artifact: {path.relative_to(ROOT)}")

    qa = load_json(QA_PATH)
    if len(qa) != 20:
        raise AssertionError("QA dataset must have exactly 20 items")
    statuses = {item["id"]: item["expected_status"] for item in qa}
    if any(status not in ALLOWED_STATUSES for status in statuses.values()):
        raise AssertionError("Unexpected QA expected_status found")
    for qid in [f"Q{index:02d}" for index in range(1, 16)] + ["Q18", "Q19"]:
        if statuses.get(qid) != "ANSWERABLE":
            raise AssertionError(f"{qid} must be ANSWERABLE")
    if statuses.get("Q16") != "PARTIALLY_ANSWERABLE":
        raise AssertionError("Q16 must be PARTIALLY_ANSWERABLE")
    if statuses.get("Q17") != "NEEDS_ADDITIONAL_OFFICIAL_SOURCE":
        raise AssertionError("Q17 must need additional official source")
    if statuses.get("Q20") != "NEEDS_ADDITIONAL_OFFICIAL_SOURCE":
        raise AssertionError("Q20 must need additional official source")

    knowledge = load_json(KNOWLEDGE_PATH)
    if not knowledge:
        raise AssertionError("Knowledge artifact is empty")
    for row in knowledge:
        for key in ["source_id", "document_title", "normalized_file_path", "page_article_reference", "text"]:
            if not row.get(key):
                raise AssertionError(f"Knowledge item missing {key}: {row.get('source_id')}")
        if row.get("official") is not True or row.get("requires_exact_source") is not True:
            raise AssertionError(f"Knowledge item lacks official source flags: {row.get('source_id')}")
    full_chunks = load_json(FULL_CHUNKS_PATH)
    if len(full_chunks) < 100:
        raise AssertionError("Full chunk artifact must contain broad coverage from the five official files")
    full_docs = {row.get("document_title") for row in full_chunks}
    if len(full_docs) != 5:
        raise AssertionError("Full chunk artifact must cover all five official source files")
    for row in full_chunks:
        for key in ["source_id", "document_title", "normalized_file_path", "page_article_reference", "text"]:
            if not row.get(key):
                raise AssertionError(f"Full chunk missing {key}: {row.get('source_id')}")
        if row.get("official") is not True or row.get("requires_exact_source") is not True:
            raise AssertionError(f"Full chunk lacks official flags: {row.get('source_id')}")

    frontend_text = read(ROOT / "test_site" / "alte-ai-chat-widget.js") + "\n" + read(
        ROOT / "dist" / "widget" / "alte-ai-chat-widget.js"
    )
    for required in ["/chat/session/start", "/chat/message"]:
        if required not in frontend_text:
            raise AssertionError(f"Frontend endpoint missing: {required}")
    for forbidden in FORBIDDEN_FRONTEND:
        if forbidden in frontend_text:
            raise AssertionError(f"Forbidden frontend pattern found: {forbidden}")

    docs_text = "\n".join(
        read(path)
        for path in [
            EVIDENCE / "OFFICIAL_ACADEMIC_RULES_MANIFEST.md",
            EVIDENCE / "OFFICIAL_ACADEMIC_RULES_SUMMARY.md",
            ANSWER_KEY,
            EVAL_REPORT,
            RESULT_DOC,
            DB_IMPORT_DOC,
        ]
    )
    if "PUBLIC_LAUNCH_DECISION=GO" in docs_text or "PUBLIC_LAUNCH_STATUS=COMPLETE" in docs_text:
        raise AssertionError("Public launch must not be complete")
    if "NO-GO" not in docs_text:
        raise AssertionError("Public launch NO-GO must remain documented")
    if "Real Alte site modified: YES" in docs_text:
        raise AssertionError("Real Alte site must not be marked modified")
    for pattern in SECRET_PATTERNS:
        if pattern.search(docs_text):
            raise AssertionError("Secret-like content found in Phase 9T docs")

    assert_not_tracked(".env", ".local-secrets")
    print("PHASE_9T_OFFICIAL_ACADEMIC_RULES_KNOWLEDGE_VERIFIER=PASS")


if __name__ == "__main__":
    main()
