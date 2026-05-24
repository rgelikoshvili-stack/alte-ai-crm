from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
DEPLOYMENT_DOCS = PROJECT_ROOT / "docs" / "deployment"
README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"

DECISION_STATES = {
    "BACKEND_DEPLOYED_CONTENT_REVIEW_DRY_RUN_PENDING_REVIEWER_DECISIONS",
    "BACKEND_DEPLOYED_CONTENT_REVIEW_PARTIAL_APPLY_PENDING_OFFICIAL_APPROVAL",
    "BACKEND_DEPLOYED_CONTENT_REVIEW_APPROVED_PENDING_SITE_EMBED",
    "BACKEND_DEPLOYED_REVIEWER_DECISION_CSV_READY_PENDING_HUMAN_REVIEW",
}

REQUIRED_FILES = [
    DEPLOYMENT_DOCS / "OFFICIAL_CONTENT_REVIEW_APPLY_PLAN.md",
    DEPLOYMENT_DOCS / "OFFICIAL_CONTENT_REVIEW_APPLY_RESULT.md",
    BACKEND_ROOT / "app" / "scripts" / "apply_official_content_review.py",
    BACKEND_ROOT / "app" / "scripts" / "verify_official_content_review_apply.py",
]

SECRET_SCAN_FILES = [
    DEPLOYMENT_DOCS / "OFFICIAL_CONTENT_REVIEW_APPLY_PLAN.md",
    DEPLOYMENT_DOCS / "OFFICIAL_CONTENT_REVIEW_APPLY_RESULT.md",
    DEPLOYMENT_DOCS / "OFFICIAL_CONTENT_REVIEW_REPORT.md",
    DEPLOYMENT_DOCS / "OFFICIAL_CONTENT_REVIEW_CHECKLIST.md",
    DEPLOYMENT_DOCS / "CHATBOT_PUBLIC_ANSWER_POLICY.md",
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
class Phase8SCheck:
    name: str
    passed: bool
    detail: str = ""


def _read(paths: list[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


def required_files_exist() -> list[Phase8SCheck]:
    return [Phase8SCheck(f"{path.name} exists", path.exists(), str(path)) for path in REQUIRED_FILES]


def apply_result_records_dry_run() -> Phase8SCheck:
    text = (DEPLOYMENT_DOCS / "OFFICIAL_CONTENT_REVIEW_APPLY_RESULT.md").read_text(encoding="utf-8")
    required = [
        "Dry-Run Summary",
        "`total_rows`: 26",
        "`decision_column_present`:",
        "`valid_decisions`: 0",
        "`missing_decisions`: 26",
        "OFFICIAL_CONTENT_REVIEW_APPLY_STATUS=DRY_RUN_ONLY_PENDING_REVIEWER_DECISIONS",
    ]
    missing = [item for item in required if item not in text]
    return Phase8SCheck("Apply result records dry-run summary", not missing, ", ".join(missing))


def apply_result_records_apply_status() -> Phase8SCheck:
    text = (DEPLOYMENT_DOCS / "OFFICIAL_CONTENT_REVIEW_APPLY_RESULT.md").read_text(encoding="utf-8")
    required = [
        "`--apply` was run: NO",
        "decision",
        "`applied_count`: 0",
    ]
    missing = [item for item in required if item not in text]
    return Phase8SCheck("Apply result records whether apply was run", not missing, ", ".join(missing))


def decision_state_documented() -> Phase8SCheck:
    text = _read([DEPLOYMENT_DOCS / "PRODUCTION_READINESS_DECISION.md", DEPLOYMENT_DOCS / "FINAL_PREFLIGHT_GATE.md", NEXT_PHASES, README])
    found = sorted(state for state in DECISION_STATES if state in text)
    return Phase8SCheck("Phase 8S decision state documented", bool(found), ", ".join(found))


def public_launch_not_falsely_complete() -> Phase8SCheck:
    text = _read([DEPLOYMENT_DOCS / "PRODUCTION_READINESS_DECISION.md", DEPLOYMENT_DOCS / "FINAL_PREFLIGHT_GATE.md", NEXT_PHASES, README])
    has_approved_state = "BACKEND_DEPLOYED_CONTENT_REVIEW_APPROVED_PENDING_SITE_EMBED" in text
    suspicious = [
        "FULL_PUBLIC_LAUNCH_COMPLETE",
        "PUBLIC_LAUNCH_COMPLETE",
        "FULL_PRODUCTION_LAUNCH_COMPLETE",
    ]
    findings = [item for item in suspicious if item in text]
    if has_approved_state:
        return Phase8SCheck("Docs do not falsely mark public launch complete", not findings, ", ".join(findings))
    blocked_terms = [
        "public launch remains blocked",
        "public launch still blocked",
        "public launch blocked",
    ]
    blocked = any(term in text.lower() for term in blocked_terms)
    return Phase8SCheck("Docs do not falsely mark public launch complete", blocked and not findings, ", ".join(findings))


def no_forbidden_patterns(paths: list[Path] | None = None) -> Phase8SCheck:
    paths = paths or SECRET_SCAN_FILES
    findings: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return Phase8SCheck("No forbidden secret patterns", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> Phase8SCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Phase8SCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked(project_root: Path = PROJECT_ROOT) -> Phase8SCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Phase8SCheck(
        ".local-secrets and generated secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks() -> list[Phase8SCheck]:
    return [
        *required_files_exist(),
        apply_result_records_dry_run(),
        apply_result_records_apply_status(),
        decision_state_documented(),
        public_launch_not_falsely_complete(),
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
