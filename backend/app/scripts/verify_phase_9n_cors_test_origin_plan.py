from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

PLAN_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_CORS_TEST_ORIGIN_PLAN.md"
HOSTING_PACKAGE = PROJECT_ROOT / "docs" / "test_origin_handoff" / "TEST_ORIGIN_HOSTING_PACKAGE_GEO.md"
BROWSER_CHECKLIST_GEO = PROJECT_ROOT / "docs" / "test_origin_handoff" / "TEST_ORIGIN_BROWSER_SMOKE_CHECKLIST_GEO.md"
NETLIFY_DEPLOY_FIX_GEO = PROJECT_ROOT / "docs" / "test_origin_handoff" / "NETLIFY_DEPLOY_FIX_GEO.md"
CORS_UPDATE_PLAN = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_TEMP_CORS_UPDATE_PLAN.md"
CORS_SCRIPT = PROJECT_ROOT / "scripts" / "phase_9n_update_cors_for_test_origin.ps1"
HOSTED_SMOKE_RESULT = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_HOSTED_BROWSER_SMOKE_RESULT.md"

README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
READINESS = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md"
FINAL_PREFLIGHT = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md"
TEST_SITE_RESULT = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_TEST_SITE_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"

TEST_SITE_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"

DECISION_STATE = "BACKEND_DEPLOYED_TEST_ORIGIN_PLAN_READY_PENDING_TEST_URL_AND_CORS_APPROVAL"

DOCS = [
    PLAN_DOC,
    HOSTING_PACKAGE,
    BROWSER_CHECKLIST_GEO,
    NETLIFY_DEPLOY_FIX_GEO,
    CORS_UPDATE_PLAN,
    HOSTED_SMOKE_RESULT,
    README,
    NEXT_PHASES,
    READINESS,
    FINAL_PREFLIGHT,
    TEST_SITE_RESULT,
    PUBLIC_LAUNCH,
]

SECRET_PATTERNS = [
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile(r"DATABASE_URL", re.IGNORECASE),
    re.compile(r"DB_PASSWORD", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
]

TEST_SITE_FORBIDDEN = [
    re.compile(r"api\.anthropic\.com", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant-", re.IGNORECASE),
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
        PLAN_DOC,
        HOSTING_PACKAGE,
        BROWSER_CHECKLIST_GEO,
        NETLIFY_DEPLOY_FIX_GEO,
        CORS_UPDATE_PLAN,
        CORS_SCRIPT,
        HOSTED_SMOKE_RESULT,
    ]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in files]


def status_markers_recorded() -> list[Check]:
    plan = read(PLAN_DOC)
    cors_plan = read(CORS_UPDATE_PLAN)
    smoke = read(HOSTED_SMOKE_RESULT)
    return [
        Check(
            "CORS test origin plan status recorded",
            "PHASE_9N_CORS_TEST_ORIGIN_STATUS=PENDING_TEST_ORIGIN_URL" in plan
            or "PHASE_9N_CORS_TEST_ORIGIN_STATUS=APPROVED_PENDING_CORS_UPDATE" in plan,
        ),
        Check(
            "Temporary CORS update status recorded",
            "TEMP_CORS_UPDATE_STATUS=NOT_EXECUTED_PENDING_TEST_ORIGIN" in cors_plan
            or "TEMP_CORS_UPDATE_STATUS=EXECUTED_TEMP_TEST_ORIGIN_READY" in cors_plan,
        ),
        Check(
            "Hosted smoke status recorded",
            "HOSTED_BROWSER_SMOKE_STATUS=NOT_EXECUTED_PENDING_TEST_ORIGIN_AND_CORS" in smoke
            or "HOSTED_BROWSER_SMOKE_STATUS=CORS_READY_PENDING_MANUAL_BROWSER_TEST" in smoke
            or "HOSTED_BROWSER_SMOKE_STATUS=BLOCKED_NETLIFY_TEST_SITE_NOT_DEPLOYED" in smoke
            or "HOSTED_BROWSER_SMOKE_STATUS=BLOCKED_PENDING_NETLIFY_REDEPLOY" in smoke
            or "HOSTED_BROWSER_SMOKE_STATUS=CORS_READY_PENDING_MANUAL_BROWSER_RETEST" in smoke
            or "HOSTED_BROWSER_SMOKE_STATUS=PENDING_REDEPLOY_AND_MANUAL_RETEST" in smoke,
        ),
    ]


def docs_record_decision_state() -> Check:
    text = "\n".join(read(path) for path in DOCS)
    return Check(
        "Docs record Phase 9N-CORS decision state",
        DECISION_STATE in text
        or "BACKEND_DEPLOYED_TEST_ORIGIN_CORS_READY_PENDING_BROWSER_SMOKE" in text
        or "BACKEND_DEPLOYED_NETLIFY_TEST_PACKAGE_READY_PENDING_REDEPLOY_AND_BROWSER_SMOKE" in text
        or "BACKEND_DEPLOYED_ACTUAL_NETLIFY_ORIGIN_CORS_READY_PENDING_BROWSER_RETEST" in text
        or "BACKEND_DEPLOYED_TEST_WIDGET_SESSION_PAYLOAD_FIX_READY_PENDING_NETLIFY_REDEPLOY" in text,
    )


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
            "actual site embed completed",
            "actual site embed executed: yes",
            "actual embed complete: yes",
        ]
        if phrase in text
    ]
    return Check("Actual Alte embed not marked complete", not bad, ", ".join(bad))


def hosted_browser_smoke_not_passed() -> Check:
    text = read(HOSTED_SMOKE_RESULT).lower()
    bad = [
        phrase
        for phrase in [
            "hosted_browser_smoke_status=passed",
            "hosted browser smoke: passed",
        ]
        if phrase in text
    ]
    return Check("Hosted browser smoke not marked passed", not bad, ", ".join(bad))


def test_site_js_is_safe() -> Check:
    text = read(TEST_SITE_JS)
    findings = [pattern.pattern for pattern in TEST_SITE_FORBIDDEN if pattern.search(text)]
    return Check("Test site JS contains no direct provider/key patterns", not findings, ", ".join(findings))


def no_secret_patterns() -> Check:
    findings: list[str] = []
    scan_paths = [
        PLAN_DOC,
        HOSTING_PACKAGE,
        BROWSER_CHECKLIST_GEO,
        NETLIFY_DEPLOY_FIX_GEO,
        CORS_UPDATE_PLAN,
        HOSTED_SMOKE_RESULT,
        CORS_SCRIPT,
        TEST_SITE_JS,
    ]
    for path in scan_paths:
        text = read(path)
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return Check("Docs/script/test JS contain no secret patterns", not findings, ", ".join(findings))


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
        *status_markers_recorded(),
        docs_record_decision_state(),
        public_launch_not_complete(),
        actual_alte_embed_not_complete(),
        hosted_browser_smoke_not_passed(),
        test_site_js_is_safe(),
        no_secret_patterns(),
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
