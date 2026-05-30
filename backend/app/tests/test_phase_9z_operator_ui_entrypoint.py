from __future__ import annotations

import importlib
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DIAGNOSIS_DOC = ROOT / "docs" / "deployment" / "PHASE_9Z_OPERATOR_UI_LOCAL_ENTRYPOINT_DIAGNOSIS.md"
RETEST_DOC = ROOT / "docs" / "deployment" / "PHASE_9Z_BROWSER_OPERATOR_LOGIN_RETEST_RESULT.md"

ALLOWED_STATUSES = {
    "READY_FOR_MANUAL_BROWSER_LOGIN",
    "PASSED",
    "BLOCKED_OPERATOR_UI_ENTRYPOINT_MISSING",
}


def test_verifier_importable():
    module = importlib.import_module("app.scripts.verify_phase_9z_operator_ui_entrypoint")
    assert callable(module.main)


def test_entrypoint_docs_have_no_secret_like_strings():
    text = DIAGNOSIS_DOC.read_text(encoding="utf-8") + "\n" + RETEST_DOC.read_text(encoding="utf-8")
    forbidden_patterns = [
        r"(?i)\bpassword\s*[:=]\s*\S+",
        r"(?i)\bpassword_hash\b",
        r"(?i)\bdatabase_url\b",
        r"(?i)\bpostgres(?:ql)?://",
        r"\bpbkdf2_sha256\$",
        r"\bsk-ant-[A-Za-z0-9_-]+",
        r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
    ]
    for pattern in forbidden_patterns:
        assert not re.search(pattern, text)


def test_retest_status_is_allowed():
    text = RETEST_DOC.read_text(encoding="utf-8")
    match = re.search(r"PHASE_9Z_BROWSER_OPERATOR_LOGIN_RETEST_STATUS=([A-Z0-9_]+)", text)
    assert match
    assert match.group(1) in ALLOWED_STATUSES


def test_public_launch_not_complete():
    text = DIAGNOSIS_DOC.read_text(encoding="utf-8") + "\n" + RETEST_DOC.read_text(encoding="utf-8")
    assert "Public launch: NO-GO" in text
    assert "PUBLIC_LAUNCH_DECISION=GO" not in text
    assert "PUBLIC_LAUNCH_STATUS=COMPLETE" not in text


def test_local_secret_paths_not_tracked():
    result = subprocess.run(
        ["git", "ls-files", "--", ".local-secrets", ".env"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert result.stdout.strip() == ""
