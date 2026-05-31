from __future__ import annotations

import importlib
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AK_DIRTY_TREE_AND_EMBED_READINESS_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_9ak_verifier_importability():
    verifier = importlib.import_module("app.scripts.verify_phase_9ak_dirty_tree_embed_readiness")
    assert hasattr(verifier, "run_checks")


def test_phase_9ak_result_doc_exists_and_classifies_dirty_tree():
    text = read(RESULT_DOC)
    assert "Modified Tracked Files" in text
    assert "Untracked Files" in text
    assert "Classification" in text
    assert "Recommended action" in text
    assert "README.md" in text
    assert "frontend/package-lock.json" in text


def test_phase_9ak_embed_readiness_statuses_documented():
    text = read(RESULT_DOC)
    assert "FINAL_WIDGET_ASSET_URL_STATUS=PENDING_APPROVAL_AND_UPLOAD" in text
    assert "STAGED_REAL_SITE_EMBED_STATUS=NOT_EXECUTED_PENDING_EXPLICIT_APPROVAL" in text
    assert "REAL_DOMAIN_SMOKE_STATUS=NOT_EXECUTED_PENDING_APPROVED_EMBED" in text
    assert "PRIVACY_URL_STATUS=PENDING" in text
    assert "CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED" in text


def test_phase_9ak_public_launch_remains_no_go():
    text = read(PUBLIC_LAUNCH).lower()
    assert "public_launch_decision=go" not in text
    assert "no-go" in text


def test_phase_9ak_no_real_site_or_db_actions_marked_done():
    text = read(RESULT_DOC)
    assert "REAL_ALTE_SITE_MODIFIED=NO" in text
    assert "JOIN_ALTE_SITE_MODIFIED=NO" in text
    assert "PRODUCTION_DB_MODIFIED=NO" in text
    assert "PRODUCTION_MIGRATION_RUN=NO" in text
    assert "PRODUCTION_SEED_RUN=NO" in text


def test_phase_9ak_no_secrets_or_local_secret_files_tracked():
    text = read(RESULT_DOC)
    assert "DATABASE_URL=" not in text
    assert "ANTHROPIC_API_KEY=" not in text
    assert "sk-ant" not in text
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    tracked = result.stdout.splitlines()
    assert not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]


def test_phase_9ak_commit_scope_is_limited_to_documentation_verifier_tests():
    text = read(RESULT_DOC)
    assert "No package-locks, generated helper scripts, older screenshots, or unrelated launch docs should be committed in Phase 9AK." in text
    assert "docs/deployment/PHASE_9AK_DIRTY_TREE_AND_EMBED_READINESS_RESULT.md" in text
    assert "backend/app/scripts/verify_phase_9ak_dirty_tree_embed_readiness.py" in text
    assert "backend/app/tests/test_phase_9ak_dirty_tree_embed_readiness.py" in text
