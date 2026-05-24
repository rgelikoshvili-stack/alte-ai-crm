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

PASSED_STATE = "BACKEND_DEPLOYED_STANDALONE_API_SMOKE_PASSED_PENDING_TEST_KNOWLEDGE_APPROVAL"
REVIEW_STATE = "BACKEND_DEPLOYED_STANDALONE_API_SMOKE_NEEDS_REVIEW"

SECRET_PATTERNS = [
    re.compile(r"sk-ant-", re.IGNORECASE),
    re.compile(r"DATABASE_URL", re.IGNORECASE),
    re.compile(r"DB_PASSWORD", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]


@dataclass
class ApiSmokeDocsCheck:
    name: str
    passed: bool
    detail: str = ""


REQUIRED_FILES = [
    DEPLOYMENT_DOCS / "STANDALONE_CHATBOT_API_SMOKE_RESULT.md",
    DEPLOYMENT_DOCS / "TEST_KNOWLEDGE_SEED_APPROVAL_GATE.md",
]

SECRET_SCAN_FILES = REQUIRED_FILES + [
    DEPLOYMENT_DOCS / "FULL_STANDALONE_CHATBOT_SMOKE_PLAN.md",
    DEPLOYMENT_DOCS / "STANDALONE_TEST_KNOWLEDGE_RUNBOOK.md",
]


def _read(paths: list[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


def required_files_exist() -> list[ApiSmokeDocsCheck]:
    return [ApiSmokeDocsCheck(f"{path.name} exists", path.exists(), str(path)) for path in REQUIRED_FILES]


def smoke_result_documents_safety() -> ApiSmokeDocsCheck:
    text = (DEPLOYMENT_DOCS / "STANDALONE_CHATBOT_API_SMOKE_RESULT.md").read_text(encoding="utf-8")
    required = [
        "Contact-flow flag used: NO",
        "Phone/email/contact details sent: NO",
        "Any leads/tasks intentionally created: NO",
        "Contact-flow test run: NO",
        "Production test knowledge seed remains pending approval and was not run",
    ]
    missing = [item for item in required if item not in text]
    return ApiSmokeDocsCheck("Smoke result records safe non-contact policy", not missing, ", ".join(missing))


def approval_gate_pending() -> ApiSmokeDocsCheck:
    text = (DEPLOYMENT_DOCS / "TEST_KNOWLEDGE_SEED_APPROVAL_GATE.md").read_text(encoding="utf-8")
    historical_pending = "PENDING_APPROVAL" in text and "approved: PENDING" in text
    executed_after_approval = "APPROVED_AND_EXECUTED" in text and "execution status: COMPLETED" in text
    phrase_present = "Approve Phase 8Q-Execution for production test knowledge seed" in text
    passed = phrase_present and (historical_pending or executed_after_approval)
    detail = "pending" if historical_pending else "executed" if executed_after_approval else "missing pending/executed status"
    if not phrase_present:
        detail = f"{detail}; missing approval phrase"
    return ApiSmokeDocsCheck("Test knowledge seed approval gate status is valid", passed, detail)


def decision_state_documented() -> ApiSmokeDocsCheck:
    text = _read(
        [
            DEPLOYMENT_DOCS / "PRODUCTION_READINESS_DECISION.md",
            DEPLOYMENT_DOCS / "FINAL_PREFLIGHT_GATE.md",
            README,
            NEXT_PHASES,
        ]
    )
    passed = PASSED_STATE in text or REVIEW_STATE in text
    return ApiSmokeDocsCheck("Decision state documented", passed)


def no_forbidden_patterns(paths: list[Path] | None = None) -> ApiSmokeDocsCheck:
    paths = paths or SECRET_SCAN_FILES
    findings: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return ApiSmokeDocsCheck("No forbidden secret patterns", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> ApiSmokeDocsCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return ApiSmokeDocsCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked(project_root: Path = PROJECT_ROOT) -> ApiSmokeDocsCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return ApiSmokeDocsCheck(
        ".local-secrets and generated secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks() -> list[ApiSmokeDocsCheck]:
    return [
        *required_files_exist(),
        smoke_result_documents_safety(),
        approval_gate_pending(),
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
