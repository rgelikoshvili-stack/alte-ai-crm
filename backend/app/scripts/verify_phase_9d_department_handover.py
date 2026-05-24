from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
APP_ROOT = BACKEND_ROOT / "app"

ROUTING_SERVICE = APP_ROOT / "services" / "department_routing_service.py"
POLICY_DOC = PROJECT_ROOT / "docs" / "deployment" / "DEPARTMENT_HANDOVER_ROUTING_POLICY.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9D_DEPARTMENT_HANDOVER_RESULT.md"
SMOKE_SCRIPT = APP_ROOT / "scripts" / "production_department_handover_smoke.py"
SAFE_PRO_WIDGET = PROJECT_ROOT / "widget" / "alte-university-ai-chatbot-safe-pro.html"

TESTS = [
    APP_ROOT / "tests" / "test_department_routing_service.py",
    APP_ROOT / "tests" / "test_department_handover_chat.py",
    APP_ROOT / "tests" / "test_widget_department_context.py",
]

README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
READINESS_DOC = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md"
FINAL_PREFLIGHT = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md"
PUBLIC_POLICY = PROJECT_ROOT / "docs" / "deployment" / "CHATBOT_PUBLIC_ANSWER_POLICY.md"
REAL_DOMAIN_SMOKE = PROJECT_ROOT / "docs" / "deployment" / "REAL_DOMAIN_WIDGET_SMOKE_PLAN.md"
FINAL_PRE_EMBED = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PRE_EMBED_APPROVAL_GATE.md"

DECISION_STATE = "BACKEND_CODE_READY_DEPARTMENT_HANDOVER_ROUTING_PENDING_REDEPLOY"

DOCS = [POLICY_DOC, RESULT_DOC, README, NEXT_PHASES, READINESS_DOC, FINAL_PREFLIGHT, PUBLIC_POLICY, REAL_DOMAIN_SMOKE, FINAL_PRE_EMBED]

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
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def required_files_exist() -> list[Check]:
    required = [ROUTING_SERVICE, POLICY_DOC, RESULT_DOC, SMOKE_SCRIPT, SAFE_PRO_WIDGET, *TESTS]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in required]


def safe_pro_widget_sends_context() -> Check:
    text = SAFE_PRO_WIDGET.read_text(encoding="utf-8") if SAFE_PRO_WIDGET.exists() else ""
    required = ["selected_department", "selected_topic", "widget_variant", "safe_pro"]
    missing = [item for item in required if item not in text]
    return Check("Safe Pro widget sends selected department/topic context", not missing, ", ".join(missing))


def safe_pro_widget_has_no_forbidden_frontend_ai() -> Check:
    text = SAFE_PRO_WIDGET.read_text(encoding="utf-8") if SAFE_PRO_WIDGET.exists() else ""
    findings = [pattern.pattern for pattern in SAFE_WIDGET_FORBIDDEN if pattern.search(text)]
    return Check("Safe Pro widget has no direct Anthropic/API-key browser call", not findings, ", ".join(findings))


def routing_service_contains_departments() -> Check:
    text = ROUTING_SERVICE.read_text(encoding="utf-8") if ROUTING_SERVICE.exists() else ""
    required = ["Admissions", "International Admissions", "Finance", "Medicine / MD", "Student Services", "IT Support"]
    missing = [item for item in required if item not in text]
    return Check("Routing service contains required departments", not missing, ", ".join(missing))


def decision_state_documented() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8") for path in DOCS if path.exists())
    return Check("Phase 9D decision state documented", DECISION_STATE in text)


def public_launch_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in DOCS if path.exists())
    bad = [phrase for phrase in ["public launch complete", "full production launch complete"] if phrase in text]
    return Check("Public launch not marked complete", not bad, ", ".join(bad))


def no_forbidden_patterns() -> Check:
    findings: list[str] = []
    for path in [ROUTING_SERVICE, SAFE_PRO_WIDGET, SMOKE_SCRIPT, *DOCS]:
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
        routing_service_contains_departments(),
        safe_pro_widget_sends_context(),
        safe_pro_widget_has_no_forbidden_frontend_ai(),
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
