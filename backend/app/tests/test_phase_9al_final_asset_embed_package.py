from __future__ import annotations

import importlib
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ASSET_MANIFEST = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AL_FINAL_ASSET_MANIFEST.md"
EMBED_PACKAGE = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AL_STAGED_EMBED_APPROVAL_PACKAGE.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AL_FINAL_ASSET_AND_STAGED_EMBED_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_9al_verifier_importability():
    verifier = importlib.import_module("app.scripts.verify_phase_9al_final_asset_embed_package")
    assert hasattr(verifier, "run_checks")


def test_phase_9al_docs_exist():
    assert ASSET_MANIFEST.exists()
    assert EMBED_PACKAGE.exists()
    assert RESULT_DOC.exists()


def test_phase_9al_asset_manifest_contains_hashes_and_urls():
    text = read(ASSET_MANIFEST)
    assert "https://alte.edu.ge/assets/alte-ai-chat-widget.js" in text
    assert "E53C4C2D9789B4BCD780D9E86B1EAA9444B81904CC3617184CC7ABCFE316D2D4" in text
    assert "0036D835E485879D77A488F9C9C6B09D3C85910B5F121759D4F8360848E6739B" in text
    assert "CC6973DEA991F08DAC4BE4D0914150985478CFA7F50347F7EE3E99011D729856" in text
    assert "ASSET_UPLOAD_EXECUTED=NO" in text


def test_phase_9al_staged_embed_package_contains_snippet_and_pages():
    text = read(EMBED_PACKAGE)
    assert '<script src="https://alte.edu.ge/assets/alte-ai-chat-widget.js" defer></script>' in text
    assert "join.alte.edu.ge" in text
    assert "admissions/program-related page" in text
    assert "Do not apply this snippet" in text


def test_phase_9al_result_statuses_are_blocked_pending_approval():
    text = read(RESULT_DOC)
    assert "PHASE_9AL_FINAL_ASSET_EMBED_STATUS=READY_PENDING_PRIVACY_ASSET_AND_EMBED_APPROVAL" in text
    assert "BACKEND_DEPLOYED_FINAL_ASSET_EMBED_PACKAGE_READY_PENDING_APPROVALS" in text
    assert "ASSET_UPLOAD_STATUS=NOT_EXECUTED_PENDING_APPROVAL" in text
    assert "STAGED_EMBED_STATUS=NOT_EXECUTED_PENDING_APPROVAL" in text
    assert "PRIVACY_URL_STATUS=PENDING" in text
    assert "CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED" in text
    assert "PUBLIC_LAUNCH_STATUS=NO_GO" in text


def test_phase_9al_public_launch_remains_no_go():
    text = read(PUBLIC_LAUNCH).lower()
    assert "public_launch_decision=go" not in text
    assert "no-go" in text


def test_phase_9al_no_secrets_or_local_secret_files_tracked():
    all_docs = "\n".join(read(path) for path in [ASSET_MANIFEST, EMBED_PACKAGE, RESULT_DOC])
    assert "DATABASE_URL=" not in all_docs
    assert "ANTHROPIC_API_KEY=" not in all_docs
    assert "sk-ant" not in all_docs
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    tracked = result.stdout.splitlines()
    assert not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]


def test_phase_9al_real_site_and_db_not_modified():
    text = read(RESULT_DOC)
    assert "REAL_ALTE_SITE_MODIFIED=NO" in text
    assert "JOIN_ALTE_SITE_MODIFIED=NO" in text
    assert "PRODUCTION_DB_MODIFIED=NO" in text
    assert "PRODUCTION_MIGRATION_RUN=NO" in text
    assert "PRODUCTION_SEED_RUN=NO" in text
