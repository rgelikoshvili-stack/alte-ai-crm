from __future__ import annotations

import csv
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from app.scripts.apply_official_content_review import (
    ALLOWED_DECISIONS,
    FULL_LOCAL_KB_REVIEWER_CSV_PATH,
    REVIEWER_CSV_PATH,
    select_review_csv_path,
)


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
DEPLOYMENT_DOCS = PROJECT_ROOT / "docs" / "deployment"
README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"

DECISION_STATE = "BACKEND_DEPLOYED_REVIEWER_DECISION_CSV_READY_PENDING_HUMAN_REVIEW"
REQUIRED_COLUMNS = {"decision", "reviewer", "review_date", "reviewer_notes"}
INSTRUCTIONS = DEPLOYMENT_DOCS / "REVIEWER_DECISION_CSV_INSTRUCTIONS.md"

SECRET_SCAN_FILES = [
    DEPLOYMENT_DOCS / "REVIEWER_DECISION_CSV_INSTRUCTIONS.md",
    DEPLOYMENT_DOCS / "OFFICIAL_CONTENT_REVIEW_APPLY_PLAN.md",
    DEPLOYMENT_DOCS / "OFFICIAL_CONTENT_REVIEW_APPLY_RESULT.md",
    DEPLOYMENT_DOCS / "OFFICIAL_CONTENT_REVIEW_REPORT.md",
    DEPLOYMENT_DOCS / "OFFICIAL_CONTENT_REVIEW_CHECKLIST.md",
    DEPLOYMENT_DOCS / "STANDALONE_TEST_KNOWLEDGE_RUNBOOK.md",
    DEPLOYMENT_DOCS / "PRODUCTION_READINESS_DECISION.md",
    DEPLOYMENT_DOCS / "FINAL_PREFLIGHT_GATE.md",
    NEXT_PHASES,
    README,
]

SECRET_PATTERNS = [
    re.compile(r"sk-ant-", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
    re.compile(r"DB_PASSWORD\s*=\s*[^`\s<>{}]+", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]


@dataclass
class Phase8TCheck:
    name: str
    passed: bool
    detail: str = ""


def load_reviewer_rows(path: Path = REVIEWER_CSV_PATH) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def reviewer_csv_exists() -> Phase8TCheck:
    return Phase8TCheck("Reviewer CSV exists", REVIEWER_CSV_PATH.exists(), str(REVIEWER_CSV_PATH))


def reviewer_columns_present() -> Phase8TCheck:
    if not REVIEWER_CSV_PATH.exists():
        return Phase8TCheck("Reviewer columns present", False, "reviewer CSV missing")
    headers, _rows = load_reviewer_rows()
    missing = sorted(REQUIRED_COLUMNS.difference(headers))
    return Phase8TCheck("Reviewer columns present", not missing, ", ".join(missing))


def decision_values_allowed_or_empty() -> Phase8TCheck:
    if not REVIEWER_CSV_PATH.exists():
        return Phase8TCheck("Decision column empty or allowed", False, "reviewer CSV missing")
    _headers, rows = load_reviewer_rows()
    invalid = sorted(
        {
            (row.get("decision") or "").strip().upper()
            for row in rows
            if (row.get("decision") or "").strip() and (row.get("decision") or "").strip().upper() not in ALLOWED_DECISIONS
        }
    )
    return Phase8TCheck("Decision column empty or allowed", not invalid, ", ".join(invalid))


def recommended_action_not_copied_to_decision() -> Phase8TCheck:
    if not REVIEWER_CSV_PATH.exists():
        return Phase8TCheck("recommended_action not copied into decision", False, "reviewer CSV missing")
    _headers, rows = load_reviewer_rows()
    copied = [
        row.get("source_key", "")
        for row in rows
        if (row.get("decision") or "").strip()
        and (row.get("decision") or "").strip().upper() == (row.get("recommended_action") or "").strip().upper()
    ]
    empty_count = sum(1 for row in rows if not (row.get("decision") or "").strip())
    return Phase8TCheck(
        "recommended_action not copied into decision",
        not copied and empty_count == len(rows),
        f"copied={len(copied)}, empty={empty_count}, rows={len(rows)}",
    )


def instructions_exist() -> Phase8TCheck:
    return Phase8TCheck("Reviewer instructions exist", INSTRUCTIONS.exists(), str(INSTRUCTIONS))


def apply_script_prefers_reviewer_csv() -> Phase8TCheck:
    selected = select_review_csv_path()
    return Phase8TCheck(
        "Apply script uses a reviewer CSV when present",
        selected in {REVIEWER_CSV_PATH, FULL_LOCAL_KB_REVIEWER_CSV_PATH},
        str(selected),
    )


def decision_state_documented() -> Phase8TCheck:
    docs = [DEPLOYMENT_DOCS / "PRODUCTION_READINESS_DECISION.md", DEPLOYMENT_DOCS / "FINAL_PREFLIGHT_GATE.md", NEXT_PHASES, README]
    text = "\n".join(path.read_text(encoding="utf-8") for path in docs if path.exists())
    return Phase8TCheck("Phase 8T decision state documented", DECISION_STATE in text)


def no_forbidden_patterns(paths: list[Path] | None = None) -> Phase8TCheck:
    paths = paths or SECRET_SCAN_FILES
    findings: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return Phase8TCheck("No forbidden secret patterns", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> Phase8TCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Phase8TCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked(project_root: Path = PROJECT_ROOT) -> Phase8TCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Phase8TCheck(
        ".local-secrets and generated secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks() -> list[Phase8TCheck]:
    return [
        reviewer_csv_exists(),
        reviewer_columns_present(),
        decision_values_allowed_or_empty(),
        recommended_action_not_copied_to_decision(),
        instructions_exist(),
        apply_script_prefers_reviewer_csv(),
        decision_state_documented(),
        no_forbidden_patterns(),
        env_not_tracked(),
        local_secrets_not_tracked(),
    ]


def main() -> None:
    checks = run_checks()
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"{status} {check.name}: {check.detail}")
    if any(not check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
