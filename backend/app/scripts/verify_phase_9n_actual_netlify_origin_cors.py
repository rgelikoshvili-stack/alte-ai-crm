from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_ACTUAL_NETLIFY_ORIGIN_CORS_RESULT.md"
HOSTED_SMOKE = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_HOSTED_BROWSER_SMOKE_RESULT.md"
CORS_SMOKE_SCRIPT = BACKEND_ROOT / "app" / "scripts" / "production_test_origin_cors_smoke.py"
TEST_SITE_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"

README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
READINESS = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md"
FINAL_PREFLIGHT = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"

ACTUAL_ORIGIN = "https://nimble-croissant-2f66e8.netlify.app"
STATUS = "PHASE_9N_ACTUAL_NETLIFY_ORIGIN_CORS_STATUS=READY_PENDING_MANUAL_BROWSER_RETEST"
HOSTED_STATUS = "HOSTED_BROWSER_SMOKE_STATUS=CORS_READY_PENDING_MANUAL_BROWSER_RETEST"
PAYLOAD_FIX_HOSTED_STATUS = "HOSTED_BROWSER_SMOKE_STATUS=PENDING_REDEPLOY_AND_MANUAL_RETEST"
DECISION_STATE = "BACKEND_DEPLOYED_ACTUAL_NETLIFY_ORIGIN_CORS_READY_PENDING_BROWSER_RETEST"
PAYLOAD_FIX_DECISION_STATE = "BACKEND_DEPLOYED_TEST_WIDGET_SESSION_PAYLOAD_FIX_READY_PENDING_NETLIFY_REDEPLOY"

DOCS = [RESULT_DOC, HOSTED_SMOKE, README, NEXT_PHASES, READINESS, FINAL_PREFLIGHT, PUBLIC_LAUNCH]

FORBIDDEN_PATTERNS = [
    re.compile(r"api\.anthropic\.com", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile(r"DATABASE_URL\s*=", re.IGNORECASE),
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


def result_doc_exists() -> Check:
    return Check("Actual Netlify CORS result doc exists", RESULT_DOC.exists(), str(RESULT_DOC))


def result_records_status() -> Check:
    text = read(RESULT_DOC)
    return Check("Result records actual origin and status", ACTUAL_ORIGIN in text and STATUS in text)


def hosted_smoke_pending() -> Check:
    text = read(HOSTED_SMOKE)
    return Check("Hosted browser smoke pending retest", HOSTED_STATUS in text or PAYLOAD_FIX_HOSTED_STATUS in text)


def docs_record_decision_state() -> Check:
    text = "\n".join(read(path) for path in DOCS)
    return Check("Docs record actual Netlify CORS decision state", DECISION_STATE in text or PAYLOAD_FIX_DECISION_STATE in text)


def cors_smoke_script_contains_origin() -> Check:
    text = read(CORS_SMOKE_SCRIPT)
    return Check("CORS smoke script contains actual Netlify origin", ACTUAL_ORIGIN in text)


def hosted_browser_smoke_not_passed() -> Check:
    text = "\n".join(read(path).lower() for path in DOCS)
    bad = [
        phrase
        for phrase in [
            "hosted_browser_smoke_status=passed",
            "hosted browser smoke: passed",
            "browser smoke passed: yes",
        ]
        if phrase in text
    ]
    return Check("Hosted browser smoke not marked passed", not bad, ", ".join(bad))


def public_launch_not_complete() -> Check:
    text = "\n".join(read(path).lower() for path in DOCS)
    bad = [
        phrase
        for phrase in [
            "public launch complete",
            "full production launch complete",
            "public launch: complete",
            "public_launch_decision=go",
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


def test_site_js_is_safe() -> Check:
    text = read(TEST_SITE_JS)
    findings = [pattern.pattern for pattern in FORBIDDEN_PATTERNS[:3] if pattern.search(text)]
    return Check("Test-site JS contains no direct provider/key patterns", not findings, ", ".join(findings))


def no_secret_patterns() -> Check:
    findings: list[str] = []
    scan_paths = [RESULT_DOC, HOSTED_SMOKE, CORS_SMOKE_SCRIPT, TEST_SITE_JS]
    for path in scan_paths:
        text = read(path)
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return Check("Docs/scripts contain no forbidden secret patterns", not findings, ", ".join(findings))


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
        result_doc_exists(),
        result_records_status(),
        hosted_smoke_pending(),
        docs_record_decision_state(),
        cors_smoke_script_contains_origin(),
        hosted_browser_smoke_not_passed(),
        public_launch_not_complete(),
        actual_alte_embed_not_complete(),
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
