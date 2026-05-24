from __future__ import annotations

import csv
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
PACKAGE_DIR = PROJECT_ROOT / "docs" / "reviewer_package"
DECISIONS_CSV = PACKAGE_DIR / "alte_kb_human_review_decisions.csv"
COMPACT_CSV = PACKAGE_DIR / "alte_kb_human_review_compact.csv"
INSTRUCTIONS = PACKAGE_DIR / "REVIEWER_INSTRUCTIONS_GEO.md"
SUMMARY = PACKAGE_DIR / "REVIEWER_SUMMARY_GEO.md"
VALIDATOR = BACKEND_ROOT / "app" / "scripts" / "validate_human_reviewer_decisions.py"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9A_HUMAN_REVIEWER_PACKAGE_RESULT.md"
DOCS = [
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "docs" / "NEXT_PHASES.md",
    PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md",
    PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md",
    PROJECT_ROOT / "docs" / "deployment" / "OFFICIAL_CONTENT_REVIEW_REPORT.md",
    PROJECT_ROOT / "docs" / "deployment" / "OFFICIAL_CONTENT_REVIEW_CHECKLIST.md",
    PROJECT_ROOT / "docs" / "deployment" / "CHATBOT_PUBLIC_ANSWER_POLICY.md",
    RESULT_DOC,
]
DECISION_STATE = "BACKEND_DEPLOYED_REVIEWER_PACKAGE_READY_PENDING_HUMAN_DECISIONS"
ALLOWED_DECISIONS = {"", "APPROVE", "REWRITE", "ARCHIVE", "HANDOVER_ONLY", "NEEDS_OFFICIAL_SOURCE"}
SECRET_PATTERNS = [
    re.compile("sk" + r"-ant-", re.IGNORECASE),
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
    required = [PACKAGE_DIR, DECISIONS_CSV, COMPACT_CSV, INSTRUCTIONS, SUMMARY, VALIDATOR, RESULT_DOC]
    return [Check(f"Required path exists: {path.name}", path.exists(), str(path)) for path in required]


def read_decision_rows() -> tuple[list[str], list[dict[str, str]]]:
    if not DECISIONS_CSV.exists():
        return [], []
    with DECISIONS_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def reviewer_csv_valid() -> list[Check]:
    headers, rows = read_decision_rows()
    decisions = [(row.get("decision") or "").strip() for row in rows]
    copied = [
        row
        for row in rows
        if (row.get("decision") or "").strip()
        and (row.get("decision") or "").strip() == (row.get("recommended_review_action") or "").strip()
    ]
    invalid = sorted({decision for decision in decisions if decision not in ALLOWED_DECISIONS})
    return [
        Check("Final reviewer CSV has rows", len(rows) == 647, f"rows={len(rows)}"),
        Check("Final reviewer CSV has decision column", "decision" in headers),
        Check("Decision column empty or allowed", not invalid, ", ".join(invalid)),
        Check("recommended_review_action not copied into decision", not copied, f"copied={len(copied)}"),
    ]


def decision_state_documented() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8") for path in DOCS if path.exists())
    return Check("Phase 9A decision state documented", DECISION_STATE in text)


def public_launch_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in DOCS if path.exists())
    bad = [phrase for phrase in ["public launch complete", "full production launch complete", "actual site embed completed"] if phrase in text]
    return Check("Public launch not marked complete", not bad, ", ".join(bad))


def no_forbidden_patterns() -> Check:
    files = [DECISIONS_CSV, COMPACT_CSV, INSTRUCTIONS, SUMMARY, VALIDATOR, *DOCS]
    findings: list[str] = []
    for path in files:
        if not path.exists() or path.is_dir():
            continue
        text = path.read_text(encoding="utf-8-sig" if path.suffix == ".csv" else "utf-8")
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
