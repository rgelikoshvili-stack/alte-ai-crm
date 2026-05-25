from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

SMOKE_SCRIPT = BACKEND_ROOT / "app" / "scripts" / "production_security_reliability_smoke.py"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9K_REDEPLOY_SECURITY_RELIABILITY_RESULT.md"
README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
READINESS = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md"
FINAL_PREFLIGHT = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md"
FIXES_RESULT = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9K_SECURITY_RELIABILITY_FIXES_RESULT.md"
FINAL_GATE = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9J_FINAL_PRE_SITE_EMBED_APPROVAL_GATE.md"

WIDGET = PROJECT_ROOT / "widget" / "alte-university-ai-chatbot-safe-pro.html"
ASSET_HTML = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.html"
ASSET_JS = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js"
PRODUCTION_ASSETS = [WIDGET, ASSET_HTML, ASSET_JS]

IMAGE_TAG = "v0.9-security-reliability-fixes"
PASSED_STATUS = "PHASE_9K_REDEPLOY_STATUS=PASSED_SECURITY_RELIABILITY_VERIFIED"
FAILED_STATUS = "PHASE_9K_REDEPLOY_STATUS=FAILED_SECURITY_RELIABILITY_NEEDS_REVIEW"
PASSED_DECISION = "BACKEND_DEPLOYED_SECURITY_RELIABILITY_VERIFIED_PENDING_FINAL_APPROVALS_AND_SITE_EMBED"
FAILED_DECISION = "BACKEND_DEPLOYED_SECURITY_RELIABILITY_FAILED_NEEDS_REVIEW"

DOCS = [RESULT_DOC, README, NEXT_PHASES, READINESS, FINAL_PREFLIGHT, FIXES_RESULT, FINAL_GATE]

FORBIDDEN_ASSET_PATTERNS = [
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
    files = [SMOKE_SCRIPT, RESULT_DOC, *PRODUCTION_ASSETS]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in files]


def result_records_required_fields() -> list[Check]:
    text = read(RESULT_DOC)
    required = [
        IMAGE_TAG,
        "/health",
        "/version",
        "/diagnostics/ai",
        "/dashboard/overview",
        "AUTH_REQUIRED=true",
        "handover spam guard",
        "AI provider failure fallback",
        "code/test verified",
        "no contact details sent: true",
        "contact-flow test run: false",
        "intentional lead/task/customer creation: no",
    ]
    return [Check(f"Result records: {item}", item in text, item) for item in required]


def result_records_status() -> Check:
    text = read(RESULT_DOC)
    return Check("Redeploy result records pass/fail status", PASSED_STATUS in text or FAILED_STATUS in text)


def docs_record_decision_state() -> Check:
    text = "\n".join(read(path) for path in DOCS)
    return Check("Docs record redeploy decision state", PASSED_DECISION in text or FAILED_DECISION in text)


def public_launch_not_marked_complete() -> Check:
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


def actual_embed_not_marked_complete() -> Check:
    text = "\n".join(read(path).lower() for path in DOCS)
    bad = [
        phrase
        for phrase in [
            "actual site embed completed",
            "actual site embed executed: yes",
            "actual site embed: complete",
            "actual embed complete: yes",
            "site embed complete: yes",
        ]
        if phrase in text
    ]
    return Check("Actual embed not marked complete", not bad, ", ".join(bad))


def production_assets_are_safe() -> Check:
    findings: list[str] = []
    for path in PRODUCTION_ASSETS:
        text = read(path)
        for pattern in FORBIDDEN_ASSET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return Check("Production widget/dist assets contain no forbidden patterns", not findings, ", ".join(findings))


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
        *result_records_required_fields(),
        result_records_status(),
        docs_record_decision_state(),
        public_launch_not_marked_complete(),
        actual_embed_not_marked_complete(),
        production_assets_are_safe(),
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
