from __future__ import annotations

import importlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOCS = PROJECT_ROOT / "docs" / "deployment"
TEST_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
TEST_HTML = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html"
FINAL_WIDGET = PROJECT_ROOT / "widget" / "alte-ai-chatbot-pro-v2-safe.html"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_verifier_importability() -> None:
    module = importlib.import_module("app.scripts.verify_phase_9s_frontend_event_binding_fix")
    assert hasattr(module, "run_checks")


def test_widget_has_safe_event_binding_guard() -> None:
    text = read(TEST_HTML) + "\n" + read(FINAL_WIDGET)
    assert "function on(selectorOrElement, event, handler, options)" in text
    assert "missing event target" in text
    assert 'attach: document.getElementById("cw-attach")' in text
    assert 'voice: document.getElementById("cw-voice")' in text
    assert "el.attach.addEventListener" not in text
    assert "el.voice.addEventListener" not in text
    assert "querySelector(\"#cw-feat\").addEventListener" not in text


def test_widget_has_backend_and_pro_v2_markers() -> None:
    text = read(TEST_JS) + "\n" + read(TEST_HTML) + "\n" + read(FINAL_WIDGET)
    for marker in [
        "/chat/session/start",
        "/chat/message",
        "website_chat",
        "pro_v2_safe",
        "selected_department",
        "selected_topic",
        "cw-win",
        "cw-backdrop",
        "cw-side",
        "cw-comp",
    ]:
        assert marker in text


def test_widget_has_no_direct_provider_or_secret_patterns() -> None:
    text = read(TEST_JS) + "\n" + read(TEST_HTML) + "\n" + read(FINAL_WIDGET)
    for forbidden in [
        "api.anthropic.com",
        "ANTHROPIC_API_KEY",
        "sk" + "-ant",
        "DATABASE_URL",
        "window.claude.complete",
        '"/api/chat"',
        "'/api/chat'",
    ]:
        assert forbidden not in text


def test_browser_smoke_and_public_launch_not_complete() -> None:
    text = "\n".join(
        read(path).lower()
        for path in [
            PROJECT_ROOT / "README.md",
            PROJECT_ROOT / "docs" / "NEXT_PHASES.md",
            DOCS / "PHASE_9N_HOSTED_BROWSER_SMOKE_RESULT.md",
            DOCS / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md",
        ]
    )
    assert "hosted_browser_smoke_status=passed" not in text
    assert "public_launch_decision=go" not in text
    assert "public launch complete" not in text
    assert "actual site embed executed: yes" not in text
