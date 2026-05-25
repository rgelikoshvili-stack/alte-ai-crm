from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9K_SECURITY_RELIABILITY_FIXES_RESULT.md"
ARCHIVE_NOTE = PROJECT_ROOT / "docs" / "knowledge_evidence" / "uploaded_widget_ui" / "ARCHIVE_SECURITY_NOTE.md"
FINAL_GATE_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9J_FINAL_PRE_SITE_EMBED_APPROVAL_GATE.md"
GO_NO_GO_CHECKLIST = PROJECT_ROOT / "docs" / "deployment" / "SITE_EMBED_GO_NO_GO_CHECKLIST.md"
PRIVACY_CHECKLIST = PROJECT_ROOT / "docs" / "deployment" / "PRIVACY_DATA_FINAL_APPROVAL_CHECKLIST.md"
README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
READINESS = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md"
FINAL_PREFLIGHT = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md"
ANSWER_POLICY = PROJECT_ROOT / "docs" / "deployment" / "CHATBOT_PUBLIC_ANSWER_POLICY.md"

AI_FALLBACK_TEST = BACKEND_ROOT / "app" / "tests" / "test_ai_provider_failure_fallback.py"
HANDOVER_TEST = BACKEND_ROOT / "app" / "tests" / "test_handover_endpoint_spam_guard.py"
RBAC_TEST = BACKEND_ROOT / "app" / "tests" / "test_rbac_deny_by_default.py"
PROD_AUTH_TEST = BACKEND_ROOT / "app" / "tests" / "test_production_auth_required_guard.py"

WIDGET = PROJECT_ROOT / "widget" / "alte-university-ai-chatbot-safe-pro.html"
ASSET_HTML = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.html"
ASSET_JS = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js"
PRODUCTION_ASSETS = [WIDGET, ASSET_HTML, ASSET_JS]

STATUS = "PHASE_9K_SECURITY_RELIABILITY_STATUS=CODE_FIXED_PENDING_REDEPLOY"
DECISION_STATE = "BACKEND_CODE_FIXED_SECURITY_RELIABILITY_PENDING_REDEPLOY"
PRIVACY_PLACEHOLDER = "#privacy-policy-pending"

DOCS = [
    RESULT_DOC,
    FINAL_GATE_DOC,
    GO_NO_GO_CHECKLIST,
    PRIVACY_CHECKLIST,
    README,
    NEXT_PHASES,
    READINESS,
    FINAL_PREFLIGHT,
    ANSWER_POLICY,
]

WIDGET_FORBIDDEN = [
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
        RESULT_DOC,
        ARCHIVE_NOTE,
        AI_FALLBACK_TEST,
        HANDOVER_TEST,
        RBAC_TEST,
        PROD_AUTH_TEST,
        *PRODUCTION_ASSETS,
    ]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in files]


def result_status_recorded() -> Check:
    text = read(RESULT_DOC)
    return Check("Phase 9K result status recorded", STATUS in text, STATUS)


def docs_record_decision_state() -> Check:
    text = "\n".join(read(path) for path in DOCS)
    return Check("Phase 9K decision state documented", DECISION_STATE in text, DECISION_STATE)


def privacy_placeholder_launch_blocker_recorded() -> Check:
    widget_has_placeholder = PRIVACY_PLACEHOLDER in read(WIDGET) or PRIVACY_PLACEHOLDER in read(ASSET_HTML)
    docs_text = "\n".join(read(path).lower() for path in [RESULT_DOC, PRIVACY_CHECKLIST, GO_NO_GO_CHECKLIST, README])
    docs_block = PRIVACY_PLACEHOLDER.lower() in docs_text and "launch blocker" in docs_text and "not_complete" in docs_text
    return Check("Privacy placeholder remains a launch blocker", widget_has_placeholder and docs_block)


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
        for pattern in WIDGET_FORBIDDEN:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return Check("Production widget/dist assets contain no forbidden secrets or direct provider calls", not findings, ", ".join(findings))


def env_not_tracked() -> Check:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
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


def archive_note_marks_evidence_non_production() -> Check:
    text = read(ARCHIVE_NOTE)
    required = ["historical evidence/reference only", "not production assets", "api.anthropic.com", "Production assets must not contain"]
    missing = [item for item in required if item not in text]
    return Check("Archive security note marks uploaded widget UI as non-production", not missing, ", ".join(missing))


def run_checks() -> list[Check]:
    return [
        *required_files_exist(),
        result_status_recorded(),
        docs_record_decision_state(),
        privacy_placeholder_launch_blocker_recorded(),
        public_launch_not_marked_complete(),
        actual_embed_not_marked_complete(),
        archive_note_marks_evidence_non_production(),
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
