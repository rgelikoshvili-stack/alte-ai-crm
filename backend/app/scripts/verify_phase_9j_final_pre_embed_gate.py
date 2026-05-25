from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

FINAL_GATE_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9J_FINAL_PRE_SITE_EMBED_APPROVAL_GATE.md"
APPROVAL_RECORD = PROJECT_ROOT / "docs" / "deployment" / "SITE_EMBED_FINAL_APPROVAL_RECORD.md"
GO_NO_GO_CHECKLIST = PROJECT_ROOT / "docs" / "deployment" / "SITE_EMBED_GO_NO_GO_CHECKLIST.md"

ASSET_HTML = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.html"
ASSET_JS = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js"
WIDGET = PROJECT_ROOT / "widget" / "alte-university-ai-chatbot-safe-pro.html"
ALTE_SNIPPET = PROJECT_ROOT / "docs" / "embed_package" / "alte_safe_pro_sidebar_embed_snippet.html"
JOIN_SNIPPET = PROJECT_ROOT / "docs" / "embed_package" / "join_alte_safe_pro_sidebar_embed_snippet.html"

README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
READINESS = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md"
FINAL_PREFLIGHT = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md"
PRE_EMBED_GATE = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PRE_EMBED_APPROVAL_GATE.md"
ASSET_DECISION = PROJECT_ROOT / "docs" / "deployment" / "FINAL_WIDGET_ASSET_URL_DECISION.md"
EMBED_RUNBOOK = PROJECT_ROOT / "docs" / "deployment" / "ACTUAL_SITE_EMBED_RUNBOOK.md"
ANSWER_POLICY = PROJECT_ROOT / "docs" / "deployment" / "CHATBOT_PUBLIC_ANSWER_POLICY.md"
OFFICIAL_REPORT = PROJECT_ROOT / "docs" / "deployment" / "OFFICIAL_CONTENT_REVIEW_REPORT.md"
PRIVACY_CHECKLIST = PROJECT_ROOT / "docs" / "deployment" / "PRIVACY_DATA_FINAL_APPROVAL_CHECKLIST.md"
SMOKE_GUIDE = PROJECT_ROOT / "docs" / "deployment" / "REAL_DOMAIN_BROWSER_SMOKE_EXECUTION_GUIDE.md"
HANDOFF_DOC = PROJECT_ROOT / "docs" / "embed_package" / "WEBSITE_DEVELOPER_HANDOFF_GEO.md"

PLACEHOLDER_URL = "https://alte.edu.ge/assets/alte-ai-chat-widget.js"
BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
FINAL_GATE_STATUS = "PHASE_9J_FINAL_PRE_SITE_EMBED_STATUS=NO_GO_PENDING_FINAL_APPROVALS"
APPROVAL_STATUS = "SITE_EMBED_FINAL_APPROVAL_STATUS=PENDING"
CHECKLIST_STATUS = "SITE_EMBED_GO_NO_GO_STATUS=NO_GO_PENDING_APPROVALS"
DECISION_STATE = "BACKEND_DEPLOYED_FINAL_PRE_EMBED_GATE_READY_NO_GO_PENDING_APPROVALS"

DOCS = [
    FINAL_GATE_DOC,
    APPROVAL_RECORD,
    GO_NO_GO_CHECKLIST,
    README,
    NEXT_PHASES,
    READINESS,
    FINAL_PREFLIGHT,
    PRE_EMBED_GATE,
    ASSET_DECISION,
    EMBED_RUNBOOK,
    ANSWER_POLICY,
    OFFICIAL_REPORT,
    PRIVACY_CHECKLIST,
    SMOKE_GUIDE,
    HANDOFF_DOC,
]

SECRET_PATTERNS = [
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
    re.compile(r"DB_PASSWORD\s*=", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]

WIDGET_FORBIDDEN = [
    re.compile(r"api\.anthropic\.com", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant-", re.IGNORECASE),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def required_files_exist() -> list[Check]:
    files = [
        FINAL_GATE_DOC,
        APPROVAL_RECORD,
        GO_NO_GO_CHECKLIST,
        ASSET_HTML,
        ASSET_JS,
        WIDGET,
        ALTE_SNIPPET,
        JOIN_SNIPPET,
    ]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in files]


def statuses_recorded() -> list[Check]:
    final_gate = FINAL_GATE_DOC.read_text(encoding="utf-8") if FINAL_GATE_DOC.exists() else ""
    approval = APPROVAL_RECORD.read_text(encoding="utf-8") if APPROVAL_RECORD.exists() else ""
    checklist = GO_NO_GO_CHECKLIST.read_text(encoding="utf-8") if GO_NO_GO_CHECKLIST.exists() else ""
    docs_text = "\n".join(path.read_text(encoding="utf-8") for path in DOCS if path.exists())
    return [
        Check("Final pre-site-embed status is NO-GO", FINAL_GATE_STATUS in final_gate),
        Check("Final approval record remains pending", APPROVAL_STATUS in approval),
        Check("GO/NO-GO checklist remains NO-GO", CHECKLIST_STATUS in checklist),
        Check("Phase 9J decision state documented", DECISION_STATE in docs_text),
    ]


def actual_embed_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in DOCS if path.exists())
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
    return Check("Actual site embed not marked complete", not bad, ", ".join(bad))


def public_launch_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in DOCS if path.exists())
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


def privacy_approval_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in DOCS if path.exists())
    bad = [
        phrase
        for phrase in [
            "privacy final approval: approved",
            "privacy approval status: approved",
            "privacy_data_final_approval_status=approved",
            "privacy/data approval completed: yes",
        ]
        if phrase in text
    ]
    return Check("Privacy approval not falsely marked complete", not bad, ", ".join(bad))


def official_content_approval_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in DOCS if path.exists())
    bad = [
        phrase
        for phrase in [
            "official human approval exists: yes",
            "official content approval complete: yes",
            "public content approval: complete",
            "content_approval_status: approved",
        ]
        if phrase in text
    ]
    return Check("Official content approval not falsely marked complete", not bad, ", ".join(bad))


def asset_placeholder_and_snippets_exist() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8") for path in [ASSET_DECISION, ALTE_SNIPPET, JOIN_SNIPPET] if path.exists())
    required = [PLACEHOLDER_URL, BACKEND_URL, 'sourceDomain: "alte.edu.ge"', 'sourceDomain: "join.alte.edu.ge"']
    missing = [item for item in required if item not in text]
    return Check("Final asset placeholder and embed snippets are ready", not missing, ", ".join(missing))


def widget_assets_are_safe() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8") for path in [WIDGET, ASSET_HTML, ASSET_JS] if path.exists())
    required = ["/chat/session/start", "/chat/message"]
    missing = [item for item in required if item not in text]
    forbidden = [pattern.pattern for pattern in WIDGET_FORBIDDEN if pattern.search(text)]
    return Check("Widget assets have backend endpoints and no unsafe browser AI/secrets", not missing and not forbidden, f"missing={missing}; forbidden={forbidden}")


def no_forbidden_patterns() -> Check:
    findings: list[str] = []
    for path in [WIDGET, ASSET_HTML, ASSET_JS, *DOCS]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return Check("No forbidden secret patterns", not findings, ", ".join(findings))


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
        *statuses_recorded(),
        actual_embed_not_complete(),
        public_launch_not_complete(),
        privacy_approval_not_complete(),
        official_content_approval_not_complete(),
        asset_placeholder_and_snippets_exist(),
        widget_assets_are_safe(),
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
