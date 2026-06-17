from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AC_INTEGRATED_CHAT_ROUTING_OPERATOR_QA_RESULT.md"
QA_SCRIPT = PROJECT_ROOT / "backend" / "app" / "scripts" / "production_integrated_chat_routing_operator_qa.py"
TEST_SITE_FILES = [
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js",
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html",
    PROJECT_ROOT / "test_site" / "join.html",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-chat.jsx",
]

VALID_STATUSES = {
    "PHASE_9AC_INTEGRATED_QA_STATUS=PASSED_PENDING_MOBILE_VISUAL_QA_PRIVACY_AND_EMBED_APPROVAL",
    "PHASE_9AC_INTEGRATED_QA_STATUS=FAILED_PENDING_ROUTING_OR_KB_FIX",
}


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def result_doc_exists() -> Check:
    return Check("Phase 9AC result doc exists", RESULT_DOC.exists(), str(RESULT_DOC))


def qa_script_exists() -> Check:
    return Check("Phase 9AC production QA script exists", QA_SCRIPT.exists(), str(QA_SCRIPT))


def status_valid() -> Check:
    text = read(RESULT_DOC)
    matches = [status for status in VALID_STATUSES if status in text]
    return Check("Phase 9AC status is valid", len(matches) == 1, ", ".join(matches))


def official_facts_documented() -> Check:
    text = read(RESULT_DOC)
    required = ["240", "120", "5", "9-14 March"]
    missing = [item for item in required if item not in text]
    return Check("Official KB facts documented", not missing, ", ".join(missing))


def auto_routing_cases_documented() -> Check:
    text = read(RESULT_DOC).lower()
    required = [
        "admissions",
        "programs",
        "finance",
        "student status",
        "exam",
        "mobility",
        "international",
        "it help",
        "library",
        "2031",
    ]
    missing = [item for item in required if item not in text]
    return Check("Auto-routing cases documented", not missing, ", ".join(missing))


def contact_safety_documented() -> Check:
    text = read(RESULT_DOC).lower()
    required = [
        "no assistant answer asked",
        "no contact details were sent",
        "no lead/task/customer",
    ]
    missing = [item for item in required if item not in text]
    return Check("Contact safety documented", not missing, ", ".join(missing))


def public_launch_no_go() -> Check:
    text = read(RESULT_DOC).lower()
    bad = ["public_launch_decision=go", "public launch complete", "public launch: go"]
    findings = [item for item in bad if item in text]
    return Check("Public launch remains NO-GO", "no-go" in text and not findings, ", ".join(findings))


def frontend_contract_safe() -> Check:
    text = "\n".join(read(path) for path in TEST_SITE_FILES)
    required = ["/chat/session/start", "/chat/message"]
    forbidden = ["/api/chat", "api.anthropic.com", "ANTHROPIC_API_KEY", "sk-ant-"]
    missing = [item for item in required if item not in text]
    findings = [item for item in forbidden if item in text]
    return Check("Frontend uses backend contract and no forbidden provider calls", not missing and not findings, f"missing={missing}; forbidden={findings}")


def env_not_tracked() -> Check:
    result = subprocess.run(["git", "ls-files", ".env", "backend/.env"], cwd=PROJECT_ROOT, capture_output=True, text=True, check=False)
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".env not tracked", not tracked, ", ".join(tracked))


def local_secrets_not_tracked() -> Check:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "backend/.local-secrets", "C:\\tmp\\alte-ai-crm.local-secrets"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".local-secrets not tracked", not tracked, ", ".join(tracked))


def run_checks() -> list[Check]:
    return [
        result_doc_exists(),
        qa_script_exists(),
        status_valid(),
        official_facts_documented(),
        auto_routing_cases_documented(),
        contact_safety_documented(),
        public_launch_no_go(),
        frontend_contract_safe(),
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
