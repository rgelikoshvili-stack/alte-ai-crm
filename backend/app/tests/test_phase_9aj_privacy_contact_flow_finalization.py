from __future__ import annotations

import importlib
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AJ_PRIVACY_CONTACT_FLOW_FINALIZATION_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def status(text: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}=([A-Z0-9_]+)$", text, re.MULTILINE)
    return match.group(1) if match else None


def test_phase_9aj_verifier_importability():
    verifier = importlib.import_module("app.scripts.verify_phase_9aj_privacy_contact_flow_finalization")
    assert hasattr(verifier, "run_checks")


def test_phase_9aj_result_doc_status_values_valid():
    text = read(RESULT_DOC)
    assert status(text, "PRIVACY_URL_STATUS") in {"PENDING", "PROVIDED_PENDING_APPROVAL"}
    assert status(text, "CONTACT_FLOW_APPROVAL_STATUS") == "NOT_APPROVED"
    assert status(text, "CONTACT_DATA_TEST_STATUS") == "NOT_EXECUTED"
    assert status(text, "PUBLIC_LAUNCH_STATUS") == "NO_GO"


def test_phase_9aj_consent_copy_exists_ka_en():
    text = read(RESULT_DOC)
    assert "ვეთანხმები, რომ ჩემი საკონტაქტო ინფორმაცია გამოყენებული იქნას მხოლოდ ჩემს მოთხოვნაზე პასუხის გასაცემად" in text
    assert "I agree that my contact information may be used only to respond to my request" in text


def test_phase_9aj_privacy_url_if_provided_is_https():
    text = read(RESULT_DOC)
    privacy_status = status(text, "PRIVACY_URL_STATUS")
    if privacy_status == "PROVIDED_PENDING_APPROVAL":
        match = re.search(r"^OFFICIAL_PRIVACY_URL=(\S+)$", text, re.MULTILINE)
        assert match
        assert match.group(1).startswith("https://")


def test_phase_9aj_public_launch_remains_no_go():
    text = read(PUBLIC_LAUNCH).lower()
    assert "public_launch_decision=go" not in text
    assert "no-go" in text


def test_phase_9aj_no_real_contact_details_in_doc():
    text = read(RESULT_DOC)
    assert "@gmail.com" not in text
    assert "+995" not in text
    assert "555-" not in text
    assert "599-" not in text
    assert "REAL_CONTACT_DATA_SENT=NO" in text


def test_phase_9aj_contact_flow_not_approved_without_explicit_approval():
    text = read(RESULT_DOC)
    assert "CONTACT_FLOW_APPROVAL_STATUS=APPROVED" not in text
    assert "CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED" in text
    assert "CONTACT_FLOW_EXECUTED=NO" in text
    assert "LEAD_TASK_CUSTOMER_CREATED=NO" in text
