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

SMOKE_SCRIPT = BACKEND_ROOT / "app" / "scripts" / "production_knowledge_smoke_after_study_docs.py"
RESULT_DOC = DEPLOYMENT_DOCS / "PRODUCTION_KNOWLEDGE_SMOKE_AFTER_STUDY_DOCS_RESULT.md"
PASSED_STATE = "BACKEND_DEPLOYED_STUDY_DOCS_KB_SMOKE_PASSED_PENDING_REVIEW_AND_SITE_EMBED"
FAILED_STATE = "BACKEND_DEPLOYED_STUDY_DOCS_KB_SMOKE_FAILED_NEEDS_REVIEW"

DOC_FILES = [
    RESULT_DOC,
    DEPLOYMENT_DOCS / "PRODUCTION_READINESS_DECISION.md",
    DEPLOYMENT_DOCS / "FINAL_PREFLIGHT_GATE.md",
    DEPLOYMENT_DOCS / "OFFICIAL_CONTENT_REVIEW_REPORT.md",
    DEPLOYMENT_DOCS / "CHATBOT_PUBLIC_ANSWER_POLICY.md",
    DEPLOYMENT_DOCS / "STANDALONE_TEST_KNOWLEDGE_RUNBOOK.md",
    NEXT_PHASES,
    README,
]

SECRET_PATTERNS = [
    re.compile(r"sk-ant-", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
    re.compile(r"DB_PASSWORD\s*=", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]


@dataclass
class Phase8WCheck:
    name: str
    passed: bool
    detail: str = ""


def read_docs(paths: list[Path] | None = None) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in (paths or DOC_FILES) if path.exists())


def required_files_exist() -> list[Phase8WCheck]:
    return [
        Phase8WCheck("Production knowledge smoke script exists", SMOKE_SCRIPT.exists(), str(SMOKE_SCRIPT)),
        Phase8WCheck("Production knowledge smoke result exists", RESULT_DOC.exists(), str(RESULT_DOC)),
    ]


def import_summary_recorded() -> Phase8WCheck:
    text = RESULT_DOC.read_text(encoding="utf-8") if RESULT_DOC.exists() else ""
    required = ["sources_created=11", "snippets_created=11", "high_sensitivity_records=5", "review_required_records=8"]
    missing = [item for item in required if item not in text]
    return Phase8WCheck("Phase 8V import summary recorded", not missing, ", ".join(missing))


def smoke_status_recorded() -> Phase8WCheck:
    text = RESULT_DOC.read_text(encoding="utf-8") if RESULT_DOC.exists() else ""
    ok = (
        "PRODUCTION_KNOWLEDGE_SMOKE_AFTER_STUDY_DOCS_STATUS=PASSED" in text
        or "PRODUCTION_KNOWLEDGE_SMOKE_AFTER_STUDY_DOCS_STATUS=FAILED_NEEDS_REVIEW" in text
    )
    return Phase8WCheck("Smoke status recorded", ok)


def safety_flags_recorded() -> Phase8WCheck:
    text = RESULT_DOC.read_text(encoding="utf-8").lower() if RESULT_DOC.exists() else ""
    required = [
        "contact-flow test run: `false`",
        "contact details sent: `false`",
        "intentional production leads/tasks/customers created: `false`",
    ]
    missing = [item for item in required if item not in text]
    return Phase8WCheck("No-contact safety flags recorded", not missing, ", ".join(missing))


def decision_state_documented() -> Phase8WCheck:
    text = read_docs([DEPLOYMENT_DOCS / "PRODUCTION_READINESS_DECISION.md", DEPLOYMENT_DOCS / "FINAL_PREFLIGHT_GATE.md", NEXT_PHASES, README])
    return Phase8WCheck("Phase 8W decision state documented", PASSED_STATE in text or FAILED_STATE in text)


def public_launch_not_complete() -> Phase8WCheck:
    text = read_docs().lower()
    bad_phrases = [
        "public launch complete",
        "full production launch complete",
        "actual site embed completed",
    ]
    findings = [phrase for phrase in bad_phrases if phrase in text]
    return Phase8WCheck("Public launch not marked complete", not findings, ", ".join(findings))


def no_forbidden_patterns(paths: list[Path] | None = None) -> Phase8WCheck:
    findings: list[str] = []
    for path in paths or DOC_FILES:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return Phase8WCheck("No forbidden secret patterns", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> Phase8WCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Phase8WCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked(project_root: Path = PROJECT_ROOT) -> Phase8WCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Phase8WCheck(
        ".local-secrets and generated secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks() -> list[Phase8WCheck]:
    return [
        *required_files_exist(),
        import_summary_recorded(),
        smoke_status_recorded(),
        safety_flags_recorded(),
        decision_state_documented(),
        public_launch_not_complete(),
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
