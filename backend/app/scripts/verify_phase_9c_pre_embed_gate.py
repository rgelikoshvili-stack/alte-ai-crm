from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

FINAL_GATE = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PRE_EMBED_APPROVAL_GATE.md"
ASSET_HOSTING = PROJECT_ROOT / "docs" / "deployment" / "WIDGET_ASSET_HOSTING_DECISION.md"
READINESS_CHECKLIST = PROJECT_ROOT / "docs" / "deployment" / "FINAL_EMBED_READINESS_CHECKLIST.md"
REAL_DOMAIN_SMOKE = PROJECT_ROOT / "docs" / "deployment" / "REAL_DOMAIN_WIDGET_SMOKE_PLAN.md"
ROLLBACK_PLAN = PROJECT_ROOT / "docs" / "deployment" / "WIDGET_EMBED_ROLLBACK_PLAN.md"
PRIVACY_RECORD = PROJECT_ROOT / "docs" / "deployment" / "PRIVACY_DATA_APPROVAL_RECORD.md"

SAFE_PRO_WIDGET = PROJECT_ROOT / "widget" / "alte-university-ai-chatbot-safe-pro.html"

README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
READINESS_DOC = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md"
FINAL_PREFLIGHT = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md"
TRANSFER_DOC = PROJECT_ROOT / "docs" / "deployment" / "WIDGET_TRANSFER_TO_ALTE_SITE.md"
EMBED_DOC = PROJECT_ROOT / "docs" / "deployment" / "WEBSITE_WIDGET_PRODUCTION_EMBED.md"
SNIPPET_DOC = PROJECT_ROOT / "docs" / "deployment" / "WIDGET_SAFE_PRO_EMBED_SNIPPET.md"
WIDGET_SMOKE_DOC = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_WIDGET_SMOKE_CHECKLIST.md"
GO_NO_GO_DOC = PROJECT_ROOT / "docs" / "deployment" / "FINAL_WIDGET_EMBED_GO_NO_GO.md"

PRODUCTION_BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
DECISION_STATE = "BACKEND_DEPLOYED_SAFE_PRO_WIDGET_PRE_EMBED_GATE_READY_PENDING_APPROVALS"

REQUIRED_DOCS = [
    FINAL_GATE,
    ASSET_HOSTING,
    READINESS_CHECKLIST,
    REAL_DOMAIN_SMOKE,
    ROLLBACK_PLAN,
    PRIVACY_RECORD,
]

STATUS_DOCS = [
    README,
    NEXT_PHASES,
    READINESS_DOC,
    FINAL_PREFLIGHT,
    TRANSFER_DOC,
    EMBED_DOC,
    SNIPPET_DOC,
    WIDGET_SMOKE_DOC,
    GO_NO_GO_DOC,
    *REQUIRED_DOCS,
]

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
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def required_docs_exist() -> list[Check]:
    return [Check(f"Required doc exists: {path.name}", path.exists(), str(path)) for path in REQUIRED_DOCS]


def required_statuses_exist() -> Check:
    expected = {
        FINAL_GATE: "FINAL_PRE_EMBED_STATUS=NO_GO_PENDING_APPROVALS",
        ASSET_HOSTING: "WIDGET_ASSET_HOSTING_STATUS=PENDING_FINAL_URL",
        PRIVACY_RECORD: "PRIVACY_DATA_APPROVAL_STATUS=PENDING",
    }
    missing = []
    for path, status in expected.items():
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        if status not in text:
            missing.append(f"{path.name}:{status}")
    return Check("Pre-embed gate statuses remain pending/no-go", not missing, ", ".join(missing))


def decision_state_documented() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8") for path in STATUS_DOCS if path.exists())
    return Check("Phase 9C decision state documented", DECISION_STATE in text)


def actual_embed_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in STATUS_DOCS if path.exists())
    bad = [
        phrase
        for phrase in [
            "actual embed complete",
            "actual site embed complete",
            "actual website embed complete",
            "actual site embed completed",
            "actual website embed completed",
        ]
        if phrase in text
    ]
    return Check("Actual site embed not marked complete", not bad, ", ".join(bad))


def public_launch_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in STATUS_DOCS if path.exists())
    bad = [
        phrase
        for phrase in [
            "public launch complete",
            "full production launch complete",
            "public launch completed",
        ]
        if phrase in text
    ]
    return Check("Public launch not marked complete", not bad, ", ".join(bad))


def safe_pro_widget_exists() -> Check:
    return Check("Safe Pro widget exists", SAFE_PRO_WIDGET.exists(), str(SAFE_PRO_WIDGET))


def safe_pro_widget_has_no_forbidden_frontend_ai() -> Check:
    if not SAFE_PRO_WIDGET.exists():
        return Check("Safe Pro widget has no forbidden frontend AI", False, "missing safe pro widget")
    text = SAFE_PRO_WIDGET.read_text(encoding="utf-8")
    findings = [pattern.pattern for pattern in SAFE_WIDGET_FORBIDDEN if pattern.search(text)]
    return Check("Safe Pro widget has no direct Anthropic/API-key browser call", not findings, ", ".join(findings))


def safe_pro_widget_has_backend_endpoints() -> Check:
    if not SAFE_PRO_WIDGET.exists():
        return Check("Safe Pro widget backend endpoints", False, "missing safe pro widget")
    text = SAFE_PRO_WIDGET.read_text(encoding="utf-8")
    required = ["/chat/session/start", "/chat/message", PRODUCTION_BACKEND_URL]
    missing = [item for item in required if item not in text]
    return Check("Safe Pro widget contains production backend endpoints", not missing, ", ".join(missing))


def no_forbidden_patterns() -> Check:
    findings: list[str] = []
    for path in [SAFE_PRO_WIDGET, *REQUIRED_DOCS, README, NEXT_PHASES, READINESS_DOC, FINAL_PREFLIGHT]:
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
        *required_docs_exist(),
        required_statuses_exist(),
        decision_state_documented(),
        actual_embed_not_complete(),
        public_launch_not_complete(),
        safe_pro_widget_exists(),
        safe_pro_widget_has_no_forbidden_frontend_ai(),
        safe_pro_widget_has_backend_endpoints(),
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
