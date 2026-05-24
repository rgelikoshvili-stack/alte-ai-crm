from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
VERIFY_SCRIPT = BACKEND_ROOT / "app" / "scripts" / "verify_finance_no_contact_guard.py"
TEST_FILE = BACKEND_ROOT / "app" / "tests" / "test_finance_no_contact_guard.py"
DOCS = [
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "docs" / "NEXT_PHASES.md",
    PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md",
    PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md",
    PROJECT_ROOT / "docs" / "deployment" / "CHATBOT_PUBLIC_ANSWER_POLICY.md",
    PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_KNOWLEDGE_SMOKE_AFTER_STUDY_DOCS_RESULT.md",
    PROJECT_ROOT / "docs" / "deployment" / "FULL_ALTE_LOCAL_KB_IMPORT_RESULT.md",
]
DECISION_STATE = "BACKEND_CODE_FIXED_FINANCE_NO_CONTACT_GUARD_PENDING_REDEPLOY"
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
        Check("Finance guard tests exist", TEST_FILE.exists(), str(TEST_FILE)),
        Check("Finance guard verification script exists", VERIFY_SCRIPT.exists(), str(VERIFY_SCRIPT)),
    ]


def docs_record_fix() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8") for path in DOCS if path.exists())
    required = ["tuition/finance no-contact lead bug", "service-layer guard fixed locally", "production redeploy required"]
    missing = [item for item in required if item not in text]
    return Check("Docs record bug, fix, and redeploy requirement", not missing, ", ".join(missing))


def decision_state_documented() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8") for path in DOCS if path.exists())
    return Check("Phase 8Y decision state documented", DECISION_STATE in text)


def public_launch_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in DOCS if path.exists())
    bad = [phrase for phrase in ["public launch complete", "full production launch complete", "actual site embed completed"] if phrase in text]
    return Check("Public launch not marked complete", not bad, ", ".join(bad))


def no_forbidden_patterns() -> Check:
    findings: list[str] = []
    for path in [TEST_FILE, *DOCS]:
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
        docs_record_fix(),
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
