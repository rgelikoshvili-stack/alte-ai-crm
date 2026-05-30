from __future__ import annotations

import importlib
import re
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AF_PRIVACY_AND_CONTACT_FLOW_APPROVAL_READINESS.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_verifier_importability() -> None:
    module = importlib.import_module("app.scripts.verify_phase_9af_privacy_contact_readiness")
    assert hasattr(module, "run_checks")


def test_phase_9af_status_is_no_go() -> None:
    text = read(RESULT_DOC)
    assert (
        "PHASE_9AF_PRIVACY_CONTACT_READINESS_STATUS="
        "NO_GO_PENDING_OFFICIAL_PRIVACY_URL_AND_CONTACT_FLOW_APPROVAL"
    ) in text
    assert "Public launch: NO-GO" in text
    assert "BACKEND_DEPLOYED_WIDGET_MOBILE_RESPONSIVE_VISUAL_QA_PASSED_PENDING_PRIVACY_AND_EMBED_APPROVAL" in text


def test_privacy_url_is_pending_and_field_is_documented() -> None:
    text = read(RESULT_DOC)
    assert "OFFICIAL_PRIVACY_URL_STATUS=PENDING" in text
    assert "OFFICIAL_PRIVACY_URL=<approved official Alte privacy policy URL>" in text
    assert "OFFICIAL_PRIVACY_URL_STATUS=APPROVED" not in text


def test_contact_flow_and_crm_creation_are_not_approved_or_executed() -> None:
    text = read(RESULT_DOC)
    assert "CONTACT_CREATION_FLOW_STATUS=NOT_APPROVED_FOR_REAL_CONTACT_DATA_TEST" in text
    assert "LEAD_TASK_CUSTOMER_CREATION_STATUS=NOT_EXECUTED_PENDING_CONTACT_FLOW_APPROVAL" in text
    assert "Lead/task/customer creation executed: NO" in text
    assert "Production contact-flow test executed: NO" in text
    assert "CONTACT_CREATION_FLOW_STATUS=APPROVED" not in text
    assert "LEAD_TASK_CUSTOMER_CREATION_STATUS=EXECUTED" not in text


def test_contact_policy_matches_no_direct_contact_detail_request_rule() -> None:
    text = read(RESULT_DOC)
    assert "must not ask the user to type phone, email, full name, WhatsApp" in text
    assert "The bot may answer informational questions without asking for contact details" in text
    assert "safe handover/contact card" in text
    assert "approved synthetic data only" in text


def test_consent_copy_exists_in_georgian_and_english() -> None:
    text = read(RESULT_DOC)
    assert "Georgian:" in text
    assert "English:" in text
    assert "კონფიდენციალურობის პოლიტიკის" in text
    assert "Privacy Policy" in text
    assert "By submitting an operator contact request" in text


def test_approval_checklist_contains_required_gates() -> None:
    text = read(RESULT_DOC)
    for expected in [
        "Official privacy URL provided",
        "Legal/privacy owner approved text",
        "Contact form fields approved",
        "Consent copy approved in Georgian",
        "Consent copy approved in English",
        "Storage destination approved",
        "CRM lead/task creation approved",
        "Synthetic contact-flow test approved",
        "Real contact-flow test approved",
        "Real-site embed approved",
    ]:
        assert expected in text


def test_no_real_contact_details_are_included() -> None:
    text = read(RESULT_DOC)
    assert not re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.IGNORECASE)
    assert not re.search(r"\+995[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}[\s-]?\d{2}", text)


def test_public_launch_not_complete() -> None:
    text = (read(RESULT_DOC) + "\n" + read(PUBLIC_LAUNCH)).lower()
    assert "public_launch_decision=go" not in text
    assert "public launch: go" not in text
    assert "public launch complete" not in text
    assert "no-go" in text


def test_env_and_local_secrets_not_tracked() -> None:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    tracked = result.stdout.splitlines()
    assert not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]
