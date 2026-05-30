from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check(condition: bool, message: str, failures: list[str]) -> None:
    print(("PASS " if condition else "FAIL ") + message)
    if not condition:
        failures.append(message)


def git_tracked(path: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", path],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return result.returncode == 0


def main() -> int:
    failures: list[str] = []
    diagnosis_script = BACKEND / "app" / "scripts" / "production_chat_session_start_500_diagnosis.py"
    root_cause_doc = ROOT / "docs" / "deployment" / "PHASE_9W_SESSION_START_500_ROOT_CAUSE.md"
    result_doc = ROOT / "docs" / "deployment" / "PHASE_9W_CHAT_SESSION_START_500_FIX_RESULT.md"
    approval_doc = ROOT / "docs" / "deployment" / "PHASE_9W_SECRET_OR_DB_CREDENTIAL_APPROVAL_REQUIRED.md"
    test_file = BACKEND / "app" / "tests" / "test_phase_9w_chat_session_start_500_fix.py"
    schemas = read(BACKEND / "app" / "schemas" / "chat.py")
    service = read(BACKEND / "app" / "services" / "chat_service.py")
    test_js = read(ROOT / "test_site" / "alte-ai-chat-widget.js")
    dist_js = read(ROOT / "dist" / "widget" / "alte-ai-chat-widget.js")
    result = read(result_doc) if result_doc.exists() else ""
    root_cause = read(root_cause_doc) if root_cause_doc.exists() else ""
    docs_bundle = "\n".join(
        read(path)
        for path in [
            ROOT / "README.md",
            ROOT / "docs" / "NEXT_PHASES.md",
            ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md",
            result_doc,
        ]
        if path.exists()
    )

    check(diagnosis_script.exists(), "diagnosis script exists", failures)
    check(root_cause_doc.exists(), "root cause doc exists", failures)
    check(result_doc.exists(), "result doc exists", failures)
    check(approval_doc.exists(), "approval-required doc exists", failures)
    check(test_file.exists(), "tests exist", failures)
    check("website_chat" in schemas, "session schema supports website_chat", failures)
    check("widget_variant" in schemas, "session schema supports widget_variant", failures)
    check("metadata" in schemas, "session schema supports metadata", failures)
    check("source_domain" in schemas, "session schema supports source_domain", failures)
    check("widget_variant" in service and "metadata" in service, "session start persists safe metadata", failures)
    for marker in ["/chat/session/start", "/chat/message"]:
        check(marker in test_js and marker in dist_js, f"frontend uses {marker}", failures)
    for forbidden in ["/chat/messages", "/api/chat", "api.anthropic.com", "ANTHROPIC_API_KEY", "sk-ant-"]:
        check(forbidden not in test_js and forbidden not in dist_js, f"frontend excludes {forbidden}", failures)
    check("asyncpg.exceptions.InvalidPasswordError" in root_cause, "root cause records sanitized DB auth exception", failures)
    check(
        "PHASE_9W_CHAT_SESSION_START_STATUS=BLOCKED_PENDING_DB_OR_SECRET_APPROVAL" in result,
        "result records blocked pending approval",
        failures,
    )
    check(
        "BACKEND_DEPLOYED_CHAT_SESSION_START_500_DIAGNOSED_PENDING_APPROVAL" in docs_bundle,
        "docs contain Phase 9W decision state",
        failures,
    )
    lowered_docs = docs_bundle.lower()
    check("public launch: no" in lowered_docs or "public launch remains no-go" in lowered_docs, "public launch remains NO-GO", failures)
    check("actual alte embed complete" not in lowered_docs, "docs do not mark real Alte embed complete", failures)
    check(not git_tracked(".env"), ".env not tracked", failures)
    check(not git_tracked(".local-secrets"), ".local-secrets not tracked", failures)

    if failures:
        print("verify_phase_9w_chat_session_start_fix=FAIL")
        return 1
    print("verify_phase_9w_chat_session_start_fix=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
