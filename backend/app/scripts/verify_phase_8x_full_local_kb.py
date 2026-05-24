from __future__ import annotations

import csv
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
EVIDENCE_DIR = PROJECT_ROOT / "docs" / "knowledge_evidence" / "alte_full_local_kb"
NORMALIZED_JSONL = BACKEND_ROOT / "app" / "knowledge_seed" / "full_alte_local_kb" / "full_alte_local_kb_normalized.jsonl"
SUMMARY_JSON = BACKEND_ROOT / "reports" / "full_alte_local_kb_normalization_summary.json"
REVIEWER_CSV = BACKEND_ROOT / "reports" / "full_alte_local_kb_reviewer_decision_queue.csv"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "FULL_ALTE_LOCAL_KB_IMPORT_RESULT.md"
README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
READINESS = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md"
FINAL_PREFLIGHT = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md"

DECISION_STATES = {
    "BACKEND_DEPLOYED_FULL_LOCAL_KB_IMPORTED_PENDING_HUMAN_REVIEW",
    "BACKEND_DEPLOYED_FULL_LOCAL_KB_NORMALIZED_PENDING_DB_IMPORT",
}
ALLOWED_DECISIONS = {"APPROVE", "REWRITE", "ARCHIVE", "HANDOVER_ONLY", "NEEDS_OFFICIAL_SOURCE", ""}
SECRET_PATTERNS = [
    re.compile(r"sk-ant-", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
    re.compile(r"DB_PASSWORD\s*=", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def required_files_exist() -> list[Check]:
    required = [
        EVIDENCE_DIR / "alte_knowledge_base_ka.jsonl",
        EVIDENCE_DIR / "alte_knowledge_base_index.md",
        EVIDENCE_DIR / "alte_source_urls.txt",
        EVIDENCE_DIR / "alte_university_knowledge_base.py",
        EVIDENCE_DIR / "alte_university_knowledge_base_v2.py",
        EVIDENCE_DIR / "prototype" / "app.js",
        NORMALIZED_JSONL,
        SUMMARY_JSON,
        REVIEWER_CSV,
        RESULT_DOC,
        BACKEND_ROOT / "app" / "scripts" / "normalize_full_alte_local_kb.py",
        BACKEND_ROOT / "app" / "scripts" / "import_full_alte_local_kb_to_database.py",
        BACKEND_ROOT / "app" / "scripts" / "verify_full_alte_local_kb_import.py",
        BACKEND_ROOT / "app" / "scripts" / "build_full_alte_local_kb_reviewer_csv.py",
    ]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in required]


def reviewer_csv_valid() -> list[Check]:
    if not REVIEWER_CSV.exists():
        return [Check("Reviewer CSV valid", False, "missing")]
    with REVIEWER_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    decisions = [row.get("decision", "") for row in rows]
    return [
        Check("Reviewer CSV has rows", len(rows) >= 600, f"rows={len(rows)}"),
        Check("Reviewer CSV has decision column", "decision" in (rows[0].keys() if rows else [])),
        Check("Reviewer decisions empty or allowed", all(item in ALLOWED_DECISIONS for item in decisions)),
        Check(
            "Reviewer decisions not auto-filled",
            not any(item for item in decisions),
            "decision column should remain blank for human review",
        ),
    ]


def decision_state_documented() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8") for path in [README, NEXT_PHASES, READINESS, FINAL_PREFLIGHT] if path.exists())
    return Check("Phase decision state documented", any(state in text for state in DECISION_STATES))


def public_launch_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in [README, NEXT_PHASES, READINESS, FINAL_PREFLIGHT] if path.exists())
    bad = [phrase for phrase in ["public launch complete", "full production launch complete", "actual site embed completed"] if phrase in text]
    return Check("Public launch not marked complete", not bad, ", ".join(bad))


def no_forbidden_patterns() -> Check:
    files = [
        RESULT_DOC,
        README,
        NEXT_PHASES,
        READINESS,
        FINAL_PREFLIGHT,
        NORMALIZED_JSONL,
        REVIEWER_CSV,
    ]
    findings: list[str] = []
    for path in files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return Check("No forbidden secret patterns", not findings, ", ".join(findings))


def env_not_tracked() -> Check:
    result = subprocess.run(["git", "ls-files", ".env", "backend/.env"], cwd=PROJECT_ROOT, capture_output=True, text=True)
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked() -> Check:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".local-secrets not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def run_checks() -> list[Check]:
    return [
        *required_files_exist(),
        *reviewer_csv_valid(),
        decision_state_documented(),
        public_launch_not_complete(),
        no_forbidden_patterns(),
        env_not_tracked(),
        local_secrets_not_tracked(),
    ]


def main() -> None:
    checks = run_checks()
    for check in checks:
        print(f"{'PASS' if check.passed else 'FAIL'} {check.name}: {check.detail}")
    if any(not check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
