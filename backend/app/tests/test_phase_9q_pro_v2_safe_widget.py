from __future__ import annotations

import importlib
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

FINAL_WIDGET = PROJECT_ROOT / "widget" / "alte-ai-chatbot-pro-v2-safe.html"
DIST_JS = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js"
TEST_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
ZIP_PATH = PROJECT_ROOT / "dist" / "netlify_test_site_deploy.zip"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9Q_PRO_V2_SAFE_WIDGET_ADAPTATION_RESULT.md"
HOSTED_SMOKE = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_HOSTED_BROWSER_SMOKE_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_verifier_importability() -> None:
    module = importlib.import_module("app.scripts.verify_phase_9q_pro_v2_safe_widget")
    assert hasattr(module, "run_checks")


def test_final_pro_v2_assets_exist() -> None:
    assert FINAL_WIDGET.exists()
    assert DIST_JS.exists()
    assert TEST_JS.exists()
    assert RESULT_DOC.exists()


def test_widget_backend_contract_markers() -> None:
    text = "\n".join(read(path) for path in [FINAL_WIDGET, DIST_JS, TEST_JS])
    for marker in [
        "/chat/session/start",
        "/chat/message",
        "source_domain",
        "language",
        "widget_variant",
        "selected_department",
        "selected_topic",
        "pro_v2_safe",
    ]:
        assert marker in text


def test_widget_assets_have_no_direct_provider_or_secret_patterns() -> None:
    text = "\n".join(read(path) for path in [FINAL_WIDGET, DIST_JS, TEST_JS])
    forbidden = ["api.anthropic.com", "ANTHROPIC_API_KEY", "sk-ant-", "DATABASE_URL"]
    for item in forbidden:
        assert item not in text


def test_deploy_zip_contains_updated_widget_assets() -> None:
    assert ZIP_PATH.exists()
    with zipfile.ZipFile(ZIP_PATH) as archive:
        names = {info.filename.replace("\\", "/") for info in archive.infolist()}
        assert "alte-ai-chat-widget.js" in names
        assert "alte-ai-chat-widget.html" in names
        assert "test_site/alte-ai-chat-widget.js" not in names
        html = archive.read("alte-ai-chat-widget.html").decode("utf-8")
        assert "pro_v2_safe" in html
        assert "/chat/session/start" in html
        assert "/chat/message" in html


def test_public_launch_and_browser_smoke_not_falsely_complete() -> None:
    text = (read(PUBLIC_LAUNCH) + "\n" + read(HOSTED_SMOKE)).lower()
    assert "public_launch_decision=go" not in text
    assert "public launch complete" not in text
    assert "hosted_browser_smoke_status=passed" not in text
    assert "hosted browser smoke: passed" not in text
