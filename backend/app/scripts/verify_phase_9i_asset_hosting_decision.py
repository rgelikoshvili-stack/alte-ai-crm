from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

ASSET_HTML = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.html"
ASSET_JS = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js"
ASSET_DECISION = PROJECT_ROOT / "docs" / "deployment" / "FINAL_WIDGET_ASSET_URL_DECISION.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9I_ASSET_HOSTING_DECISION_RESULT.md"
ALTE_SNIPPET = PROJECT_ROOT / "docs" / "embed_package" / "alte_safe_pro_sidebar_embed_snippet.html"
JOIN_SNIPPET = PROJECT_ROOT / "docs" / "embed_package" / "join_alte_safe_pro_sidebar_embed_snippet.html"
HANDOFF_DOC = PROJECT_ROOT / "docs" / "embed_package" / "WEBSITE_DEVELOPER_HANDOFF_GEO.md"

README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
READINESS = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md"
FINAL_PREFLIGHT = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md"
FINAL_GATE = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PRE_EMBED_APPROVAL_GATE.md"
EMBED_RUNBOOK = PROJECT_ROOT / "docs" / "deployment" / "ACTUAL_SITE_EMBED_RUNBOOK.md"
SMOKE_GUIDE = PROJECT_ROOT / "docs" / "deployment" / "REAL_DOMAIN_BROWSER_SMOKE_EXECUTION_GUIDE.md"
EMBED_README = PROJECT_ROOT / "docs" / "embed_package" / "EMBED_PACKAGE_README_GEO.md"

PLACEHOLDER_URL = "https://alte.edu.ge/assets/alte-ai-chat-widget.js"
BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
HOSTING_OPTION = "FINAL_WIDGET_ASSET_HOSTING_OPTION=ALTE_CONTROLLED_HOSTING"
ASSET_STATUS = "FINAL_WIDGET_ASSET_URL_STATUS=PENDING_UPLOAD_BY_ALTE_WEBSITE_TEAM"
RESULT_STATUS = "PHASE_9I_ASSET_HOSTING_STATUS=ALTE_CONTROLLED_HOSTING_SELECTED_PENDING_UPLOAD_AND_EMBED"
DECISION_STATE = "BACKEND_DEPLOYED_ASSET_HOSTING_SELECTED_ALTE_CONTROLLED_PENDING_UPLOAD_AND_SITE_EMBED"

DOCS = [
    ASSET_DECISION,
    RESULT_DOC,
    ALTE_SNIPPET,
    JOIN_SNIPPET,
    HANDOFF_DOC,
    README,
    NEXT_PHASES,
    READINESS,
    FINAL_PREFLIGHT,
    FINAL_GATE,
    EMBED_RUNBOOK,
    SMOKE_GUIDE,
    EMBED_README,
]

SECRET_PATTERNS = [
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
    re.compile(r"DB_PASSWORD\s*=", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]

FORBIDDEN_ASSET_PATTERNS = [
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
    files = [ASSET_HTML, ASSET_JS, ASSET_DECISION, RESULT_DOC, ALTE_SNIPPET, JOIN_SNIPPET, HANDOFF_DOC]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in files]


def decision_doc_records_option() -> Check:
    text = ASSET_DECISION.read_text(encoding="utf-8") if ASSET_DECISION.exists() else ""
    required = [HOSTING_OPTION, ASSET_STATUS, PLACEHOLDER_URL]
    missing = [item for item in required if item not in text]
    return Check("Final asset decision records Alte-controlled hosting", not missing, ", ".join(missing))


def result_doc_records_status() -> Check:
    text = RESULT_DOC.read_text(encoding="utf-8") if RESULT_DOC.exists() else ""
    required = [RESULT_STATUS, PLACEHOLDER_URL, "Actual upload executed: NO", "Actual site embed executed: NO"]
    missing = [item for item in required if item not in text]
    return Check("Phase 9I result doc records status and no execution", not missing, ", ".join(missing))


def snippets_use_placeholder() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8") for path in [ALTE_SNIPPET, JOIN_SNIPPET] if path.exists())
    required = [PLACEHOLDER_URL, BACKEND_URL, 'sourceDomain: "alte.edu.ge"', 'sourceDomain: "join.alte.edu.ge"']
    missing = [item for item in required if item not in text]
    return Check("Embed snippets use final placeholder URL and backend config", not missing, ", ".join(missing))


def decision_state_documented() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8") for path in DOCS if path.exists())
    return Check("Phase 9I decision state documented", DECISION_STATE in text)


def actual_upload_embed_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in DOCS if path.exists())
    bad = [
        phrase
        for phrase in [
            "actual upload executed: yes",
            "actual site embed executed: yes",
            "actual site embed completed",
            "actual site embed: complete",
        ]
        if phrase in text
    ]
    return Check("Actual upload/embed not marked complete", not bad, ", ".join(bad))


def public_launch_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in DOCS if path.exists())
    bad = [
        phrase
        for phrase in ["public launch complete", "full production launch complete", "public launch: complete"]
        if phrase in text
    ]
    return Check("Public launch not marked complete", not bad, ", ".join(bad))


def assets_are_safe_and_backend_connected() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8") for path in [ASSET_HTML, ASSET_JS] if path.exists())
    required = ["/chat/session/start", "/chat/message", BACKEND_URL]
    missing = [item for item in required if item not in text]
    forbidden = [pattern.pattern for pattern in FORBIDDEN_ASSET_PATTERNS if pattern.search(text)]
    return Check("Final widget assets are safe and backend-connected", not missing and not forbidden, f"missing={missing}; forbidden={forbidden}")


def no_forbidden_patterns() -> Check:
    findings: list[str] = []
    for path in [ASSET_HTML, ASSET_JS, *DOCS]:
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
        decision_doc_records_option(),
        result_doc_records_status(),
        snippets_use_placeholder(),
        decision_state_documented(),
        actual_upload_embed_not_complete(),
        public_launch_not_complete(),
        assets_are_safe_and_backend_connected(),
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
