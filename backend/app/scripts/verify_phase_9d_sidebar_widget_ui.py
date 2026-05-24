from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

SAFE_PRO_WIDGET = PROJECT_ROOT / "widget" / "alte-university-ai-chatbot-safe-pro.html"
PIP_ARCHIVE = PROJECT_ROOT / "widget" / "archive" / "alte-university-ai-chatbot-safe-pro-pip-archive.html"
STANDALONE_DEMO = PROJECT_ROOT / "widget" / "standalone-safe-pro-demo.html"
DECISION_DOC = PROJECT_ROOT / "docs" / "deployment" / "WIDGET_SAFE_PRO_SIDEBAR_UI_DECISION.md"
README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
DESIGN_REVIEW = PROJECT_ROOT / "docs" / "deployment" / "WIDGET_DESIGN_CONCEPTS_REVIEW.md"
SNIPPET_DOC = PROJECT_ROOT / "docs" / "deployment" / "WIDGET_SAFE_PRO_EMBED_SNIPPET.md"
REAL_DOMAIN_SMOKE = PROJECT_ROOT / "docs" / "deployment" / "REAL_DOMAIN_WIDGET_SMOKE_PLAN.md"
FINAL_GATE = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PRE_EMBED_APPROVAL_GATE.md"

PRODUCTION_BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
DECISION_STATE = "BACKEND_DEPLOYED_SAFE_PRO_SIDEBAR_WIDGET_READY_PENDING_REDEPLOY_AND_SITE_EMBED"
DOCS = [DECISION_DOC, README, NEXT_PHASES, DESIGN_REVIEW, SNIPPET_DOC, REAL_DOMAIN_SMOKE, FINAL_GATE]

SECRET_PATTERNS = [
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
    re.compile(r"DB_PASSWORD\s*=", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]

SAFE_WIDGET_FORBIDDEN = [
    re.compile(r"api\.anthropic\.com", re.IGNORECASE),
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile(r"\bconst\s+SYS\b", re.IGNORECASE),
    re.compile(r"\bsystem\s*:\s*SYS\b", re.IGNORECASE),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def required_files_exist() -> list[Check]:
    required = [SAFE_PRO_WIDGET, PIP_ARCHIVE, STANDALONE_DEMO, DECISION_DOC]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in required]


def sidebar_structure_present() -> Check:
    text = SAFE_PRO_WIDGET.read_text(encoding="utf-8") if SAFE_PRO_WIDGET.exists() else ""
    required = [
        "alte-sidebar",
        "dept-list",
        "selected_department",
        "selected_topic",
        "safe_pro_sidebar",
        "admissions",
        "finance",
        "international",
        "medicine",
        "student_services",
        "it_support",
    ]
    missing = [item for item in required if item not in text]
    return Check("Safe Pro widget contains sidebar department structure", not missing, ", ".join(missing))


def backend_wiring_present() -> Check:
    text = SAFE_PRO_WIDGET.read_text(encoding="utf-8") if SAFE_PRO_WIDGET.exists() else ""
    required = ["/chat/session/start", "/chat/message", PRODUCTION_BACKEND_URL]
    missing = [item for item in required if item not in text]
    return Check("Safe Pro widget contains backend endpoints", not missing, ", ".join(missing))


def safe_widget_has_no_forbidden_frontend_ai() -> Check:
    text = SAFE_PRO_WIDGET.read_text(encoding="utf-8") if SAFE_PRO_WIDGET.exists() else ""
    findings = [pattern.pattern for pattern in SAFE_WIDGET_FORBIDDEN if pattern.search(text)]
    return Check("Safe Pro widget has no direct Anthropic/API-key/system-prompt browser call", not findings, ", ".join(findings))


def standalone_demo_references_sidebar() -> Check:
    text = STANDALONE_DEMO.read_text(encoding="utf-8") if STANDALONE_DEMO.exists() else ""
    required = ["sidebar Pro layout", "browser -> FastAPI backend", "alte-university-ai-chatbot-safe-pro.html"]
    missing = [item for item in required if item not in text]
    return Check("Standalone demo references sidebar Pro layout", not missing, ", ".join(missing))


def decision_state_documented() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8") for path in DOCS if path.exists())
    return Check("Phase 9D-UI decision state documented", DECISION_STATE in text)


def public_launch_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in DOCS if path.exists())
    bad = [phrase for phrase in ["public launch complete", "full production launch complete"] if phrase in text]
    return Check("Public launch not marked complete", not bad, ", ".join(bad))


def no_forbidden_patterns() -> Check:
    findings: list[str] = []
    for path in [SAFE_PRO_WIDGET, *DOCS]:
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
        sidebar_structure_present(),
        backend_wiring_present(),
        safe_widget_has_no_forbidden_frontend_ai(),
        standalone_demo_references_sidebar(),
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
