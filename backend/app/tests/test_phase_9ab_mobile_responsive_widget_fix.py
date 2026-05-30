from __future__ import annotations

import importlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AB_MOBILE_RESPONSIVE_WIDGET_FIX_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
PHASE_9AD_RESULT = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AD_INTEGRATED_ROUTING_FIX_RESULT.md"
TEST_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
TEST_CHAT = PROJECT_ROOT / "test_site" / "variants" / "pro-v2-chat.jsx"
WIDGET_CHAT = PROJECT_ROOT / "widget" / "variants" / "pro-v2-chat.jsx"
TEST_JOIN = PROJECT_ROOT / "test_site" / "join.html"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_verifier_importability() -> None:
    module = importlib.import_module("app.scripts.verify_phase_9ab_mobile_responsive_widget_fix")
    assert hasattr(module, "run_checks")


def test_visual_qa_script_importability() -> None:
    module = importlib.import_module("app.scripts.visual_qa_netlify_widget")
    assert hasattr(module, "run_visual_qa")


def test_result_doc_status_is_valid() -> None:
    text = read(RESULT_DOC)
    valid_statuses = [
        "PHASE_9AB_MOBILE_RESPONSIVE_STATUS=FIXED_PENDING_NETLIFY_REDEPLOY_AND_VISUAL_QA",
        "PHASE_9AB_MOBILE_RESPONSIVE_STATUS=PASSED_PENDING_PRIVACY_AND_EMBED_APPROVAL",
        "PHASE_9AB_MOBILE_RESPONSIVE_STATUS=FAILED_PENDING_LAYOUT_FIX",
        "PHASE_9AB_MOBILE_RESPONSIVE_STATUS=BLOCKED_NETLIFY_REDEPLOY_REQUIRED",
    ]
    assert sum(status in text for status in valid_statuses) == 1


def test_frontend_forbidden_patterns_absent() -> None:
    text = "\n".join(read(path) for path in [TEST_JS, TEST_JOIN, TEST_CHAT, WIDGET_CHAT])
    for forbidden in ["/api/chat", "api.anthropic.com", "ANTHROPIC_API_KEY", "sk-ant-"]:
        assert forbidden not in text


def test_frontend_backend_contract_intact() -> None:
    text = read(TEST_JS)
    assert "/chat/session/start" in text
    assert "/chat/message" in text


def test_public_launch_not_complete_and_real_site_not_modified() -> None:
    text = (read(PUBLIC_LAUNCH) + "\n" + read(RESULT_DOC)).lower()
    assert "public_launch_decision=go" not in text
    assert "public launch complete" not in text
    assert "public launch: no-go" in text or "public launch remains no-go" in text
    assert "real alte site modified: no" in text
    assert "real join.alte.edu.ge modified: no" in text


def test_integrated_qa_state_not_downgraded() -> None:
    text = read(PHASE_9AD_RESULT) + "\n" + read(RESULT_DOC)
    assert (
        "BACKEND_DEPLOYED_INTEGRATED_CHAT_ROUTING_QA_PASSED_PENDING_FINAL_APPROVALS" in text
        or "18/18 passed" in text
    )


def test_responsive_css_contains_mobile_guard() -> None:
    text = read(TEST_CHAT) + "\n" + read(WIDGET_CHAT)
    assert (
        "@media (max-width: 1024px)" in text
        or "@media (max-width: 900px)" in text
        or "@media (max-width: 640px)" in text
    )
    assert "max-width:calc(100vw - 16px)" in text
    assert ".cw-win.expanded .cw-side" in text
