from __future__ import annotations

import importlib
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AE_FINAL_PREFLIGHT_APPROVAL_PACKAGE.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
TEST_SITE_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
TEST_SITE_CHAT = PROJECT_ROOT / "test_site" / "variants" / "pro-v2-chat.jsx"
TEST_SITE_JOIN = PROJECT_ROOT / "test_site" / "join.html"
WIDGET_CHAT = PROJECT_ROOT / "widget" / "variants" / "pro-v2-chat.jsx"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_verifier_importability() -> None:
    module = importlib.import_module("app.scripts.verify_phase_9ae_final_preflight_approval_package")
    assert hasattr(module, "run_checks")


def test_phase_9ae_status_is_no_go_pending_approvals() -> None:
    text = read(RESULT_DOC)
    assert (
        "PHASE_9AE_FINAL_PREFLIGHT_APPROVAL_STATUS="
        "NO_GO_PENDING_PRIVACY_CONTACT_ASSET_EMBED_AND_REAL_DOMAIN_SMOKE"
    ) in text
    assert "Public launch: NO-GO" in text
    assert "BACKEND_DEPLOYED_WIDGET_MOBILE_RESPONSIVE_VISUAL_QA_PASSED_PENDING_PRIVACY_AND_EMBED_APPROVAL" in text


def test_privacy_contact_asset_and_embed_gates_remain_pending() -> None:
    text = read(RESULT_DOC)
    assert "OFFICIAL_PRIVACY_URL_STATUS=PENDING" in text
    assert "CONTACT_CREATION_FLOW_STATUS=NOT_APPROVED_FOR_REAL_CONTACT_DATA_TEST" in text
    assert "FINAL_WIDGET_ASSET_URL_STATUS=PENDING_APPROVAL_AND_UPLOAD" in text
    assert "site embed status: NOT_EXECUTED" in text
    assert "Do not apply this to `alte.edu.ge` or `join.alte.edu.ge`" in text


def test_proposed_asset_url_and_embed_snippet_present() -> None:
    text = read(RESULT_DOC)
    assert "https://alte.edu.ge/assets/alte-ai-chat-widget.js" in text
    assert "window.AlteChatWidgetConfig" in text
    assert "apiBaseUrl" in text
    assert "sourceDomain: \"alte.edu.ge\"" in text
    assert "sourceDomain: \"join.alte.edu.ge\"" in text


def test_real_domain_smoke_checklist_covers_required_kb_and_contact_cases() -> None:
    text = read(RESULT_DOC)
    for expected in ["240 ECTS", "120 ECTS", "5 years", "9-14 March", "2031"]:
        assert expected in text
    assert "No lead/task/customer created during no-contact smoke" in text
    assert "must not ask the user to type phone/email/name directly" in text


def test_dirty_tree_triage_documents_known_pending_files() -> None:
    text = read(RESULT_DOC)
    for expected in [
        "Dirty Tree Triage",
        "README.md",
        "docs/NEXT_PHASES.md",
        "FULL_PROJECT_AUDIT_2026_05_30.md",
        "frontend/package-lock.json",
        "leave pending",
    ]:
        assert expected in text


def test_frontend_forbidden_patterns_absent() -> None:
    text = "\n".join(read(path) for path in [TEST_SITE_JS, TEST_SITE_JOIN, TEST_SITE_CHAT, WIDGET_CHAT])
    for forbidden in ["/api/chat", "api.anthropic.com", "ANTHROPIC_API_KEY", "sk-ant"]:
        assert forbidden not in text
    assert "/chat/session/start" in text
    assert "/chat/message" in text


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
