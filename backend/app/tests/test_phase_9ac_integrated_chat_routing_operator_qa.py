from __future__ import annotations

import importlib
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AC_INTEGRATED_CHAT_ROUTING_OPERATOR_QA_RESULT.md"
TEST_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
TEST_HTML = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_verifier_importability() -> None:
    module = importlib.import_module("app.scripts.verify_phase_9ac_integrated_chat_routing_operator_qa")
    assert hasattr(module, "run_checks")


def test_qa_script_importability() -> None:
    module = importlib.import_module("app.scripts.production_integrated_chat_routing_operator_qa")
    assert hasattr(module, "run_qa")


def test_result_doc_status_valid() -> None:
    text = read(RESULT_DOC)
    statuses = [
        "PHASE_9AC_INTEGRATED_QA_STATUS=PASSED_PENDING_MOBILE_VISUAL_QA_PRIVACY_AND_EMBED_APPROVAL",
        "PHASE_9AC_INTEGRATED_QA_STATUS=FAILED_PENDING_ROUTING_OR_KB_FIX",
    ]
    assert sum(status in text for status in statuses) == 1


def test_forbidden_direct_contact_request_patterns_absent_from_result_doc() -> None:
    text = read(RESULT_DOC).lower()
    forbidden_patterns = [
        "type your phone",
        "enter your email",
        "send your full name",
        "provide your whatsapp",
        "მომწერეთ ტელეფონი",
        "შეიყვანეთ ელფოსტა",
    ]
    for pattern in forbidden_patterns:
        assert pattern not in text


def test_public_launch_not_complete() -> None:
    text = read(RESULT_DOC).lower()
    assert "public_launch_decision=go" not in text
    assert "public launch complete" not in text
    assert "public launch: no-go" in text or "public launch remains blocked" in text


def test_frontend_forbidden_patterns_absent() -> None:
    text = read(TEST_JS) + "\n" + read(TEST_HTML)
    for forbidden in ["/api/chat", "api.anthropic.com", "ANTHROPIC_API_KEY", "sk-ant-"]:
        assert forbidden not in text
    assert "/chat/session/start" in text
    assert "/chat/message" in text


def test_local_secrets_not_tracked() -> None:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "backend/.local-secrets"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert not [line for line in result.stdout.splitlines() if line.strip()]
