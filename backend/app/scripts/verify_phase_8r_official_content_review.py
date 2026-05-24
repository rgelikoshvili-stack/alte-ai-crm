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

DECISION_STATE = "BACKEND_DEPLOYED_TEST_KNOWLEDGE_SEEDED_PENDING_OFFICIAL_CONTENT_REVIEW"

REQUIRED_FILES = [
    DEPLOYMENT_DOCS / "OFFICIAL_CONTENT_REVIEW_REPORT.md",
    DEPLOYMENT_DOCS / "OFFICIAL_CONTENT_REVIEW_CHECKLIST.md",
    DEPLOYMENT_DOCS / "CHATBOT_PUBLIC_ANSWER_POLICY.md",
    DEPLOYMENT_DOCS / "KNOWLEDGE_REVIEW_QUEUE_TEMPLATE.csv",
    BACKEND_ROOT / "app" / "scripts" / "export_knowledge_review_queue.py",
]

SECRET_SCAN_FILES = REQUIRED_FILES[:-1] + [
    DEPLOYMENT_DOCS / "FULL_STANDALONE_CHATBOT_SMOKE_PLAN.md",
    DEPLOYMENT_DOCS / "PRODUCTION_WIDGET_SMOKE_CHECKLIST.md",
    BACKEND_ROOT / "reports" / "knowledge_review_queue.csv",
]

SECRET_PATTERNS = [
    re.compile(r"sk-ant-", re.IGNORECASE),
    re.compile(r"DATABASE_URL", re.IGNORECASE),
    re.compile(r"DB_PASSWORD", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]


@dataclass
class OfficialContentReviewCheck:
    name: str
    passed: bool
    detail: str = ""


def _read(paths: list[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


def required_files_exist() -> list[OfficialContentReviewCheck]:
    return [OfficialContentReviewCheck(f"{path.name} exists", path.exists(), str(path)) for path in REQUIRED_FILES]


def review_status_pending() -> OfficialContentReviewCheck:
    text = (DEPLOYMENT_DOCS / "OFFICIAL_CONTENT_REVIEW_REPORT.md").read_text(encoding="utf-8")
    return OfficialContentReviewCheck(
        "Official content review status pending",
        "OFFICIAL_CONTENT_REVIEW_STATUS=PENDING" in text,
    )


def public_answer_policy_conservative() -> OfficialContentReviewCheck:
    text = (DEPLOYMENT_DOCS / "CHATBOT_PUBLIC_ANSWER_POLICY.md").read_text(encoding="utf-8").lower()
    required = [
        "do not answer exact price",
        "do not answer exact deadline",
        "source is missing",
        "human handover",
        "below `0.70`",
        "ask for phone or email before creating a lead/task",
    ]
    missing = [item for item in required if item not in text]
    return OfficialContentReviewCheck("Public-answer policy contains conservative rules", not missing, ", ".join(missing))


def decision_state_documented() -> OfficialContentReviewCheck:
    text = _read([DEPLOYMENT_DOCS / "PRODUCTION_READINESS_DECISION.md", DEPLOYMENT_DOCS / "FINAL_PREFLIGHT_GATE.md", NEXT_PHASES, README])
    return OfficialContentReviewCheck("Decision state documented", DECISION_STATE in text)


def no_forbidden_patterns(paths: list[Path] | None = None) -> OfficialContentReviewCheck:
    paths = paths or SECRET_SCAN_FILES
    findings: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return OfficialContentReviewCheck("No forbidden secret patterns", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> OfficialContentReviewCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return OfficialContentReviewCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked(project_root: Path = PROJECT_ROOT) -> OfficialContentReviewCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return OfficialContentReviewCheck(
        ".local-secrets and generated secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks() -> list[OfficialContentReviewCheck]:
    return [
        *required_files_exist(),
        review_status_pending(),
        public_answer_policy_conservative(),
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
