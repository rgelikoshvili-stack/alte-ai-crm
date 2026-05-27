from __future__ import annotations

import re
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RUNBOOK = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9X_MANUAL_BROWSER_WORKFLOW_RUNBOOK.md"
RESULT = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9X_MANUAL_BROWSER_WORKFLOW_RESULT.md"


def read(path: str | Path) -> str:
    path = Path(path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def is_tracked(path: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", path],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def run_checks() -> dict:
    require(RUNBOOK.exists(), f"Missing runbook: {RUNBOOK}")
    require(RESULT.exists(), f"Missing result doc: {RESULT}")

    runbook = read(RUNBOOK)
    result = read(RESULT)
    docs = "\n".join(
        read(path)
        for path in [
            "README.md",
            "docs/NEXT_PHASES.md",
            "docs/deployment/PHASE_9P_PUBLIC_LAUNCH_DECISION.md",
            "docs/deployment/PHASE_9X_MANUAL_BROWSER_WORKFLOW_RESULT.md",
        ]
    )
    frontend = "\n".join(
        read(path)
        for path in [
            "test_site/alte-ai-chat-widget.js",
            "dist/widget/alte-ai-chat-widget.js",
            "widget/pro-v2.html",
            "widget/variants/pro-v2-chat.jsx",
            "frontend/app.js",
        ]
        if (PROJECT_ROOT / path).exists()
    )

    for marker in [
        "PHASE_9X_MANUAL_BROWSER_WORKFLOW_RUNBOOK_STATUS=READY_FOR_MANUAL_TEST",
        "https://nimble-croissant-2f66e8.netlify.app/join.html",
        "http://127.0.0.1:5173/",
        "Production API",
        "Create knowledge candidate",
        "Open review",
    ]:
        require(marker in runbook, f"Runbook missing marker: {marker}")

    for marker in [
        "PHASE_9X_MANUAL_BROWSER_WORKFLOW_STATUS=PENDING_MANUAL_TEST",
        "BACKEND_CHATBOT_MANUAL_BROWSER_WORKFLOW_PENDING",
        "Operator reply appears in chatbot",
        "Knowledge candidate can be created from operator reply",
    ]:
        require(marker in result, f"Result missing marker: {marker}")

    require("BACKEND_CHATBOT_MANUAL_BROWSER_WORKFLOW_PENDING" in docs, "Pending manual workflow state not recorded")

    for marker in [
        "/chat/session/start",
        "/chat/message",
        "/chat/contact",
        "/chat/messages",
        "/knowledge/operator-reply-candidates/",
        "website_chat",
        "pro_v2_safe",
        "selected_department",
        "selected_topic",
    ]:
        require(marker in frontend, f"Missing frontend/backend marker: {marker}")

    for pattern in [
        r"api\.anthropic\.com",
        r"ANTHROPIC_API_KEY",
        "sk" + r"-ant",
        r"DATABASE_URL",
        r"window\.claude\.complete",
    ]:
        require(not re.search(pattern, frontend, re.IGNORECASE), f"Forbidden frontend marker found: {pattern}")

    lower_docs = docs.lower()
    for phrase in [
        "public_launch_decision=go",
        "actual_site_embed_execution_status=executed",
        "real_domain_smoke_status=passed",
        "phase_9x_manual_browser_workflow_status=passed",
    ]:
        require(phrase not in lower_docs, f"False completion marker found: {phrase}")

    require(not is_tracked(".env"), ".env must not be tracked")
    require(not is_tracked(".local-secrets"), ".local-secrets must not be tracked")

    return {
        "status": "PASS",
        "decision_state": "BACKEND_CHATBOT_MANUAL_BROWSER_WORKFLOW_PENDING",
    }


def main() -> None:
    print(run_checks())


if __name__ == "__main__":
    main()

