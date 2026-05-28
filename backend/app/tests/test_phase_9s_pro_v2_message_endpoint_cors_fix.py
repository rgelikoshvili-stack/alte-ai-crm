import importlib
from pathlib import Path
import zipfile


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TEST_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
DIST_JS = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js"
TEST_HTML = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html"
DIST_HTML = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.html"
SAFE_WIDGET = PROJECT_ROOT / "widget" / "alte-ai-chatbot-pro-v2-safe.html"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9S_PRO_V2_MESSAGE_ENDPOINT_CORS_FIX_RESULT.md"
ZIP_PATH = PROJECT_ROOT / "dist" / "netlify_test_site_deploy.zip"


def frontend_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in [TEST_JS, DIST_JS, TEST_HTML, DIST_HTML, SAFE_WIDGET])


def test_verifier_and_cors_smoke_importable():
    assert hasattr(importlib.import_module("app.scripts.verify_phase_9s_pro_v2_message_endpoint_cors_fix"), "run_checks")
    assert hasattr(importlib.import_module("app.scripts.production_netlify_pro_v2_cors_smoke"), "run_smoke")


def test_frontend_uses_approved_chat_endpoints_only():
    text = frontend_text()
    assert "/chat/session/start" in text
    assert "/chat/message" in text
    assert "/chat/messages" not in text
    assert "/api/chat" not in text


def test_frontend_has_backend_payload_markers():
    text = frontend_text()
    assert "website_chat" in text
    assert "pro_v2_safe" in text
    assert "selected_department" in text
    assert "selected_topic" in text


def test_frontend_has_no_direct_anthropic_or_secret_patterns():
    text = frontend_text()
    for forbidden in ["api.anthropic.com", "ANTHROPIC_API_KEY", "sk-ant-", "DATABASE_URL"]:
        assert forbidden not in text


def test_result_doc_keeps_launch_and_browser_smoke_blocked():
    text = RESULT_DOC.read_text(encoding="utf-8", errors="ignore")
    assert "PHASE_9S_PRO_V2_MESSAGE_ENDPOINT_CORS_FIX_STATUS=READY_PENDING_NETLIFY_REDEPLOY_AND_BROWSER_RETEST" in text
    assert "browser smoke pending manual retest" in text.lower()
    assert "public launch: NO" in text or "Public launch: NO" in text
    assert "HOSTED_BROWSER_SMOKE_STATUS=PASSED" not in text


def test_netlify_zip_contains_updated_widget_files_at_root():
    assert ZIP_PATH.exists()
    with zipfile.ZipFile(ZIP_PATH) as archive:
        names = set(archive.namelist())
        js_text = archive.read("alte-ai-chat-widget.html").decode("utf-8", errors="ignore")
    assert "index.html" in names
    assert "join.html" in names
    assert "alte-ai-chat-widget.js" in names
    assert "alte-ai-chat-widget.html" in names
    assert "_redirects" in names
    assert not any(name.startswith("test_site/") for name in names)
    assert "/chat/message" in js_text
    assert "/chat/messages" not in js_text
