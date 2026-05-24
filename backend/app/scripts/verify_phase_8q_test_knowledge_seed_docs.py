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

SEEDED_STATE = "BACKEND_DEPLOYED_TEST_KNOWLEDGE_SEEDED_SAFE_SMOKE_PASSED_PENDING_OFFICIAL_REVIEW_AND_SITE_EMBED"
REVIEW_STATE = "BACKEND_DEPLOYED_TEST_KNOWLEDGE_SEED_NEEDS_REVIEW"

RESULT_DOC = DEPLOYMENT_DOCS / "PRODUCTION_TEST_KNOWLEDGE_SEED_RESULT.md"
APPROVAL_GATE = DEPLOYMENT_DOCS / "TEST_KNOWLEDGE_SEED_APPROVAL_GATE.md"

SECRET_SCAN_FILES = [
    RESULT_DOC,
    APPROVAL_GATE,
    DEPLOYMENT_DOCS / "FULL_STANDALONE_CHATBOT_SMOKE_PLAN.md",
    DEPLOYMENT_DOCS / "STANDALONE_TEST_KNOWLEDGE_RUNBOOK.md",
]

SECRET_PATTERNS = [
    re.compile(r"sk-ant-", re.IGNORECASE),
    re.compile(r"DATABASE_URL", re.IGNORECASE),
    re.compile(r"DB_PASSWORD", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]


@dataclass
class TestKnowledgeSeedDocsCheck:
    name: str
    passed: bool
    detail: str = ""


def _read(paths: list[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


def required_files_exist() -> list[TestKnowledgeSeedDocsCheck]:
    return [
        TestKnowledgeSeedDocsCheck("PRODUCTION_TEST_KNOWLEDGE_SEED_RESULT.md exists", RESULT_DOC.exists(), str(RESULT_DOC)),
        TestKnowledgeSeedDocsCheck("TEST_KNOWLEDGE_SEED_APPROVAL_GATE.md exists", APPROVAL_GATE.exists(), str(APPROVAL_GATE)),
    ]


def approval_gate_executed() -> TestKnowledgeSeedDocsCheck:
    text = APPROVAL_GATE.read_text(encoding="utf-8")
    required = ["APPROVED_AND_EXECUTED", "approved: YES", "execution status: COMPLETED"]
    missing = [item for item in required if item not in text]
    return TestKnowledgeSeedDocsCheck("Test knowledge approval gate executed", not missing, ", ".join(missing))


def result_records_seed_and_smoke() -> TestKnowledgeSeedDocsCheck:
    text = RESULT_DOC.read_text(encoding="utf-8")
    required = [
        "Idempotency result: PASS",
        "Required test knowledge verification: PASS",
        "Safe API Smoke After Seed",
        "Contact-flow test run: NO",
        "Any leads/tasks intentionally created: NO",
        "Official content review is still required",
    ]
    missing = [item for item in required if item not in text]
    return TestKnowledgeSeedDocsCheck("Seed result records idempotency, safe smoke, and review limits", not missing, ", ".join(missing))


def decision_state_documented() -> TestKnowledgeSeedDocsCheck:
    text = _read([DEPLOYMENT_DOCS / "PRODUCTION_READINESS_DECISION.md", DEPLOYMENT_DOCS / "FINAL_PREFLIGHT_GATE.md", NEXT_PHASES, README])
    return TestKnowledgeSeedDocsCheck("Decision state documented", SEEDED_STATE in text or REVIEW_STATE in text)


def no_forbidden_patterns(paths: list[Path] | None = None) -> TestKnowledgeSeedDocsCheck:
    paths = paths or SECRET_SCAN_FILES
    findings: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return TestKnowledgeSeedDocsCheck("No forbidden secret patterns", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> TestKnowledgeSeedDocsCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return TestKnowledgeSeedDocsCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked(project_root: Path = PROJECT_ROOT) -> TestKnowledgeSeedDocsCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return TestKnowledgeSeedDocsCheck(
        ".local-secrets and generated secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks() -> list[TestKnowledgeSeedDocsCheck]:
    return [
        *required_files_exist(),
        approval_gate_executed(),
        result_records_seed_and_smoke(),
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
