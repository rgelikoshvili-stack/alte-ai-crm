from __future__ import annotations

import importlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FRONTEND_APP = PROJECT_ROOT / "frontend" / "app.js"
FRONTEND_INDEX = PROJECT_ROOT / "frontend" / "index.html"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9V_STAGING_OPERATOR_CRM_TEST_WORKFLOW.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_verifier_importability() -> None:
    module = importlib.import_module("app.scripts.verify_phase_9v_staging_operator_crm_workflow")
    assert hasattr(module, "run_checks")


def test_frontend_has_local_and_production_api_switch() -> None:
    text = read(FRONTEND_APP) + "\n" + read(FRONTEND_INDEX)
    assert "API_PRESETS" in text
    assert "http://127.0.0.1:8000" in text
    assert "https://alte-ai-crm-backend-226875230147.europe-west1.run.app" in text
    assert "useLocalApiBtn" in text
    assert "useProductionApiBtn" in text


def test_workflow_doc_records_safe_staging_topology() -> None:
    text = read(RESULT_DOC)
    assert "PHASE_9V_STAGING_OPERATOR_CRM_STATUS=LOCAL_OPERATOR_CRM_CAN_TARGET_PRODUCTION_BACKEND_FOR_NETLIFY_TESTING" in text
    assert "https://nimble-croissant-2f66e8.netlify.app" in text
    assert "http://127.0.0.1:5173" in text
    assert "Public launch: NO-GO" in text


def test_frontend_has_no_forbidden_secret_patterns() -> None:
    text = read(FRONTEND_APP) + "\n" + read(FRONTEND_INDEX)
    for forbidden in ["api.anthropic.com", "ANTHROPIC_API_KEY", "sk" + "-ant", "DATABASE_URL"]:
        assert forbidden not in text
