from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

CORS_SMOKE_SCRIPT = BACKEND_ROOT / "app" / "scripts" / "production_test_origin_cors_smoke.py"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_CORS_TEST_ORIGIN_EXECUTION_RESULT.md"

README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
READINESS = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md"
FINAL_PREFLIGHT = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
HOSTED_SMOKE = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_HOSTED_BROWSER_SMOKE_RESULT.md"
PLAN_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_CORS_TEST_ORIGIN_PLAN.md"
TEMP_CORS_PLAN = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_TEMP_CORS_UPDATE_PLAN.md"

TEST_SITE_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
TEST_ORIGIN = "https://alte-ai-chat-test.netlify.app"

DOCS = [RESULT_DOC, README, NEXT_PHASES, READINESS, FINAL_PREFLIGHT, PUBLIC_LAUNCH, HOSTED_SMOKE, PLAN_DOC, TEMP_CORS_PLAN]

FORBIDDEN_TEST_SITE_PATTERNS = [
    re.compile(r"api\.anthropic\.com", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant-", re.IGNORECASE),
]

SECRET_PATTERNS = [
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant-", re.IGNORECASE),
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
    files = [CORS_SMOKE_SCRIPT, RESULT_DOC]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in files]


def result_records_required_status() -> list[Check]:
    text = read(RESULT_DOC)
    return [
        Check("Result records test origin URL", TEST_ORIGIN in text),
        Check(
            "Result records execution status",
            "TEMP_TEST_ORIGIN_CORS_READY_PENDING_BROWSER_SMOKE" in text
            or "TEMP_TEST_ORIGIN_BROWSER_SMOKE_PASSED" in text,
        ),
    ]


def docs_record_decision_state() -> Check:
    text = "\n".join(read(path) for path in DOCS)
    return Check(
        "Docs record execution decision state",
        "BACKEND_DEPLOYED_TEST_ORIGIN_CORS_READY_PENDING_BROWSER_SMOKE" in text
        or "BACKEND_DEPLOYED_HOSTED_TEST_ORIGIN_BROWSER_SMOKE_PASSED_PENDING_ALTE_SITE_EMBED" in text,
    )


def real_alte_embed_not_complete() -> Check:
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
    return Check("Real Alte site embed not marked complete", not bad, ", ".join(bad))


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


def real_alte_smoke_not_passed() -> Check:
    text = "\n".join(read(path).lower() for path in DOCS)
    bad = [
        phrase
        for phrase in [
            "real_domain_smoke_status=passed",
            "real alte smoke passed",
            "real-domain smoke: passed",
        ]
        if phrase in text
    ]
    return Check("Real Alte smoke not marked passed", not bad, ", ".join(bad))


def test_site_js_is_safe() -> Check:
    text = read(TEST_SITE_JS)
    findings = [pattern.pattern for pattern in FORBIDDEN_TEST_SITE_PATTERNS if pattern.search(text)]
    return Check("Test site JS contains no direct provider/key patterns", not findings, ", ".join(findings))


def no_secret_patterns() -> Check:
    findings: list[str] = []
    for path in [RESULT_DOC, CORS_SMOKE_SCRIPT, TEST_SITE_JS]:
        text = read(path)
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return Check("Execution docs/scripts contain no secret patterns", not findings, ", ".join(findings))


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
        *result_records_required_status(),
        docs_record_decision_state(),
        real_alte_embed_not_complete(),
        public_launch_not_complete(),
        real_alte_smoke_not_passed(),
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
