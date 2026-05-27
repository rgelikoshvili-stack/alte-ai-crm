from __future__ import annotations

import re
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9W_CHATBOT_FUNCTION_AUDIT_RESULT.md"
DECISION = "BACKEND_CHATBOT_FUNCTION_AUDIT_PASSED_PENDING_MANUAL_BROWSER_WORKFLOW"
STATUS = "PHASE_9W_CHATBOT_FUNCTION_AUDIT_STATUS=AUTOMATED_FUNCTION_SMOKE_PASSED_PENDING_MANUAL_BROWSER_WORKFLOW"


def read(path: str | Path) -> str:
    path = Path(path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def git_tracked(path: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", path],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_checks() -> dict:
    require(RESULT_DOC.exists(), f"Missing result doc: {RESULT_DOC}")
    result = read(RESULT_DOC)
    docs = "\n".join(
        read(path)
        for path in [
            "README.md",
            "docs/NEXT_PHASES.md",
            "docs/deployment/PHASE_9W_CHATBOT_FUNCTION_AUDIT_RESULT.md",
            "docs/deployment/PHASE_9P_PUBLIC_LAUNCH_DECISION.md",
        ]
    )
    frontend = "\n".join(
        read(path)
        for path in [
            "test_site/alte-ai-chat-widget.js",
            "dist/widget/alte-ai-chat-widget.js",
            "widget/pro-v2.html",
            "widget/variants/pro-v2-chat.jsx",
            "widget/variants/pro-v2-modals.jsx",
            "frontend/app.js",
        ]
        if (PROJECT_ROOT / path).exists()
    )

    for marker in [
        STATUS,
        "Session payload smoke | 2/2 PASS",
        "Test site API smoke | 10/10 PASS",
        "CORS smoke | 10/10 PASS",
        "Security/reliability smoke | 16/16 PASS",
        "Department routing/sidebar smoke | 28/28 PASS",
        "Finance no-contact smoke | 24/24 PASS",
        "Knowledge smoke | 25/25 PASS",
        "Local operator workflow smoke | 5/5 PASS",
        "Phase 9T/9U/9V targeted tests | 18 passed",
        DECISION,
    ]:
        require(marker in result, f"Missing result marker: {marker}")

    require(DECISION in docs, "Decision state not recorded in status docs")

    for marker in [
        "/chat/session/start",
        "/chat/message",
        "website_chat",
        "pro_v2_safe",
        "selected_department",
        "selected_topic",
        "/chat/contact",
        "/chat/messages",
        "/knowledge/operator-reply-candidates/",
    ]:
        require(marker in frontend, f"Missing functional marker: {marker}")

    forbidden = [
        r"api\.anthropic\.com",
        r"ANTHROPIC_API_KEY",
        "sk" + r"-ant",
        r"DATABASE_URL",
        r"window\.claude\.complete",
    ]
    for pattern in forbidden:
        require(not re.search(pattern, frontend, re.IGNORECASE), f"Forbidden frontend marker found: {pattern}")

    lower_docs = docs.lower()
    for phrase in [
        "public_launch_decision=go",
        "actual_site_embed_execution_status=executed",
        "real_domain_smoke_status=passed",
    ]:
        require(phrase not in lower_docs, f"Launch/embed falsely marked: {phrase}")

    require(not git_tracked(".env"), ".env must not be tracked")
    require(not git_tracked(".local-secrets"), ".local-secrets must not be tracked")

    return {
        "status": "PASS",
        "decision_state": DECISION,
    }


def main() -> None:
    print(run_checks())


if __name__ == "__main__":
    main()

