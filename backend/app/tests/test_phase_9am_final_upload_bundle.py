from __future__ import annotations

import importlib
import subprocess
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BUNDLE_DIR = PROJECT_ROOT / "dist" / "final_alte_widget_upload"
ZIP_PATH = PROJECT_ROOT / "dist" / "final_alte_widget_upload.zip"
MANIFEST = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AM_FINAL_UPLOAD_BUNDLE_MANIFEST.md"
SMOKE_CHECKLIST = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AM_REAL_DOMAIN_SMOKE_CHECKLIST.md"
ROLLBACK_PLAN = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AM_REAL_SITE_ROLLBACK_PLAN.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AM_FINAL_UPLOAD_BUNDLE_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
REQUIRED_ZIP_FILES = {
    "alte-ai-chat-widget.js",
    "alte-ai-chat-widget.html",
    "variants/pro-v2-chat.jsx",
    "variants/pro-v2-icons.jsx",
    "variants/pro-v2-modals.jsx",
    "variants/pro-v2-page.jsx",
    "variants/pro-v2-strings.jsx",
    "variants/tweaks-panel.jsx",
}
MOJIBAKE_MARKER = "\u00e1\u0192"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_9am_verifier_importability():
    verifier = importlib.import_module("app.scripts.verify_phase_9am_final_upload_bundle")
    assert hasattr(verifier, "run_checks")


def test_phase_9am_bundle_directory_and_zip_exist():
    assert BUNDLE_DIR.exists()
    assert ZIP_PATH.exists()
    assert (BUNDLE_DIR / "alte-ai-chat-widget.js").exists()
    assert (BUNDLE_DIR / "alte-ai-chat-widget.html").exists()
    assert (BUNDLE_DIR / "variants" / "pro-v2-chat.jsx").exists()


def test_phase_9am_zip_root_contains_required_files_exactly():
    with zipfile.ZipFile(ZIP_PATH) as archive:
        entries = {info.filename.replace("\\", "/").rstrip("/") for info in archive.infolist() if not info.is_dir()}
    assert entries == REQUIRED_ZIP_FILES


def test_phase_9am_manifest_contains_hashes_and_production_paths():
    text = read(MANIFEST)
    assert "dist/final_alte_widget_upload/" in text
    assert "dist/final_alte_widget_upload.zip" in text
    assert "EEE750AA2E960BECC71E840C75C57D58C4E02CECAE63AAD8C72769A87F32FE2A" in text
    assert "/assets/alte-ai-chat-widget.js" in text
    assert "/assets/variants/pro-v2-chat.jsx" in text
    assert "0036D835E485879D77A488F9C9C6B09D3C85910B5F121759D4F8360848E6739B" in text


def test_phase_9am_bundle_consistency_and_forbidden_patterns():
    text = "\n".join(path.read_text(encoding="utf-8") for path in BUNDLE_DIR.rglob("*") if path.is_file())
    assert "https://alte-ai-crm-backend-226875230147.europe-west1.run.app" in text
    assert "alte-ai-chat-widget.html" in text
    assert "variants/pro-v2-chat.jsx" in text
    assert "api.anthropic.com" not in text
    assert "ANTHROPIC_API_KEY" not in text
    assert "sk-ant" not in text
    assert "/api/chat" not in text
    assert "127.0.0.1" not in text
    assert "localhost" not in text
    assert MOJIBAKE_MARKER not in text


def test_phase_9am_smoke_and_rollback_docs_exist_and_are_blocked():
    smoke = read(SMOKE_CHECKLIST)
    rollback = read(ROLLBACK_PLAN)
    result = read(RESULT_DOC)
    assert "join.alte.edu.ge" in smoke
    assert "Bachelor completion question returns `240 ECTS`, not `180`" in smoke
    assert "Remove the widget loader script" in rollback
    assert "REAL_SITE_ROLLBACK_EXECUTED=NO" in rollback
    assert "PHASE_9AM_FINAL_UPLOAD_BUNDLE_STATUS=READY_PENDING_ASSET_UPLOAD_AND_EMBED_APPROVAL" in result
    assert "ASSET_UPLOAD_STATUS=NOT_EXECUTED_PENDING_APPROVAL" in result
    assert "STAGED_EMBED_STATUS=NOT_EXECUTED_PENDING_APPROVAL" in result


def test_phase_9am_public_launch_no_go_and_no_local_secrets_tracked():
    public = read(PUBLIC_LAUNCH).lower()
    docs = "\n".join(read(path) for path in [MANIFEST, SMOKE_CHECKLIST, ROLLBACK_PLAN, RESULT_DOC])
    assert "public_launch_decision=go" not in public
    assert "no-go" in public
    assert "DATABASE_URL=" not in docs
    assert "ANTHROPIC_API_KEY=" not in docs
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    tracked = result.stdout.splitlines()
    assert not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]
