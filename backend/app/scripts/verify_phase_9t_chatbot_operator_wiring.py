from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = PROJECT_ROOT / "backend"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9T_CHATBOT_OPERATOR_WIRING_RESULT.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
CHAT_ROUTES = BACKEND_ROOT / "app" / "api" / "routes_chat.py"
CHAT_SCHEMA = BACKEND_ROOT / "app" / "schemas" / "chat.py"
CHAT_SERVICE = BACKEND_ROOT / "app" / "services" / "chat_service.py"
PERMISSIONS = BACKEND_ROOT / "app" / "services" / "permission_service.py"
PRO_V2 = PROJECT_ROOT / "widget" / "pro-v2.html"
PRO_V2_CHAT = PROJECT_ROOT / "widget" / "variants" / "pro-v2-chat.jsx"
PRO_V2_MODALS = PROJECT_ROOT / "widget" / "variants" / "pro-v2-modals.jsx"
TEST_FILE = BACKEND_ROOT / "app" / "tests" / "test_phase_9t_chatbot_operator_wiring.py"
SMOKE_SCRIPT = BACKEND_ROOT / "app" / "scripts" / "local_pro_v2_operator_workflow_smoke.py"

FORBIDDEN = ["api.anthropic.com", "ANTHROPIC_API_KEY", "sk-ant-", "DATABASE_URL"]


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def contains(path: Path, markers: list[str]) -> Check:
    text = read(path)
    missing = [marker for marker in markers if marker not in text]
    return Check(f"{path.name} markers", not missing, ", ".join(missing))


def file_exists(path: Path) -> Check:
    return Check(f"{path.name} exists", path.exists(), str(path))


def no_forbidden_frontend_patterns() -> Check:
    text = "\n".join(read(path) for path in [PRO_V2, PRO_V2_CHAT, PRO_V2_MODALS] if path.exists())
    found = [pattern for pattern in FORBIDDEN if pattern in text]
    return Check("Frontend has no direct provider/secret patterns", not found, ", ".join(found))


def public_launch_not_complete() -> Check:
    text = "\n".join(read(path).lower() for path in [NEXT_PHASES, PUBLIC_LAUNCH] if path.exists())
    bad = [
        phrase
        for phrase in [
            "public_launch_decision=go",
            "public launch complete",
            "actual alte embed complete",
            "actual site embed executed: yes",
        ]
        if phrase in text
    ]
    return Check("Public launch and Alte embed are not marked complete", not bad, ", ".join(bad))


def env_not_tracked(filename: str) -> Check:
    result = subprocess.run(
        ["git", "ls-files", filename],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tracked = bool(result.stdout.strip())
    return Check(f"{filename} not tracked", not tracked)


def run_checks() -> list[Check]:
    return [
        file_exists(RESULT_DOC),
        file_exists(TEST_FILE),
        file_exists(SMOKE_SCRIPT),
        file_exists(PRO_V2),
        file_exists(PRO_V2_CHAT),
        file_exists(PRO_V2_MODALS),
        contains(RESULT_DOC, ["PHASE_9T_CHATBOT_OPERATOR_WIRING_STATUS=LOCAL_CODE_READY_PENDING_BROWSER_WORKFLOW_TEST"]),
        contains(NEXT_PHASES, ["BACKEND_LOCAL_PRO_V2_OPERATOR_WIRING_READY_PENDING_BROWSER_WORKFLOW_TEST"]),
        contains(CHAT_SCHEMA, ["ChatContactRequest", "ChatContactResponse", "ChatTranscriptMessage"]),
        contains(CHAT_ROUTES, ["/contact/{conversation_id}", "/messages/{conversation_id}"]),
        contains(CHAT_SERVICE, ["submit_chat_contact", "list_public_chat_messages", "handover_session_matches"]),
        contains(SMOKE_SCRIPT, ["chat/contact", "chat/messages", "operator", "session_id"]),
        contains(PERMISSIONS, ["/chat/contact", "/chat/messages"]),
        contains(PRO_V2, ["/chat/session/start", "/chat/message", "/chat/contact/", "/chat/messages/"]),
        contains(PRO_V2_CHAT, ["selected_department", "selected_topic", "requestBackendHandover", "pollOperatorMessages"]),
        contains(PRO_V2_MODALS, ["full_name", "phone", "email", "consent"]),
        no_forbidden_frontend_patterns(),
        public_launch_not_complete(),
        env_not_tracked(".env"),
        env_not_tracked(".local-secrets"),
    ]


def main() -> int:
    checks = run_checks()
    for check in checks:
        status = "PASS" if check.ok else "FAIL"
        detail = f" - {check.detail}" if check.detail else ""
        print(f"{status}: {check.name}{detail}")
    return 0 if all(check.ok for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
