from __future__ import annotations

import importlib
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
HANDOFF_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AN_OWNER_APPROVAL_HANDOFF.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AN_OWNER_APPROVAL_HANDOFF_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
REQUIRED_ASSET_PATHS = [
    "/assets/alte-ai-chat-widget.js",
    "/assets/alte-ai-chat-widget.html",
    "/assets/variants/pro-v2-chat.jsx",
    "/assets/variants/pro-v2-icons.jsx",
    "/assets/variants/pro-v2-modals.jsx",
    "/assets/variants/pro-v2-page.jsx",
    "/assets/variants/pro-v2-strings.jsx",
    "/assets/variants/tweaks-panel.jsx",
]
EMBED_SNIPPET = '<script src="https://alte.edu.ge/assets/alte-ai-chat-widget.js" defer></script>'
SECRET_PATTERNS = [
    "DATABASE_URL=",
    "ANTHROPIC_API_KEY=",
    "sk-ant",
    "password=",
    "token=",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def combined_docs() -> str:
    return "\n".join([read(HANDOFF_DOC), read(RESULT_DOC)])


def test_phase_9an_verifier_importability():
    verifier = importlib.import_module("app.scripts.verify_phase_9an_owner_approval_handoff")
    assert hasattr(verifier, "run_checks")


def test_phase_9an_handoff_and_result_docs_exist():
    assert HANDOFF_DOC.exists()
    assert RESULT_DOC.exists()
    text = combined_docs()
    assert "PHASE_9AN_OWNER_APPROVAL_HANDOFF_STATUS=READY_PENDING_OWNER_APPROVAL" in text
    assert "BACKEND_DEPLOYED_OWNER_HANDOFF_READY_PENDING_APPROVALS" in text


def test_phase_9an_required_asset_paths_exist_in_docs():
    text = combined_docs()
    assert "dist/final_alte_widget_upload.zip" in text
    assert "EEE750AA2E960BECC71E840C75C57D58C4E02CECAE63AAD8C72769A87F32FE2A" in text
    for path in REQUIRED_ASSET_PATHS:
        assert path in text


def test_phase_9an_embed_snippet_exists_in_docs():
    text = combined_docs()
    assert EMBED_SNIPPET in text
    assert "join.alte.edu.ge" in text
    assert "admissions/program-related page" in text


def test_phase_9an_upload_and_embed_are_not_marked_executed():
    text = combined_docs()
    assert "ASSET_UPLOAD_STATUS=NOT_EXECUTED_PENDING_APPROVAL" in text
    assert "STAGED_EMBED_STATUS=NOT_EXECUTED_PENDING_APPROVAL" in text
    assert "ASSET_UPLOAD_EXECUTED=YES" not in text
    assert "STAGED_EMBED_EXECUTED=YES" not in text
    assert "REAL_ALTE_SITE_MODIFIED=NO" in text
    assert "JOIN_ALTE_SITE_MODIFIED=NO" in text


def test_phase_9an_public_launch_no_go():
    text = combined_docs()
    public = read(PUBLIC_LAUNCH).lower()
    assert "PUBLIC_LAUNCH_STATUS=NO_GO" in text
    assert "public_launch_decision=go" not in public
    assert "no-go" in public


def test_phase_9an_no_secrets_or_real_contact_data():
    text = combined_docs()
    assert all(pattern not in text for pattern in SECRET_PATTERNS)
    assert "REAL_CONTACT_DATA_SENT=NO" in text
    assert "LEAD_TASK_CUSTOMER_CREATED=NO" in text
    assert "LEAD_CUSTOMER_TASK_CREATED=YES" not in text
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    tracked = result.stdout.splitlines()
    assert not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]

