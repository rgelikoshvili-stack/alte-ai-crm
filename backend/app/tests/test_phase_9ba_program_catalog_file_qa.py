from __future__ import annotations

import importlib
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9BA_PROGRAM_CATALOG_FILE_QA_RESULT.md"
SECRET_PATTERNS = [
    "DATABASE_URL=",
    "ANTHROPIC_API_KEY=",
    "sk-ant",
    "password=",
    "token=",
]


def read_doc() -> str:
    return RESULT_DOC.read_text(encoding="utf-8")


def qa_rows(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("| 01_program_catalog.pdf |")]


def test_phase_9ba_verifier_importability():
    verifier = importlib.import_module("app.scripts.verify_phase_9ba_program_catalog_file_qa")
    assert hasattr(verifier, "run_checks")


def test_phase_9ba_result_doc_exists_and_has_20_rows():
    text = read_doc()
    assert "PHASE_9BA_PROGRAM_CATALOG_FILE_QA_STATUS=COMPLETED_WITH_FINDINGS" in text
    assert "QA Set 01 - Higher Education Program Catalog" in text
    assert "01_program_catalog.pdf" in text
    assert "Higher Education Program Catalog" in text
    assert len(qa_rows(text)) == 20


def test_phase_9ba_summary_counts_and_root_causes_present():
    text = read_doc()
    assert "Total tests: 20" in text
    assert "PASS count: 11" in text
    assert "PARTIAL count: 9" in text
    assert "FAIL count: 0" in text
    assert "## Failure Root Causes" in text
    assert "wrong source" in text
    assert "incomplete answer" in text
    assert "clarification missing" in text


def test_phase_9ba_rows_cover_required_categories_and_safety_cases():
    text = read_doc()
    assert "| main |" in text
    assert "| detailed |" in text
    assert "| clarification |" in text
    assert "| unsupported/safety |" in text
    assert "pc_safe_20_space_campus_2031" not in text  # row table is user-facing, not internal IDs
    assert "2031" in text
    assert "კოსმოსური" in text
    assert "ტელეფონის ნომერი" in text


def test_phase_9ba_public_launch_and_safety_no_go():
    text = read_doc()
    assert "Public launch: `NO-GO`" in text
    assert "Public launch remains: NO-GO" in text
    assert "Real site modified: NO" in text
    assert "Assets uploaded or embedded: NO" in text
    assert "Contact flow submitted: NO" in text
    assert "Lead/customer/task created: NO" in text
    assert "DB schema/migration/seed/import changed or run: NO" in text
    assert "Secret Manager changed: NO" in text
    assert "CORS changed: NO" in text
    assert "Bridge Hub touched: NO" in text


def test_phase_9ba_no_secrets_or_tracked_env_files():
    text = read_doc()
    assert all(pattern not in text for pattern in SECRET_PATTERNS)
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    tracked = result.stdout.splitlines()
    assert not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]
