from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

TEST_INDEX = PROJECT_ROOT / "test_site" / "index.html"
TEST_JOIN = PROJECT_ROOT / "test_site" / "join.html"
TEST_WIDGET_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
TEST_README = PROJECT_ROOT / "test_site" / "README_GEO.md"

DECISION_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_TEST_SITE_DECISION.md"
CORS_PLAN = PROJECT_ROOT / "docs" / "deployment" / "OPTIONAL_TEST_ORIGIN_CORS_PLAN.md"
BROWSER_CHECKLIST = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_TEST_SITE_BROWSER_SMOKE_CHECKLIST.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_TEST_SITE_RESULT.md"
SMOKE_SCRIPT = BACKEND_ROOT / "app" / "scripts" / "test_site_api_smoke.py"

README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
READINESS = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md"
FINAL_PREFLIGHT = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
SITE_EMBED_DECISION = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_ACTUAL_SITE_EMBED_DECISION.md"
SMOKE_GUIDE = PROJECT_ROOT / "docs" / "deployment" / "REAL_DOMAIN_BROWSER_SMOKE_EXECUTION_GUIDE.md"

PRODUCTION_BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
PASSED_STATUS = "LOCAL_TEST_PACKAGE_READY_API_SMOKE_PASSED_PENDING_BROWSER_ORIGIN"
FAILED_STATUS = "LOCAL_TEST_PACKAGE_READY_API_SMOKE_FAILED_NEEDS_REVIEW"
PASSED_DECISION = "BACKEND_DEPLOYED_TEST_SITE_PACKAGE_READY_PENDING_BROWSER_TEST_ORIGIN_AND_SITE_EMBED"
FAILED_DECISION = "BACKEND_DEPLOYED_TEST_SITE_API_SMOKE_FAILED_NEEDS_REVIEW"

DOCS = [
    DECISION_DOC,
    CORS_PLAN,
    BROWSER_CHECKLIST,
    RESULT_DOC,
    README,
    NEXT_PHASES,
    READINESS,
    FINAL_PREFLIGHT,
    PUBLIC_LAUNCH,
    SITE_EMBED_DECISION,
    SMOKE_GUIDE,
]

SCAN_FILES = [TEST_INDEX, TEST_JOIN, TEST_WIDGET_JS, TEST_README, DECISION_DOC, CORS_PLAN, BROWSER_CHECKLIST, RESULT_DOC]

FORBIDDEN_PATTERNS = [
    re.compile(r"api\.anthropic\.com", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile(r"DATABASE_URL", re.IGNORECASE),
    re.compile(r"DB_PASSWORD", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def required_files_exist() -> list[Check]:
    files = [
        TEST_INDEX,
        TEST_JOIN,
        TEST_WIDGET_JS,
        TEST_README,
        DECISION_DOC,
        CORS_PLAN,
        BROWSER_CHECKLIST,
        RESULT_DOC,
        SMOKE_SCRIPT,
    ]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in files]


def test_site_assets_are_safe() -> Check:
    findings: list[str] = []
    for path in [TEST_INDEX, TEST_JOIN, TEST_WIDGET_JS]:
        text = read(path)
        for pattern in FORBIDDEN_PATTERNS[:3]:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return Check("Test site assets contain no direct provider/key patterns", not findings, ", ".join(findings))


def test_site_config_is_present() -> Check:
    text = "\n".join(read(path) for path in [TEST_INDEX, TEST_JOIN, TEST_WIDGET_JS])
    required = [
        PRODUCTION_BACKEND_URL,
        'sourceDomain: "alte.edu.ge"',
        'sourceDomain: "join.alte.edu.ge"',
        'mode: "test_site"',
    ]
    missing = [item for item in required if item not in text]
    return Check("Test site config contains backend and source domains", not missing, ", ".join(missing))


def result_status_recorded() -> Check:
    text = read(RESULT_DOC)
    return Check("Result records pass/fail status", PASSED_STATUS in text or FAILED_STATUS in text)


def docs_record_decision_state() -> Check:
    text = "\n".join(read(path) for path in DOCS)
    return Check("Docs record test-site decision state", PASSED_DECISION in text or FAILED_DECISION in text)


def public_launch_not_complete() -> Check:
    text = "\n".join(read(path).lower() for path in DOCS)
    bad = [
        phrase
        for phrase in [
            "public launch complete",
            "full production launch complete",
            "public launch: complete",
            "public launch approval granted: yes",
        ]
        if phrase in text
    ]
    return Check("Public launch not marked complete", not bad, ", ".join(bad))


def actual_alte_embed_not_complete() -> Check:
    text = "\n".join(read(path).lower() for path in DOCS)
    bad = [
        phrase
        for phrase in [
            "actual alte embed complete",
            "actual alte embed: complete",
            "actual site embed completed",
            "actual site embed executed: yes",
            "actual embed complete: yes",
        ]
        if phrase in text
    ]
    return Check("Actual Alte embed not marked complete", not bad, ", ".join(bad))


def no_forbidden_secret_patterns() -> Check:
    findings: list[str] = []
    secret_patterns = FORBIDDEN_PATTERNS[1:]
    for path in SCAN_FILES:
        text = read(path)
        for pattern in secret_patterns:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return Check("Test-site package/docs contain no forbidden secret patterns", not findings, ", ".join(findings))


def env_not_tracked() -> Check:
    result = subprocess.run(["git", "ls-files", ".env", "backend/.env"], cwd=PROJECT_ROOT, capture_output=True, text=True, check=False)
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked() -> Check:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "backend/.local-secrets", "secret-values.local.txt", "secret-values.local.*"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".local-secrets are not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def run_checks() -> list[Check]:
    return [
        *required_files_exist(),
        test_site_assets_are_safe(),
        test_site_config_is_present(),
        result_status_recorded(),
        docs_record_decision_state(),
        public_launch_not_complete(),
        actual_alte_embed_not_complete(),
        no_forbidden_secret_patterns(),
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
