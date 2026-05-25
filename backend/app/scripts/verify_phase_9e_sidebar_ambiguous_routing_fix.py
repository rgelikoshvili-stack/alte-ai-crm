from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

ROUTING_SERVICE = BACKEND_ROOT / "app" / "services" / "department_routing_service.py"
TEST_FILE = BACKEND_ROOT / "app" / "tests" / "test_sidebar_ambiguous_department_priority.py"
FIX_DOC = PROJECT_ROOT / "docs" / "deployment" / "SIDEBAR_AMBIGUOUS_ROUTING_FIX.md"

README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
READINESS = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md"
FINAL_PREFLIGHT = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md"
ROUTING_POLICY = PROJECT_ROOT / "docs" / "deployment" / "DEPARTMENT_HANDOVER_ROUTING_POLICY.md"
REDEPLOY_RESULT = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9D_REDEPLOY_DEPARTMENT_ROUTING_RESULT.md"

DECISION_STATE = "BACKEND_CODE_FIXED_SIDEBAR_AMBIGUOUS_ROUTING_PENDING_REDEPLOY"
DOCS = [FIX_DOC, README, NEXT_PHASES, READINESS, FINAL_PREFLIGHT, ROUTING_POLICY, REDEPLOY_RESULT]

SECRET_PATTERNS = [
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
    re.compile(r"DB_PASSWORD\s*=", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def required_files_exist() -> list[Check]:
    return [
        Check("Routing service exists", ROUTING_SERVICE.exists(), str(ROUTING_SERVICE)),
        Check("Sidebar ambiguous routing tests exist", TEST_FILE.exists(), str(TEST_FILE)),
        Check("Sidebar ambiguous routing fix doc exists", FIX_DOC.exists(), str(FIX_DOC)),
    ]


def routing_service_contains_fix() -> Check:
    text = ROUTING_SERVICE.read_text(encoding="utf-8") if ROUTING_SERVICE.exists() else ""
    required = [
        "is_ambiguous_message",
        "AMBIGUOUS_MESSAGE_TERMS",
        "sidebar_context_for_ambiguous_message",
        "message_only_context",
    ]
    missing = [item for item in required if item not in text]
    return Check("Routing service contains ambiguous sidebar priority fix", not missing, ", ".join(missing))


def docs_record_fix() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8") for path in DOCS if path.exists())
    required = [
        "selected_department=finance",
        "მაინტერესებს დეტალები",
        "selected_department=medicine",
        "დეტალები მაინტერესებს",
        "Strong explicit",
        "Redeploy is required",
        DECISION_STATE,
    ]
    missing = [item for item in required if item not in text]
    return Check("Docs record failing cases, priority rule, override rule, redeploy, and decision state", not missing, ", ".join(missing))


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
    for path in [ROUTING_SERVICE, TEST_FILE, *DOCS]:
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
        routing_service_contains_fix(),
        docs_record_fix(),
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
