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
WIDGET_ROOT = PROJECT_ROOT / "widget"

DECISION_STATE = "BACKEND_DEPLOYED_STANDALONE_WIDGET_API_SMOKE_PASSED_PENDING_REAL_DOMAIN_SMOKE"
LOCALHOST_DECISION = "LOCALHOST_CORS_NOT_APPROVED_FOR_PRODUCTION"

SECRET_PATTERNS = [
    re.compile(r"sk-ant-", re.IGNORECASE),
    re.compile(r"DATABASE_URL", re.IGNORECASE),
    re.compile(r"DB_PASSWORD", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]


@dataclass
class CorsDecisionCheck:
    name: str
    passed: bool
    detail: str = ""


REQUIRED_FILES = [
    DEPLOYMENT_DOCS / "CORS_LOCALHOST_TEST_DECISION.md",
    DEPLOYMENT_DOCS / "STANDALONE_WIDGET_SMOKE_CHECKLIST.md",
    DEPLOYMENT_DOCS / "PRODUCTION_WIDGET_SMOKE_CHECKLIST.md",
]


SECRET_SCAN_FILES = REQUIRED_FILES + [
    WIDGET_ROOT / "STANDALONE_PRODUCTION_DEMO.md",
]


def _read(paths: list[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


def required_files_exist() -> list[CorsDecisionCheck]:
    return [CorsDecisionCheck(f"{path.name} exists", path.exists(), str(path)) for path in REQUIRED_FILES]


def cors_decision_doc_valid() -> CorsDecisionCheck:
    text = (DEPLOYMENT_DOCS / "CORS_LOCALHOST_TEST_DECISION.md").read_text(encoding="utf-8")
    required = [
        "Do not add localhost to production CORS by default",
        "https://alte.edu.ge",
        "https://join.alte.edu.ge",
        "real production domain `https://alte.edu.ge` CORS preflight: PASS",
        "real production domain `https://join.alte.edu.ge` CORS preflight: PASS",
        "http://127.0.0.1:5500",
        "blocked by CORS",
        LOCALHOST_DECISION,
    ]
    normalized = text.lower()
    missing = [item for item in required if item.lower() not in normalized]
    return CorsDecisionCheck("CORS localhost decision is documented", not missing, ", ".join(missing))


def smoke_results_documented() -> CorsDecisionCheck:
    text = _read(
        [
            DEPLOYMENT_DOCS / "STANDALONE_WIDGET_SMOKE_CHECKLIST.md",
            DEPLOYMENT_DOCS / "PRODUCTION_WIDGET_SMOKE_CHECKLIST.md",
            WIDGET_ROOT / "STANDALONE_PRODUCTION_DEMO.md",
        ]
    )
    required = [
        "alte.edu.ge` CORS preflight PASS",
        "join.alte.edu.ge` CORS preflight PASS",
        "localhost browser CORS",
        "blocked as expected",
        "backend API smoke",
        "Claude enabled",
    ]
    normalized = text.lower()
    missing = [item for item in required if item.lower() not in normalized]
    return CorsDecisionCheck("Standalone smoke results are documented", not missing, ", ".join(missing))


def decision_state_documented() -> CorsDecisionCheck:
    text = _read(
        [
            DEPLOYMENT_DOCS / "PRODUCTION_READINESS_DECISION.md",
            DEPLOYMENT_DOCS / "FINAL_PREFLIGHT_GATE.md",
            README,
            NEXT_PHASES,
            WIDGET_ROOT / "STANDALONE_PRODUCTION_DEMO.md",
        ]
    )
    forbidden = [
        "FULL_PRODUCTION_LAUNCH_COMPLETE",
        "WEBSITE_WIDGET_EMBED_COMPLETED",
        "WEBSITE_PRIVACY_APPROVED_FOR_WIDGET_EMBED",
    ]
    findings = [item for item in forbidden if item in text]
    return CorsDecisionCheck(
        "Decision state remains pending real-domain smoke",
        DECISION_STATE in text and not findings,
        ", ".join(findings),
    )


def no_forbidden_patterns(paths: list[Path] | None = None) -> CorsDecisionCheck:
    paths = paths or SECRET_SCAN_FILES
    findings: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return CorsDecisionCheck("No forbidden secret patterns", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> CorsDecisionCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return CorsDecisionCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked(project_root: Path = PROJECT_ROOT) -> CorsDecisionCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return CorsDecisionCheck(
        ".local-secrets and generated secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks() -> list[CorsDecisionCheck]:
    return [
        *required_files_exist(),
        cors_decision_doc_valid(),
        smoke_results_documented(),
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
