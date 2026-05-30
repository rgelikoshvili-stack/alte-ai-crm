from __future__ import annotations

import importlib
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AD_INTEGRATED_ROUTING_FIX_RESULT.md"
TEST_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
TEST_HTML = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_9ad_verifier_importability() -> None:
    module = importlib.import_module("app.scripts.verify_phase_9ad_integrated_routing_fix")
    assert hasattr(module, "run_checks")


def test_phase_9ad_focused_smoke_importability() -> None:
    module = importlib.import_module("app.scripts.production_phase_9ad_routing_fix_smoke")
    assert hasattr(module, "run_smoke")


def test_phase_9ad_result_doc_status_valid() -> None:
    text = _read(RESULT_DOC)
    statuses = [
        "PHASE_9AD_ROUTING_FIX_STATUS=PASSED_PENDING_MOBILE_VISUAL_QA_PRIVACY_AND_EMBED_APPROVAL",
        "PHASE_9AD_ROUTING_FIX_STATUS=FAILED_PENDING_ROUTING_FIX",
    ]
    assert sum(status in text for status in statuses) == 1


def test_phase_9ad_result_doc_contact_safety_and_no_go() -> None:
    text = _read(RESULT_DOC).lower()
    assert "no phone/email/name request" in text
    assert "no lead/task/customer created" in text
    assert "public launch: no-go" in text
    assert "public_launch_decision=go" not in text


def test_phase_9ad_integrated_qa_script_marks_fixed_cases() -> None:
    text = _read(PROJECT_ROOT / "backend" / "app" / "scripts" / "production_integrated_chat_routing_operator_qa.py")
    for case_id in ["admissions_auto_route_fixed", "library_auto_route_fixed", "finance_handover_route_fixed"]:
        assert case_id in text


def test_phase_9ad_frontend_forbidden_patterns_absent() -> None:
    text = _read(TEST_JS) + "\n" + _read(TEST_HTML)
    for forbidden in ["/api/chat", "api.anthropic.com", "ANTHROPIC_API_KEY", "sk-ant-"]:
        assert forbidden not in text
    assert "/chat/session/start" in text
    assert "/chat/message" in text


def test_phase_9ad_local_secrets_not_tracked() -> None:
    result = subprocess.run(
        ["git", "ls-files", ".env", ".env.*", ".local-secrets", ".local-secrets/*", "backend/.local-secrets"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert not [line for line in result.stdout.splitlines() if line.strip()]
