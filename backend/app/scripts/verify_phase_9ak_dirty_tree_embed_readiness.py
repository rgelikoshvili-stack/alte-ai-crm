from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AK_DIRTY_TREE_AND_EMBED_READINESS_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
TEST_SITE_FILES = [
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html",
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-chat.jsx",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-modals.jsx",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-strings.jsx",
]
SECRET_PATTERNS = [
    "DATABASE_URL=",
    "ANTHROPIC_API_KEY=",
    "sk-ant",
    "password=",
    "token=",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    return result.stdout.splitlines()


def check(name: str, passed: bool, detail: str = "") -> tuple[str, bool, str]:
    print(f"{'PASS' if passed else 'FAIL'} {name}: {detail}")
    return name, passed, detail


def run_checks() -> list[tuple[str, bool, str]]:
    doc_text = read(RESULT_DOC) if RESULT_DOC.exists() else ""
    public_text = read(PUBLIC_LAUNCH).lower() if PUBLIC_LAUNCH.exists() else ""
    frontend_text = "\n".join(read(path) for path in TEST_SITE_FILES if path.exists())
    tracked = tracked_files()
    return [
        check("result doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
        check("dirty tree classification exists", all(value in doc_text for value in ["Modified Tracked Files", "Untracked Files", "Classification", "Recommended action"])),
        check("public launch remains NO-GO", "public_launch_decision=go" not in public_text and "no-go" in public_text),
        check("privacy URL pending unless provided", "PRIVACY_URL_STATUS=PENDING" in doc_text or "PRIVACY_URL_STATUS=PROVIDED_PENDING_APPROVAL" in doc_text),
        check("contact-flow not approved", "CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED" in doc_text),
        check("real site not modified", "REAL_ALTE_SITE_MODIFIED=NO" in doc_text and "JOIN_ALTE_SITE_MODIFIED=NO" in doc_text),
        check("env/local-secrets are not tracked", not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]),
        check("no secrets in 9AK doc", all(pattern not in doc_text for pattern in SECRET_PATTERNS)),
        check("frontend does not expose API keys", all(value not in frontend_text for value in ["ANTHROPIC_API_KEY", "sk-ant"])),
        check("frontend uses backend endpoints only", all(value in frontend_text for value in ["/chat/session/start", "/chat/message"])),
        check("final asset URL status documented", "FINAL_WIDGET_ASSET_URL_STATUS=PENDING_APPROVAL_AND_UPLOAD" in doc_text),
        check("real-domain smoke pending", "REAL_DOMAIN_SMOKE_STATUS=NOT_EXECUTED_PENDING_APPROVED_EMBED" in doc_text),
        check("no lead/task/customer created", "LEAD_TASK_CUSTOMER_CREATED=NO" in doc_text),
    ]


def main() -> int:
    checks = run_checks()
    return 0 if all(passed for _, passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
