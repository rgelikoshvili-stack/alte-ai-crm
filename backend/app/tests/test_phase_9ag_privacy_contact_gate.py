from __future__ import annotations

import importlib
import re
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AG_PRIVACY_CONTACT_APPROVAL_GATE_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"

FRONTEND_FILES = [
    PROJECT_ROOT / "test_site" / "join.html",
    PROJECT_ROOT / "test_site" / "index.html",
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js",
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-chat.jsx",
    PROJECT_ROOT / "widget" / "variants" / "pro-v2-chat.jsx",
    PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_verifier_importability() -> None:
    module = importlib.import_module("app.scripts.verify_phase_9ag_privacy_contact_gate")
    assert hasattr(module, "run_checks")


def test_phase_9ag_status_is_no_go_pending_privacy_and_contact_approval() -> None:
    text = read(RESULT_DOC)
    assert "PHASE_9AG_PRIVACY_CONTACT_GATE_STATUS=NO_GO_PRIVACY_URL_PENDING_CONTACT_FLOW_NOT_APPROVED" in text
    assert "Public launch: NO-GO" in text
    assert "BACKEND_DEPLOYED_GEORGIAN_ENCODING_FIXED_PENDING_PRIVACY_AND_EMBED_APPROVAL" in text


def test_privacy_url_is_pending_or_https_if_later_provided() -> None:
    text = read(RESULT_DOC)
    assert "PRIVACY_URL_STATUS=PENDING" in text
    match = re.search(r"^OFFICIAL_PRIVACY_URL=(.+)$", text, re.MULTILINE)
    assert match
    value = match.group(1).strip()
    assert value == "<approved official Alte privacy policy URL>" or value.startswith("https://")


def test_contact_flow_is_not_approved_or_executed() -> None:
    text = read(RESULT_DOC)
    assert "CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED" in text
    assert "CONTACT_DATA_TEST_STATUS=NOT_EXECUTED" in text
    assert "LEAD_TASK_CUSTOMER_CREATION_STATUS=NOT_EXECUTED_PENDING_CONTACT_FLOW_APPROVAL" in text
    assert "Production contact-flow test executed: NO" in text
    assert "Lead/task/customer created: NO" in text
    assert "CONTACT_FLOW_APPROVAL_STATUS=APPROVED" not in text
    assert "CONTACT_DATA_TEST_STATUS=EXECUTED" not in text
    assert "LEAD_TASK_CUSTOMER_CREATION_STATUS=EXECUTED" not in text


def test_consent_copy_is_present_and_georgian_is_not_mojibake() -> None:
    text = read(RESULT_DOC)
    assert "Georgian:" in text
    assert "English:" in text
    assert "ოპერატორთან დაკავშირების მოთხოვნის გაგზავნამდე" in text
    assert "კონფიდენციალურობის პოლიტიკას" in text
    assert "Before submitting an operator contact request" in text
    assert "Privacy Policy" in text
    assert "áƒ" not in text


def test_no_real_contact_details_are_included() -> None:
    text = read(RESULT_DOC)
    assert not re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.IGNORECASE)
    assert not re.search(r"\+995[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}[\s-]?\d{2}", text)


def test_public_launch_not_go() -> None:
    text = (read(RESULT_DOC) + "\n" + read(PUBLIC_LAUNCH)).lower()
    assert "public_launch_decision=go" not in text
    assert "public launch: go" not in text
    assert "public launch complete" not in text
    assert "no-go" in text


def test_real_site_and_production_actions_not_executed() -> None:
    text = read(RESULT_DOC)
    for expected in [
        "Real `alte.edu.ge` modified: NO",
        "Real `join.alte.edu.ge` modified: NO",
        "Secret Manager changed: NO",
        "Production DB changed: NO",
        "Migration/seed run: NO",
    ]:
        assert expected in text


def test_frontend_forbidden_api_key_patterns_absent() -> None:
    text = "\n".join(read(path) for path in FRONTEND_FILES if path.exists())
    for forbidden in ["/api/chat", "api.anthropic.com", "ANTHROPIC_API_KEY", "sk-ant"]:
        assert forbidden not in text
    assert "/chat/session/start" in text
    assert "/chat/message" in text


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
