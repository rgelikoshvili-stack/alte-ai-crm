from __future__ import annotations

import importlib
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOCS = PROJECT_ROOT / "docs" / "deployment"
ZIP_EVIDENCE = PROJECT_ROOT / "docs" / "knowledge_evidence" / "uploaded_pro_v2_zip_source"
FINAL_WIDGET = PROJECT_ROOT / "widget" / "alte-ai-chatbot-pro-v2-safe.html"
TEST_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
TEST_HTML = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html"
ZIP_PATH = PROJECT_ROOT / "dist" / "netlify_test_site_deploy.zip"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_verifier_importability() -> None:
    module = importlib.import_module("app.scripts.verify_phase_9s_exact_zip_source_port")
    assert hasattr(module, "run_checks")


def test_zip_source_evidence_exists() -> None:
    assert (ZIP_EVIDENCE / "deploy" / "variants" / "pro-v2-chat.jsx").exists()
    assert (ZIP_EVIDENCE / "deploy" / "variants" / "pro-v2-strings.jsx").exists()
    assert (ZIP_EVIDENCE / "deploy" / "variants" / "pro-v2-icons.jsx").exists()
    assert (ZIP_EVIDENCE / "deploy" / "variants" / "pro-v2-modals.jsx").exists()


def test_final_widget_contains_backend_and_zip_visual_markers() -> None:
    text = read(FINAL_WIDGET) + "\n" + read(TEST_JS) + "\n" + read(TEST_HTML)
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
        "cw-side collapsed",
        "settings",
        "expand",
        "close",
    ]:
        assert marker in text


def test_final_widget_has_no_direct_provider_or_secret_patterns() -> None:
    text = read(FINAL_WIDGET) + "\n" + read(TEST_JS) + "\n" + read(TEST_HTML)
    for forbidden in ["api.anthropic.com", "ANTHROPIC_API_KEY", "sk" + "-ant", "DATABASE_URL", "window.claude.complete", '"/api/chat"', "'/api/chat'"]:
        assert forbidden not in text


def test_deploy_zip_contains_updated_widget_at_root() -> None:
    assert ZIP_PATH.exists()
    with zipfile.ZipFile(ZIP_PATH) as archive:
        names = {info.filename.replace("\\", "/") for info in archive.infolist()}
        assert "alte-ai-chat-widget.js" in names
        assert "alte-ai-chat-widget.html" in names
        assert "test_site/alte-ai-chat-widget.js" not in names
        html = archive.read("alte-ai-chat-widget.html").decode("utf-8")
        chat_source = archive.read("variants/pro-v2-chat.jsx").decode("utf-8")
        zip_text = html + "\n" + chat_source
        assert "cw-win" in zip_text
        assert "cw-backdrop" in zip_text
        assert "pro_v2_safe" in html


def test_public_launch_browser_smoke_and_embed_not_complete() -> None:
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
