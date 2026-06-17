from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_verifier_importable() -> None:
    importlib.import_module("app.scripts.verify_phase_9s_message_500_fix")


def test_production_smoke_importable() -> None:
    importlib.import_module("app.scripts.production_chat_message_smoke")


def test_frontend_uses_approved_chat_endpoints() -> None:
    text = (ROOT / "test_site" / "alte-ai-chat-widget.html").read_text(encoding="utf-8", errors="ignore")
    assert "/chat/session/start" in text
    assert "/chat/message" in text
    assert "/api/chat" not in text
    assert "api.anthropic.com" not in text
    assert "ANTHROPIC_API_KEY" not in text
    assert "sk-ant-" not in text
    assert "DATABASE_URL" not in text
    assert "window.claude.complete" not in text


def test_message_payload_fields_present() -> None:
    text = (ROOT / "test_site" / "alte-ai-chat-widget.html").read_text(encoding="utf-8", errors="ignore")
    for marker in [
        "conversation_id",
        "session_id",
        "message",
        "source_domain",
        "language",
        "selected_department",
        "selected_topic",
        "page_url",
        "widget_variant",
        "pro_v2_safe",
        "website_chat",
    ]:
        assert marker in text


def test_handover_not_automatic_for_normal_typed_message() -> None:
    variant = (ROOT / "test_site" / "variants" / "pro-v2-chat.jsx").read_text(encoding="utf-8", errors="ignore")
    assert "/chat/handover automatically from a normal typed message" in variant
    assert "requestBackendHandover(currentDept, requestText)" in variant


def test_visible_error_renderer_present() -> None:
    variant = (ROOT / "test_site" / "variants" / "pro-v2-chat.jsx").read_text(encoding="utf-8", errors="ignore")
    assert "ვერ მივიღე პასუხი. სცადეთ თავიდან ან მიმართეთ ოპერატორს." in variant
    assert "Could not get an answer. Please try again or contact an operator." in variant


def test_public_launch_and_browser_smoke_not_marked_complete() -> None:
    docs = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in [
            ROOT / "README.md",
            ROOT / "docs" / "NEXT_PHASES.md",
            ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md",
        ]
        if path.exists()
    )
    assert "PUBLIC_LAUNCH_DECISION=GO_APPROVED_FOR_PUBLIC_LAUNCH" not in docs
    assert "HOSTED_BROWSER_SMOKE_STATUS=PASSED" not in docs
