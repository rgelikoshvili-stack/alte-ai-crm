from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
CHAT_SERVICE = BACKEND_ROOT / "app" / "services" / "chat_service.py"
TEST_FILE = BACKEND_ROOT / "app" / "tests" / "test_finance_no_contact_guard.py"
SMOKE_SCRIPT = BACKEND_ROOT / "app" / "scripts" / "production_knowledge_smoke_after_study_docs.py"
DOCS = [
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "docs" / "NEXT_PHASES.md",
    PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md",
    PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md",
    PROJECT_ROOT / "docs" / "deployment" / "CHATBOT_PUBLIC_ANSWER_POLICY.md",
    PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_KNOWLEDGE_SMOKE_AFTER_STUDY_DOCS_RESULT.md",
    PROJECT_ROOT / "docs" / "deployment" / "FULL_ALTE_LOCAL_KB_IMPORT_RESULT.md",
]
SECRET_PATTERNS = [
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
    re.compile(r"DB_PASSWORD\s*=", re.IGNORECASE),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def finance_guard_exists() -> Check:
    text = CHAT_SERVICE.read_text(encoding="utf-8")
    required = [
        "apply_info_only_no_contact_guard",
        "INFO_ONLY_NO_CONTACT_QUALIFICATION_INTENTS",
        "tuition_fee",
        "scholarship",
        "schedule",
        "analysis.should_create_lead = False",
    ]
    missing = [item for item in required if item not in text]
    return Check("Finance no-contact guard exists", not missing, ", ".join(missing))


def tests_exist() -> Check:
    text = TEST_FILE.read_text(encoding="utf-8") if TEST_FILE.exists() else ""
    required = [
        "test_ka_tuition_without_contact_does_not_create_lead_task_or_customer",
        "test_en_tuition_without_contact_does_not_create_lead_task_or_customer",
        "test_scholarship_without_contact_does_not_create_lead_task_or_customer",
        "test_deadline_without_contact_does_not_create_lead_task_or_customer",
    ]
    missing = [item for item in required if item not in text]
    return Check("Finance no-contact guard tests exist", TEST_FILE.exists() and not missing, ", ".join(missing))


def smoke_expectation_updated() -> Check:
    text = SMOKE_SCRIPT.read_text(encoding="utf-8") if SMOKE_SCRIPT.exists() else ""
    return Check("Smoke script checks tuition no-contact guard", "tuition no-contact lead guard" in text)


def docs_record_rule() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8") for path in DOCS if path.exists())
    required = [
        "finance no-contact lead guard",
        "production redeploy required",
        "BACKEND_CODE_FIXED_FINANCE_NO_CONTACT_GUARD_PENDING_REDEPLOY",
    ]
    missing = [item for item in required if item not in text]
    return Check("Docs record finance no-contact guard and redeploy requirement", not missing, ", ".join(missing))


def no_forbidden_secrets() -> Check:
    findings: list[str] = []
    for path in [CHAT_SERVICE, TEST_FILE, SMOKE_SCRIPT, *DOCS]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return Check("No forbidden secret patterns", not findings, ", ".join(findings))


def run_checks() -> list[Check]:
    return [
        finance_guard_exists(),
        tests_exist(),
        smoke_expectation_updated(),
        docs_record_rule(),
        no_forbidden_secrets(),
    ]


def main() -> None:
    checks = run_checks()
    for check in checks:
        print(f"{'PASS' if check.passed else 'FAIL'} {check.name}: {check.detail}")
    if any(not check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
