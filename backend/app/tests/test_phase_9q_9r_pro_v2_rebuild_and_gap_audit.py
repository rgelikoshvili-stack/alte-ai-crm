from __future__ import annotations

import importlib
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

FINAL_WIDGET = PROJECT_ROOT / "widget" / "alte-ai-chatbot-pro-v2-safe.html"
TEST_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
TEST_HTML = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html"
ZIP_PATH = PROJECT_ROOT / "dist" / "netlify_test_site_deploy.zip"
DOCS = PROJECT_ROOT / "docs" / "deployment"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_combined_verifier_importability() -> None:
    module = importlib.import_module("app.scripts.verify_phase_9q_9r_pro_v2_rebuild_and_gap_audit")
    assert hasattr(module, "run_checks")


def test_extraction_inventory_gap_and_result_docs_exist() -> None:
    for name in [
        "PRO_V2_EXTRACTION_RESULT.md",
        "PRO_V2_UPLOADED_WIDGET_AUDIT.md",
        "PRO_V2_FINAL_UI_TARGET.md",
        "PRO_V2_FUNCTION_INVENTORY.md",
        "PRO_V2_CURRENT_PROGRAM_GAP_MATRIX.md",
        "PRO_V2_MISSING_FUNCTION_IMPLEMENTATION_PLAN.md",
        "PRO_V2_BACKEND_GAPS_REQUIRING_APPROVAL.md",
        "PHASE_9Q_9R_PRO_V2_REBUILD_AND_GAP_AUDIT_RESULT.md",
    ]:
        assert (DOCS / name).exists()


def test_final_widget_and_test_assets_have_backend_markers() -> None:
    text = read(FINAL_WIDGET) + "\n" + read(TEST_JS) + "\n" + read(TEST_HTML)
    for marker in [
        "/chat/session/start",
        "/chat/message",
        "website_chat",
        "pro_v2_safe",
        "selected_department",
        "selected_topic",
        "reset",
        "expand",
        "fullscreen",
        "close",
        "Alte AI Assistant",
        "KA",
        "EN",
    ]:
        assert marker in text


def test_test_assets_have_no_direct_ai_or_secret_patterns() -> None:
    text = read(FINAL_WIDGET) + "\n" + read(TEST_JS) + "\n" + read(TEST_HTML)
    for forbidden in ["api.anthropic.com", "ANTHROPIC_API_KEY", "sk" + "-ant", "DATABASE_URL"]:
        assert forbidden not in text


def test_deploy_zip_contains_updated_js_at_root() -> None:
    assert ZIP_PATH.exists()
    with zipfile.ZipFile(ZIP_PATH) as archive:
        names = {info.filename.replace("\\", "/") for info in archive.infolist()}
        assert "alte-ai-chat-widget.js" in names
        assert "alte-ai-chat-widget.html" in names
        assert "test_site/alte-ai-chat-widget.js" not in names
        html = archive.read("alte-ai-chat-widget.html").decode("utf-8")
        chat_source = archive.read("variants/pro-v2-chat.jsx").decode("utf-8")
        zip_text = html + "\n" + chat_source
        assert "pro_v2_safe" in zip_text
        assert "fullscreen" in zip_text or "expanded" in zip_text
        assert "closeWidget" in zip_text or "close" in zip_text


def test_launch_embed_and_browser_smoke_not_complete() -> None:
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
