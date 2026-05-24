from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
EVIDENCE_HTML = PROJECT_ROOT / "docs" / "knowledge_evidence" / "uploaded_widget_ui" / "alte_university_ai_chatbot.html"
SAFE_WIDGET = PROJECT_ROOT / "widget" / "alte-university-ai-chatbot-safe.html"
UI_REVIEW_DOC = PROJECT_ROOT / "docs" / "deployment" / "UPLOADED_WIDGET_UI_REVIEW.md"
INTEGRATION_DOC = PROJECT_ROOT / "docs" / "deployment" / "SAFE_UPLOADED_WIDGET_UI_INTEGRATION.md"
README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
WIDGET_README = PROJECT_ROOT / "widget" / "README.md"
TRANSFER_DOC = PROJECT_ROOT / "docs" / "deployment" / "WIDGET_TRANSFER_TO_ALTE_SITE.md"
EMBED_DOC = PROJECT_ROOT / "docs" / "deployment" / "WEBSITE_WIDGET_PRODUCTION_EMBED.md"
SMOKE_DOC = PROJECT_ROOT / "docs" / "deployment" / "STANDALONE_WIDGET_SMOKE_CHECKLIST.md"

PRODUCTION_BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
DECISION_STATE = "BACKEND_DEPLOYED_FULL_LOCAL_KB_IMPORTED_SAFE_WIDGET_UI_READY_PENDING_REVIEW_AND_SITE_EMBED"
DOCS = [UI_REVIEW_DOC, INTEGRATION_DOC, README, NEXT_PHASES, WIDGET_README, TRANSFER_DOC, EMBED_DOC, SMOKE_DOC]

SECRET_PATTERNS = [
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
    re.compile(r"DB_PASSWORD\s*=", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]
SAFE_WIDGET_FORBIDDEN = [
    re.compile(r"api\.anthropic\.com", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile(r"\bconst\s+SYS\b", re.IGNORECASE),
    re.compile(r"\bsystem\s*:\s*SYS\b", re.IGNORECASE),
    re.compile(r"https://api\.anthropic\.com/v1/messages", re.IGNORECASE),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def required_files_exist() -> list[Check]:
    required = [EVIDENCE_HTML, SAFE_WIDGET, UI_REVIEW_DOC, INTEGRATION_DOC]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in required]


def safe_widget_has_required_backend_wiring() -> Check:
    if not SAFE_WIDGET.exists():
        return Check("Safe widget backend wiring", False, "missing safe widget")
    text = SAFE_WIDGET.read_text(encoding="utf-8")
    required = [
        "/chat/session/start",
        "/chat/message",
        PRODUCTION_BACKEND_URL,
        "sourceDomain",
        "localStorage",
    ]
    missing = [item for item in required if item not in text]
    return Check("Safe widget uses backend chat endpoints and session storage", not missing, ", ".join(missing))


def safe_widget_has_no_forbidden_frontend_ai() -> Check:
    if not SAFE_WIDGET.exists():
        return Check("Safe widget has no direct browser AI call", False, "missing safe widget")
    text = SAFE_WIDGET.read_text(encoding="utf-8")
    findings = [pattern.pattern for pattern in SAFE_WIDGET_FORBIDDEN if pattern.search(text)]
    return Check("Safe widget has no direct Anthropic/API-key/system-prompt browser call", not findings, ", ".join(findings))


def docs_record_safe_architecture() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8") for path in [UI_REVIEW_DOC, INTEGRATION_DOC] if path.exists())
    required = [
        "direct browser Anthropic calls are forbidden",
        "browser widget -> FastAPI backend -> Claude -> Knowledge Base -> CRM business rules",
    ]
    missing = [item for item in required if item not in text]
    return Check("Docs record forbidden browser Anthropic calls and safe backend architecture", not missing, ", ".join(missing))


def decision_state_documented() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8") for path in DOCS if path.exists())
    return Check("Phase 8Z decision state documented", DECISION_STATE in text)


def public_launch_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in DOCS if path.exists())
    bad = [phrase for phrase in ["public launch complete", "full production launch complete", "actual site embed completed"] if phrase in text]
    return Check("Public launch not marked complete", not bad, ", ".join(bad))


def no_forbidden_patterns() -> Check:
    findings: list[str] = []
    for path in [SAFE_WIDGET, *DOCS]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return Check("No forbidden secret patterns in safe widget/docs", not findings, ", ".join(findings))


def env_not_tracked() -> Check:
    result = subprocess.run(["git", "ls-files", ".env", "backend/.env"], cwd=PROJECT_ROOT, capture_output=True, text=True)
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked() -> Check:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".local-secrets not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def run_checks() -> list[Check]:
    return [
        *required_files_exist(),
        safe_widget_has_required_backend_wiring(),
        safe_widget_has_no_forbidden_frontend_ai(),
        docs_record_safe_architecture(),
        decision_state_documented(),
        public_launch_not_complete(),
        no_forbidden_patterns(),
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
