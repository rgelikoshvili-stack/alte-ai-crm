from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9E_REDEPLOY_SIDEBAR_AMBIGUOUS_ROUTING_RESULT.md"
SMOKE_SCRIPT = BACKEND_ROOT / "app" / "scripts" / "production_department_routing_sidebar_smoke.py"
SAFE_PRO_WIDGET = PROJECT_ROOT / "widget" / "alte-university-ai-chatbot-safe-pro.html"

README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
READINESS = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md"
FINAL_PREFLIGHT = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md"
ROUTING_POLICY = PROJECT_ROOT / "docs" / "deployment" / "DEPARTMENT_HANDOVER_ROUTING_POLICY.md"
FIX_DOC = PROJECT_ROOT / "docs" / "deployment" / "SIDEBAR_AMBIGUOUS_ROUTING_FIX.md"
PHASE_9D_RESULT = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9D_REDEPLOY_DEPARTMENT_ROUTING_RESULT.md"
REAL_DOMAIN_SMOKE = PROJECT_ROOT / "docs" / "deployment" / "REAL_DOMAIN_WIDGET_SMOKE_PLAN.md"
FINAL_GATE = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PRE_EMBED_APPROVAL_GATE.md"

IMAGE_TAG = "v0.9-sidebar-ambiguous-routing-fix"
PASS_STATUS = "PASSED_SIDEBAR_AMBIGUOUS_ROUTING_VERIFIED"
FAIL_STATUS = "FAILED_SIDEBAR_AMBIGUOUS_ROUTING_NEEDS_REVIEW"
PASS_DECISION = "BACKEND_DEPLOYED_SIDEBAR_AMBIGUOUS_ROUTING_VERIFIED_PENDING_REVIEW_AND_SITE_EMBED"
FAIL_DECISION = "BACKEND_DEPLOYED_SIDEBAR_AMBIGUOUS_ROUTING_FAILED_NEEDS_REVIEW"
PRODUCTION_BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"

DOCS = [
    RESULT_DOC,
    README,
    NEXT_PHASES,
    READINESS,
    FINAL_PREFLIGHT,
    ROUTING_POLICY,
    FIX_DOC,
    PHASE_9D_RESULT,
    REAL_DOMAIN_SMOKE,
    FINAL_GATE,
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
    return [
        Check("Phase 9E redeploy result doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
        Check("Production department routing sidebar smoke script exists", SMOKE_SCRIPT.exists(), str(SMOKE_SCRIPT)),
        Check("Safe Pro widget exists", SAFE_PRO_WIDGET.exists(), str(SAFE_PRO_WIDGET)),
    ]


def result_doc_records_redeploy() -> Check:
    if not RESULT_DOC.exists():
        return Check("Result doc records redeploy", False, "missing")
    text = RESULT_DOC.read_text(encoding="utf-8")
    required = [
        IMAGE_TAG,
        "/health",
        "/version",
        "/diagnostics/ai",
        "Finance ambiguous sidebar case: PASS",
        "Medicine ambiguous sidebar case: PASS",
        "No contact details sent: yes",
        "Contact-flow test not run: yes",
        "Intentional lead/task/customer creation: no",
    ]
    missing = [item for item in required if item not in text]
    has_status = PASS_STATUS in text or FAIL_STATUS in text
    return Check("Result doc records image, endpoints, fixed cases, safety, and status", not missing and has_status, ", ".join(missing))


def decision_state_documented() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8") for path in DOCS if path.exists())
    return Check("Phase 9E redeploy decision state documented", PASS_DECISION in text or FAIL_DECISION in text)


def safe_widget_still_safe() -> Check:
    text = SAFE_PRO_WIDGET.read_text(encoding="utf-8") if SAFE_PRO_WIDGET.exists() else ""
    required = [
        "/chat/session/start",
        "/chat/message",
        "selected_department",
        "selected_topic",
        PRODUCTION_BACKEND_URL,
    ]
    missing = [item for item in required if item not in text]
    forbidden = [pattern.pattern for pattern in WIDGET_FORBIDDEN if pattern.search(text)]
    return Check("Safe Pro widget still uses backend endpoints and safe context", not missing and not forbidden, f"missing={missing}; forbidden={forbidden}")


def public_launch_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in DOCS if path.exists())
    bad = [
        phrase
        for phrase in ["public launch complete", "full production launch complete", "actual site embed completed"]
        if phrase in text
    ]
    return Check("Public launch not marked complete", not bad, ", ".join(bad))


def no_forbidden_patterns() -> Check:
    findings: list[str] = []
    for path in [RESULT_DOC, SMOKE_SCRIPT, SAFE_PRO_WIDGET, *DOCS]:
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
        result_doc_records_redeploy(),
        decision_state_documented(),
        safe_widget_still_safe(),
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
