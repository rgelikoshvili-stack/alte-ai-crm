from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AG_PRIVACY_CONTACT_APPROVAL_GATE_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"

FRONTEND_FILES = [
    PROJECT_ROOT / "test_site" / "join.html",
    PROJECT_ROOT / "test_site" / "index.html",
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js",
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-chat.jsx",
    PROJECT_ROOT / "widget" / "variants" / "pro-v2-chat.jsx",
    PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js",
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

VALID_STATUS = "PHASE_9AG_PRIVACY_CONTACT_GATE_STATUS=NO_GO_PRIVACY_URL_PENDING_CONTACT_FLOW_NOT_APPROVED"


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
    return Check("Phase 9AG gate doc exists", RESULT_DOC.exists(), str(RESULT_DOC))


def status_values_valid() -> Check:
    text = read(RESULT_DOC)
    required = [
        VALID_STATUS,
        "BACKEND_DEPLOYED_GEORGIAN_ENCODING_FIXED_PENDING_PRIVACY_AND_EMBED_APPROVAL",
        "Public launch: NO-GO",
        "PRIVACY_URL_STATUS=PENDING",
        "CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED",
        "CONTACT_DATA_TEST_STATUS=NOT_EXECUTED",
        "PUBLIC_LAUNCH_STATUS=NO_GO",
    ]
    missing = [item for item in required if item not in text]
    return Check("Phase 9AG status values are pending/no-go", not missing, ", ".join(missing))


def privacy_url_pending_or_https() -> Check:
    text = read(RESULT_DOC)
    pending = "PRIVACY_URL_STATUS=PENDING" in text
    match = re.search(r"^OFFICIAL_PRIVACY_URL=(.+)$", text, re.MULTILINE)
    if not match:
        return Check("Official privacy URL field exists", False)
    value = match.group(1).strip()
    is_placeholder = value == "<approved official Alte privacy policy URL>"
    valid = (pending and is_placeholder) or value.startswith("https://")
    return Check("Privacy URL is pending or HTTPS if provided", valid, value)


def contact_flow_not_approved_or_executed() -> Check:
    text = read(RESULT_DOC)
    required = [
        "CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED",
        "CONTACT_DATA_TEST_STATUS=NOT_EXECUTED",
        "LEAD_TASK_CUSTOMER_CREATION_STATUS=NOT_EXECUTED_PENDING_CONTACT_FLOW_APPROVAL",
        "Production contact-flow test executed: NO",
        "Lead/task/customer created: NO",
    ]
    forbidden = [
        "CONTACT_FLOW_APPROVAL_STATUS=APPROVED",
        "CONTACT_DATA_TEST_STATUS=EXECUTED",
        "LEAD_TASK_CUSTOMER_CREATION_STATUS=EXECUTED",
        "Production contact-flow test executed: YES",
        "Lead/task/customer created: YES",
    ]
    missing = [item for item in required if item not in text]
    findings = [item for item in forbidden if item in text]
    return Check("Contact-flow and CRM creation remain unapproved/unexecuted", not missing and not findings, ", ".join(missing + findings))


def consent_copy_present_and_utf8() -> Check:
    text = read(RESULT_DOC)
    required = [
        "Georgian:",
        "English:",
        "ოპერატორთან დაკავშირების მოთხოვნის გაგზავნამდე",
        "კონფიდენციალურობის პოლიტიკას",
        "Before submitting an operator contact request",
        "Privacy Policy",
    ]
    missing = [item for item in required if item not in text]
    mojibake = "áƒ" in text
    detail = ", ".join(missing + (["mojibake áƒ"] if mojibake else []))
    return Check("Consent copy is present and UTF-8 Georgian is intact", not missing and not mojibake, detail)


def public_launch_no_go() -> Check:
    text = "\n".join(read(path).lower() for path in [RESULT_DOC, PUBLIC_LAUNCH])
    bad = ["public_launch_decision=go", "public launch: go", "public launch complete"]
    findings = [item for item in bad if item in text]
    return Check("Public launch remains NO-GO", "no-go" in text and not findings, ", ".join(findings))


def no_real_contact_details_in_doc() -> Check:
    text = read(RESULT_DOC)
    findings: list[str] = []
    for pattern in REAL_CONTACT_PATTERNS:
        findings.extend(match.group(0) for match in pattern.finditer(text))
    return Check("No real contact details are included", not findings, ", ".join(findings))


def no_real_site_or_production_actions() -> Check:
    text = read(RESULT_DOC)
    required = [
        "Real `alte.edu.ge` modified: NO",
        "Real `join.alte.edu.ge` modified: NO",
        "Secret Manager changed: NO",
        "Production DB changed: NO",
        "Migration/seed run: NO",
    ]
    missing = [item for item in required if item not in text]
    return Check("No real-site or production infrastructure action is recorded", not missing, ", ".join(missing))


def frontend_contract_and_secrets_safe() -> Check:
    findings: list[str] = []
    combined = []
    for path in FRONTEND_FILES:
        if not path.exists():
            continue
        text = read(path)
        combined.append(text)
        for pattern in FORBIDDEN_FRONTEND_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.relative_to(PROJECT_ROOT)}:{pattern.pattern}")
    joined = "\n".join(combined)
    if "/chat/session/start" not in joined:
        findings.append("missing /chat/session/start")
    if "/chat/message" not in joined:
        findings.append("missing /chat/message")
    return Check("Frontend uses approved endpoints and exposes no API keys", not findings, ", ".join(findings))


def tracked_secret_files_absent() -> Check:
    tracked = set(git_lines("ls-files"))
    forbidden = [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]
    return Check("No .env or .local-secrets files are tracked", not forbidden, ", ".join(forbidden))


def run_checks() -> list[Check]:
    return [
        result_doc_exists(),
        status_values_valid(),
        privacy_url_pending_or_https(),
        contact_flow_not_approved_or_executed(),
        consent_copy_present_and_utf8(),
        public_launch_no_go(),
        no_real_contact_details_in_doc(),
        no_real_site_or_production_actions(),
        frontend_contract_and_secrets_safe(),
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
