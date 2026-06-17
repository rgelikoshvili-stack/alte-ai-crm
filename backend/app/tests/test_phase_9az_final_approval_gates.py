from __future__ import annotations

import importlib
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOC_PATH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AZ_FINAL_APPROVAL_GATES_AND_STAGED_EMBED_READINESS.md"
EMBED_SNIPPET = '<script src="https://alte.edu.ge/assets/alte-ai-chat-widget.js" defer></script>'
SECRET_PATTERNS = [
    "DATABASE_URL=",
    "ANTHROPIC_API_KEY=",
    "sk-ant",
    "password=",
    "token=",
]


def read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_phase_9az_verifier_importability():
    verifier = importlib.import_module("app.scripts.verify_phase_9az_final_approval_gates")
    assert hasattr(verifier, "run_checks")


def test_phase_9az_doc_records_verified_backend_state():
    text = read_doc()
    assert "BACKEND_DEPLOYED_FULL_KNOWLEDGE_AND_PUBLIC_ANSWER_CLEANUP_VERIFIED_PENDING_APPROVALS" in text
    assert "alte-ai-crm-backend-00051-btg" in text
    assert "v0.9-phase-9ax-9ay-final-routing-cleanup3" in text
    assert "Focused Phase 9AT QA: `7/7 PASS`" in text
    assert "Full Phase 9AS QA: `53/53 PASS`" in text
    assert "Operator alignment QA: `7/7 PASS`" in text
    assert "Browser/API answer-cleanliness QA: `7/7 PASS`" in text
    assert "Remaining failures/gaps: none" in text


def test_phase_9az_remaining_gates_are_blocking():
    text = read_doc()
    for gate in [
        "Official Privacy URL approval",
        "Contact-flow approval",
        "Asset upload approval",
        "Staged real-site embed approval",
        "Real-domain smoke approval",
        "Dirty tree reconciliation",
        "Final public launch GO",
    ]:
        assert gate in text
    assert "Status: `PENDING`" in text
    assert "Status: `NOT_APPROVED`" in text
    assert "Ready for public launch: NO-GO" in text


def test_phase_9az_asset_and_embed_are_prepared_but_not_executed():
    text = read_doc()
    assert "https://alte.edu.ge/assets/alte-ai-chat-widget.js" in text
    assert "Upload status: `NOT_EXECUTED_PENDING_APPROVAL`" in text
    assert "Asset upload executed: NO" in text
    assert "Staged embed executed: NO" in text
    assert EMBED_SNIPPET in text
    assert "dist/widget/alte-ai-chat-widget.js" in text
    assert "A5083446ADE39513D77969115FE0CEF21A4BF8EF3F588551BC87EFDD4E2C2B73" in text


def test_phase_9az_real_domain_smoke_and_rollback_are_documented():
    text = read_doc()
    assert "Real-Domain Smoke Checklist" in text
    assert "Bachelor ECTS question returns `240 ECTS`" in text
    assert "Master ECTS question returns `120 ECTS`" in text
    assert "Computer Science spring calendar returns `9-14 March` and `30 March`" in text
    assert "Unsupported prompts do not hallucinate" in text
    assert "Explicit operator handover works" in text
    assert "Rollback Plan" in text
    assert "Remove the staged embed snippet" in text


def test_phase_9az_safety_confirmations_remain_no_go():
    text = read_doc()
    assert "Public launch:\n\n`NO-GO`" in text
    assert "Real `alte.edu.ge` modified: NO" in text
    assert "Real `join.alte.edu.ge` modified: NO" in text
    assert "Assets uploaded: NO" in text
    assert "Embed executed: NO" in text
    assert "Contact flow submitted: NO" in text
    assert "Lead/customer/task created: NO" in text
    assert "DB schema/migration/seed/import changed or run: NO" in text
    assert "Secret Manager changed: NO" in text
    assert "CORS changed: NO" in text
    assert "Bridge Hub touched: NO" in text


def test_phase_9az_no_secrets_or_tracked_env_files():
    text = read_doc()
    assert all(pattern not in text for pattern in SECRET_PATTERNS)
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    tracked = result.stdout.splitlines()
    assert not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]
