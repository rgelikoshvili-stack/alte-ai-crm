from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AH_WAIT_FOR_OPERATOR_AND_MESSAGE_FIELD_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"

FRONTEND_FILES = [
    PROJECT_ROOT / "test_site" / "join.html",
    PROJECT_ROOT / "test_site" / "index.html",
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js",
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-chat.jsx",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-modals.jsx",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-strings.jsx",
    PROJECT_ROOT / "widget" / "variants" / "pro-v2-chat.jsx",
    PROJECT_ROOT / "widget" / "variants" / "pro-v2-modals.jsx",
    PROJECT_ROOT / "widget" / "variants" / "pro-v2-strings.jsx",
    PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js",
]

BACKEND_FILES = [
    PROJECT_ROOT / "backend" / "app" / "schemas" / "chat.py",
    PROJECT_ROOT / "backend" / "app" / "services" / "chat_service.py",
    PROJECT_ROOT / "backend" / "app" / "services" / "operator_service.py",
]

FORBIDDEN_FRONTEND_PATTERNS = [
    re.compile(r"/api/chat", re.IGNORECASE),
    re.compile(r"api\.anthropic\.com", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant", re.IGNORECASE),
]

REAL_CONTACT_PATTERNS = [
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"\+995[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}[\s-]?\d{2}"),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def git_lines(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def result_doc_exists() -> Check:
    return Check("Phase 9AH result doc exists", RESULT_DOC.exists(), str(RESULT_DOC))


def result_status_valid() -> Check:
    text = read(RESULT_DOC)
    valid = [
        "PHASE_9AH_WAIT_FOR_OPERATOR_STATUS=READY_PENDING_PRIVACY_CONTACT_APPROVAL",
        "PHASE_9AH_WAIT_FOR_OPERATOR_STATUS=FRONTEND_READY_PENDING_BACKEND_PERSISTENCE_APPROVAL",
        "PHASE_9AH_WAIT_FOR_OPERATOR_STATUS=FIXED_PENDING_NETLIFY_REDEPLOY",
    ]
    return Check("Phase 9AH result status is valid", any(item in text for item in valid))


def contact_textarea_labels_present() -> Check:
    text = "\n".join(read(path) for path in FRONTEND_FILES)
    required = [
        "თქვენი კითხვა / შეტყობინება",
        "Your question / message",
        "დაწერეთ თქვენი კითხვა ან მოკლე ტექსტი ოპერატორისთვის...",
        "Write your question or message for the operator...",
        "<textarea",
    ]
    missing = [item for item in required if item not in text]
    return Check("Contact message textarea labels/placeholders exist", not missing, ", ".join(missing))


def wait_for_operator_text_present() -> Check:
    text = "\n".join(read(path) for path in FRONTEND_FILES + BACKEND_FILES)
    required = [
        "დაელოდე ოპერატორს",
        "Wait for operator",
        "waiting_for_operator",
        "თქვენი მოთხოვნა გადაეცა ოპერატორს",
        "Your request has been sent to an operator",
    ]
    missing = [item for item in required if item not in text]
    return Check("Wait-for-operator action and confirmation exist", not missing, ", ".join(missing))


def unsupported_copy_present() -> Check:
    text = read(PROJECT_ROOT / "backend" / "app" / "services" / "chat_service.py")
    required = [
        "ამ საკითხზე დამტკიცებულ წყაროში ზუსტი ინფორმაცია ვერ ვიპოვე",
        "შემიძლია დაგაკავშიროთ შესაბამის ოპერატორთან",
        "I couldn't find an exact answer in the approved official sources",
        "I can connect you with the relevant operator",
    ]
    missing = [item for item in required if item not in text]
    return Check("Unsupported answer copy offers safe operator handover", not missing, ", ".join(missing))


def backend_waiting_support_present() -> Check:
    text = "\n".join(read(path) for path in BACKEND_FILES)
    required = [
        "ChatHandoverRequest",
        "selected_department",
        "message: str | None = None",
        "conversation.status = \"waiting_for_operator\"",
        "handover_waiting_for_operator",
        "task_created",
        "selected_department=selected_department",
    ]
    missing = [item for item in required if item not in text]
    return Check("Backend supports no-contact waiting handover without migration", not missing, ", ".join(missing))


def frontend_contract_safe() -> Check:
    findings: list[str] = []
    text = "\n".join(read(path) for path in FRONTEND_FILES)
    for pattern in FORBIDDEN_FRONTEND_PATTERNS:
        if pattern.search(text):
            findings.append(pattern.pattern)
    if "/chat/session/start" not in text:
        findings.append("missing /chat/session/start")
    if "/chat/message" not in text:
        findings.append("missing /chat/message")
    if "/chat/handover/" not in text:
        findings.append("missing /chat/handover/")
    return Check("Frontend uses backend endpoints and no direct AI/key patterns", not findings, ", ".join(findings))


def no_mojibake() -> Check:
    paths = FRONTEND_FILES + BACKEND_FILES + [RESULT_DOC]
    findings = [str(path.relative_to(PROJECT_ROOT)) for path in paths if "áƒ" in read(path)]
    return Check("No Georgian mojibake in changed source/doc files", not findings, ", ".join(findings))


def public_launch_no_go() -> Check:
    text = "\n".join(read(path).lower() for path in [RESULT_DOC, PUBLIC_LAUNCH])
    bad = ["public_launch_decision=go", "public launch: go", "public launch complete"]
    findings = [item for item in bad if item in text]
    return Check("Public launch remains NO-GO", "no-go" in text and not findings, ", ".join(findings))


def no_real_contact_data_or_crm_execution_marked() -> Check:
    text = read(RESULT_DOC)
    findings: list[str] = []
    for pattern in REAL_CONTACT_PATTERNS:
        findings.extend(match.group(0) for match in pattern.finditer(text))
    forbidden = [
        "Real contact data sent: YES",
        "Lead/task/customer created: YES",
        "DB migration status: RUN",
        "Real Alte site modified: YES",
    ]
    findings.extend(item for item in forbidden if item in text)
    return Check("No real contact data or approved CRM execution is recorded", not findings, ", ".join(findings))


def tracked_secret_files_absent() -> Check:
    tracked = set(git_lines("ls-files"))
    forbidden = [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]
    return Check("No .env or .local-secrets files are tracked", not forbidden, ", ".join(forbidden))


def run_checks() -> list[Check]:
    return [
        result_doc_exists(),
        result_status_valid(),
        contact_textarea_labels_present(),
        wait_for_operator_text_present(),
        unsupported_copy_present(),
        backend_waiting_support_present(),
        frontend_contract_safe(),
        no_mojibake(),
        public_launch_no_go(),
        no_real_contact_data_or_crm_execution_marked(),
        tracked_secret_files_absent(),
    ]


def main() -> None:
    checks = run_checks()
    for check in checks:
        print(f"{'PASS' if check.passed else 'FAIL'} {check.name}: {check.detail}")
    if any(not check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
