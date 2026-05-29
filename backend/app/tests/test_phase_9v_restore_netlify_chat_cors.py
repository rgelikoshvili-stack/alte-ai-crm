from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_verifier_importable() -> None:
    importlib.import_module("app.scripts.verify_phase_9v_restore_netlify_chat_cors")


def test_smoke_script_importable() -> None:
    module = importlib.import_module("app.scripts.production_netlify_public_chat_cors_smoke")
    assert module.ORIGIN == "https://nimble-croissant-2f66e8.netlify.app"


def test_frontend_uses_only_safe_backend_chat_endpoints() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in [
            ROOT / "test_site" / "alte-ai-chat-widget.js",
            ROOT / "dist" / "widget" / "alte-ai-chat-widget.js",
            ROOT / "test_site" / "alte-ai-chat-widget.html",
            ROOT / "dist" / "widget" / "alte-ai-chat-widget.html",
        ]
        if path.exists()
    )
    assert "/chat/session/start" in text
    assert "/chat/message" in text
    for forbidden in ["/chat/messages", "/api/chat", "api.anthropic.com", "ANTHROPIC_API_KEY", "sk-ant-"]:
        assert forbidden not in text


def test_result_docs_keep_launch_no_go() -> None:
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


def test_cors_middleware_documents_error_response_coverage() -> None:
    main_py = (ROOT / "backend" / "app" / "main.py").read_text(encoding="utf-8")
    assert "error responses, including backend 500s" in main_py
