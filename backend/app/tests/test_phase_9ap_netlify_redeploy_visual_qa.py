from __future__ import annotations

from pathlib import Path

from app.scripts import verify_phase_9ap_netlify_redeploy_visual_qa as verifier


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AP_NETLIFY_REDEPLOY_AND_VISUAL_QA_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_9ap_netlify_verifier_importable():
    assert verifier.RESULT_DOC == RESULT_DOC


def test_phase_9ap_netlify_result_doc_exists_and_passed():
    text = read(RESULT_DOC)

    assert "PHASE_9AP_NETLIFY_STATUS=PASSED" in text
    assert "BACKEND_DEPLOYED_FULL_CHATBOT_FUNCTIONALITY_FIXES_VERIFIED_PENDING_APPROVALS" in text
    assert "Public launch: NO-GO" in text


def test_phase_9ap_netlify_live_source_freshness_documented():
    text = read(RESULT_DOC)

    assert "LIVE_SOURCE_FRESH=YES" in text
    assert "HTTP_STATUS=200" in text
    assert "latestUserText() || m.text" in text
    assert "m.text || latestUserText()" in text
    assert "მედიცინა / MD" in text
    assert "მედიცინა/MD" in text


def test_phase_9ap_netlify_visual_and_production_qa_documented():
    text = read(RESULT_DOC)

    assert "VISUAL_QA_STATUS=PASSED" in text
    assert "CONTACT_PREFILL_PASS=True" in text
    assert "PRODUCTION_9AP_QA_STATUS=PASSED" in text
    assert "PRODUCTION_9AP_QA_CHECKS=16/16" in text


def test_phase_9ap_netlify_safety_gates_remain_closed():
    text = read(RESULT_DOC)
    public = read(PUBLIC_LAUNCH).lower()

    assert "REAL_ALTE_SITE_MODIFIED=NO" in text
    assert "Real Alte asset upload executed: NO" in text
    assert "Real-site embed executed: NO" in text
    assert "CONTACT_FLOW_EXECUTED=NO" in text
    assert "LEAD_TASK_CUSTOMER_CREATED=NO" in text
    assert "REAL_CONTACT_DATA_SENT=NO" in text
    assert "public_launch_decision=go" not in public
    assert "no-go" in public


def test_phase_9ap_netlify_no_secrets_or_real_contact_data():
    text = read(RESULT_DOC)

    assert "DATABASE_URL=" not in text
    assert "ANTHROPIC_API_KEY=" not in text
    assert "sk-ant" not in text
    assert "@gmail.com" not in text
    assert "+995" not in text
