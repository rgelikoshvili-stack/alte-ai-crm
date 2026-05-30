from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AF_PRIVACY_AND_CONTACT_FLOW_APPROVAL_READINESS.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
PHASE_9AE_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AE_FINAL_PREFLIGHT_APPROVAL_PACKAGE.md"

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
    return Check("Phase 9AF readiness doc exists", RESULT_DOC.exists(), str(RESULT_DOC))


def privacy_url_pending_unless_provided() -> Check:
    text = read(RESULT_DOC)
    has_pending = "OFFICIAL_PRIVACY_URL_STATUS=PENDING" in text
    placeholder_field = "OFFICIAL_PRIVACY_URL=<approved official Alte privacy policy URL>" in text
    approved = "OFFICIAL_PRIVACY_URL_STATUS=APPROVED" in text
    return Check("Privacy URL remains pending", has_pending and placeholder_field and not approved)


def contact_flow_not_approved() -> Check:
    text = read(RESULT_DOC)
    required = [
        "CONTACT_CREATION_FLOW_STATUS=NOT_APPROVED_FOR_REAL_CONTACT_DATA_TEST",
        "LEAD_TASK_CUSTOMER_CREATION_STATUS=NOT_EXECUTED_PENDING_CONTACT_FLOW_APPROVAL",
        "Production contact-flow test executed: NO",
        "Lead/task/customer creation executed: NO",
    ]
    missing = [item for item in required if item not in text]
    forbidden = [
        "CONTACT_CREATION_FLOW_STATUS=APPROVED",
        "LEAD_TASK_CUSTOMER_CREATION_STATUS=EXECUTED",
        "Production contact-flow test executed: YES",
    ]
    findings = [item for item in forbidden if item in text]
    return Check("Contact-flow remains unapproved and unexecuted", not missing and not findings, ", ".join(missing + findings))


def consent_copy_present() -> Check:
    text = read(RESULT_DOC)
    required = ["Georgian:", "English:", "კონფიდენციალურობის პოლიტიკის", "Privacy Policy"]
    missing = [item for item in required if item not in text]
    return Check("Proposed Georgian and English consent copy exists", not missing, ", ".join(missing))


def approval_checklist_present() -> Check:
    text = read(RESULT_DOC)
    required = [
        "Official privacy URL provided",
        "Legal/privacy owner approved text",
        "Contact form fields approved",
        "Consent copy approved in Georgian",
        "Consent copy approved in English",
        "Storage destination approved",
        "CRM lead/task creation approved",
        "Synthetic contact-flow test approved",
        "Real contact-flow test approved",
        "Real-site embed approved",
    ]
    missing = [item for item in required if item not in text]
    return Check("Approval checklist covers required items", not missing, ", ".join(missing))


def public_launch_no_go() -> Check:
    text = "\n".join(read(path).lower() for path in [RESULT_DOC, PUBLIC_LAUNCH, PHASE_9AE_DOC])
    bad = ["public_launch_decision=go", "public launch: go", "public launch complete"]
    findings = [item for item in bad if item in text]
    return Check("Public launch remains NO-GO", "no-go" in text and not findings, ", ".join(findings))


def no_real_contact_details_in_doc() -> Check:
    text = read(RESULT_DOC)
    findings: list[str] = []
    for pattern in REAL_CONTACT_PATTERNS:
        findings.extend(match.group(0) for match in pattern.finditer(text))
    return Check("No real contact details are included", not findings, ", ".join(findings))


def no_real_site_or_db_actions() -> Check:
    text = read(RESULT_DOC)
    required = [
        "Real `alte.edu.ge` modified: NO",
        "Real `join.alte.edu.ge` modified: NO",
        "Production DB changed: NO",
        "Migration/seed run: NO",
    ]
    missing = [item for item in required if item not in text]
    return Check("No real-site, DB, migration, or seed action is recorded", not missing, ", ".join(missing))


def tracked_secret_files_absent() -> Check:
    tracked = set(git_lines("ls-files"))
    forbidden = [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]
    return Check("No .env or .local-secrets files are tracked", not forbidden, ", ".join(forbidden))


def run_checks() -> list[Check]:
    return [
        result_doc_exists(),
        privacy_url_pending_unless_provided(),
        contact_flow_not_approved(),
        consent_copy_present(),
        approval_checklist_present(),
        public_launch_no_go(),
        no_real_contact_details_in_doc(),
        no_real_site_or_db_actions(),
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
