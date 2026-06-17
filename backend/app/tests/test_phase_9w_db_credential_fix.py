import importlib
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[3]


def test_verifier_importability():
    importlib.import_module("app.scripts.verify_phase_9w_db_credential_fix")


def test_smoke_script_importability():
    importlib.import_module("app.scripts.production_db_credential_smoke")


def test_docs_do_not_contain_raw_database_url_or_password():
    paths = [
        ROOT / "docs" / "deployment" / "PHASE_9W_DB_CREDENTIAL_FIX_ROOT_CAUSE.md",
        ROOT / "docs" / "deployment" / "PHASE_9W_DB_CREDENTIAL_FIX_RESULT.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())
    assert not re.search(r"postgres(?:ql)?(?:\+asyncpg)?://[^<\s]+:[^<\s]+@", combined, re.IGNORECASE)
    assert not re.search(r"password\s*[:=]\s*['\"]?[^<\s]{8,}", combined, re.IGNORECASE)


def test_frontend_forbidden_patterns_absent_and_endpoints_present():
    combined = "\n".join(
        [
            (ROOT / "test_site" / "alte-ai-chat-widget.js").read_text(encoding="utf-8"),
            (ROOT / "dist" / "widget" / "alte-ai-chat-widget.js").read_text(encoding="utf-8"),
        ]
    )
    assert "/chat/session/start" in combined
    assert "/chat/message" in combined
    for forbidden in ["ANTHROPIC_API_KEY", "api.anthropic.com", "sk-ant-", "/api/chat"]:
        assert forbidden not in combined


def test_public_launch_not_complete():
    result = (ROOT / "docs" / "deployment" / "PHASE_9W_DB_CREDENTIAL_FIX_RESULT.md").read_text(encoding="utf-8")
    assert "Public launch: NO" in result
    assert "PUBLIC_LAUNCH_DECISION=GO" not in result
