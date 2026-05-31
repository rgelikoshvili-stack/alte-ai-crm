from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AJ_PRIVACY_CONTACT_FLOW_FINALIZATION_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
TEST_SITE_FILES = [
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html",
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-chat.jsx",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-modals.jsx",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-strings.jsx",
]
MOJIBAKE_MARKER = "\u00e1\u0192"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    return result.stdout.splitlines()


def check(name: str, passed: bool, detail: str = "") -> tuple[str, bool, str]:
    print(f"{'PASS' if passed else 'FAIL'} {name}: {detail}")
    return name, passed, detail


def extract_status(text: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}=([A-Z0-9_]+)$", text, re.MULTILINE)
    return match.group(1) if match else None


def run_checks() -> list[tuple[str, bool, str]]:
    doc_text = read(RESULT_DOC) if RESULT_DOC.exists() else ""
    public_text = read(PUBLIC_LAUNCH).lower() if PUBLIC_LAUNCH.exists() else ""
    frontend_text = "\n".join(read(path) for path in TEST_SITE_FILES if path.exists())
    tracked = tracked_files()
    privacy_status = extract_status(doc_text, "PRIVACY_URL_STATUS")
    contact_status = extract_status(doc_text, "CONTACT_FLOW_APPROVAL_STATUS")
    test_status = extract_status(doc_text, "CONTACT_DATA_TEST_STATUS")
    launch_status = extract_status(doc_text, "PUBLIC_LAUNCH_STATUS")
    valid_privacy_statuses = {"PENDING", "PROVIDED_PENDING_APPROVAL"}
    valid_contact_statuses = {"NOT_APPROVED"}
    return [
        check("result doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
        check("privacy status is valid", privacy_status in valid_privacy_statuses, str(privacy_status)),
        check("contact-flow not approved", contact_status in valid_contact_statuses, str(contact_status)),
        check("contact data test not executed", test_status == "NOT_EXECUTED", str(test_status)),
        check("public launch status NO_GO", launch_status == "NO_GO", str(launch_status)),
        check("Georgian consent copy exists", "ვეთანხმები, რომ ჩემი საკონტაქტო ინფორმაცია" in doc_text),
        check("English consent copy exists", "I agree that my contact information may be used only" in doc_text),
        check("contact form fields documented", all(value in doc_text for value in ["name", "phone", "language", "email", "interest/department", "question/message", "consent checkbox"])),
        check("lead/task/customer creation not executed", "LEAD_TASK_CUSTOMER_CREATED=NO" in doc_text and "LEAD_TASK_CUSTOMER_CREATION_EXECUTED=NO" in doc_text),
        check("real contact flow not executed", "CONTACT_FLOW_EXECUTED=NO" in doc_text and "REAL_CONTACT_DATA_SENT=NO" in doc_text),
        check("public launch remains NO-GO", "public_launch_decision=go" not in public_text and "no-go" in public_text),
        check("no real contact details in doc", all(value not in doc_text for value in ["@gmail.com", "+995", "555-", "599-"])),
        check("env/local-secrets are not tracked", not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]),
        check("frontend does not expose API keys", all(value not in frontend_text for value in ["ANTHROPIC_API_KEY", "sk-ant"])),
        check("frontend does not call api.anthropic.com", "api.anthropic.com" not in frontend_text),
        check("frontend uses backend endpoints only", all(value in frontend_text for value in ["/chat/session/start", "/chat/message"])),
        check("no mojibake marker", MOJIBAKE_MARKER not in doc_text + frontend_text),
        check("real Alte site not modified", "REAL_ALTE_SITE_MODIFIED=NO" in doc_text),
    ]


def main() -> int:
    checks = run_checks()
    return 0 if all(passed for _, passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
