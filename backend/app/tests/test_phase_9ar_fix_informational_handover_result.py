from __future__ import annotations

from pathlib import Path

from app.scripts import verify_phase_9ar_fix_informational_handover


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AR_FIX_INFORMATIONAL_HANDOVER_POLLUTION_RESULT.md"
QA_SCRIPT = PROJECT_ROOT / "backend" / "app" / "scripts" / "production_phase_9ar_fix_informational_handover_qa.py"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_9ar_verifier_importable():
    assert callable(verify_phase_9ar_fix_informational_handover.main)


def test_phase_9ar_result_doc_status_and_decision():
    text = read(RESULT_DOC)

    assert "PHASE_9AR_FIX_STATUS=PASSED_PENDING_APPROVALS" in text
    assert "BACKEND_DEPLOYED_CHATBOT_OPERATOR_ALIGNMENT_FIX_VERIFIED_PENDING_APPROVALS" in text
    assert "Public launch: NO-GO" in text


def test_phase_9ar_bachelor_behavior_documented():
    text = read(RESULT_DOC)

    assert "Bachelor ECTS" in text
    assert "should_handover=false" in text
    assert "human_handover=false" in text
    assert "selected_department=Programs" in text
    assert "240 ECTS" in text


def test_phase_9ar_handover_policy_documented():
    text = read(RESULT_DOC)

    assert "Source-backed informational answers now clear `should_handover`" in text
    assert "Unsupported no-source answer still has operator fallback" in text
    assert "Explicit operator request still has `should_handover=true`" in text
    assert "Wait-for-operator still sets `waiting_for_operator` and `human_handover=true`" in text


def test_phase_9ar_production_qa_and_deploy_documented():
    text = read(RESULT_DOC)

    assert "36/36 passed" in text
    assert "116/116 passed" in text
    assert "alte-ai-crm-backend-00037-7xh" in text
    assert "v0.9-phase-9ar-informational-handover-fix" in text


def test_phase_9ar_safety_documented():
    text = read(RESULT_DOC)
    public = read(PUBLIC_LAUNCH).lower()

    assert "REAL_ALTE_SITE_MODIFIED=NO" in text
    assert "CONTACT_FLOW_EXECUTED=NO" in text
    assert "REAL_CONTACT_DATA_SENT=NO" in text
    assert "LEAD_TASK_CUSTOMER_CREATED=NO" in text
    assert "Production DB migration run: NO" in text
    assert "Production seed run: NO" in text
    assert "Secret Manager changed: NO" in text
    assert "CORS changed: NO" in text
    assert "public_launch_decision=go" not in public


def test_phase_9ar_polling_limitation_remains_documented():
    text = read(RESULT_DOC)

    assert "VISITOR_SIDE_OPERATOR_REPLY_POLLING=NOT_ACTIVE" in text


def test_phase_9ar_qa_script_safe_surface():
    script = read(QA_SCRIPT)

    assert "/chat/contact" not in script
    assert "contact_flow_executed" in script
    assert "real_contact_data_sent" in script
    assert "lead_task_customer_created_intentionally" in script


def test_phase_9ar_no_secrets_or_real_contact_data_in_docs():
    text = "\n".join([read(RESULT_DOC), read(QA_SCRIPT)])

    for forbidden in [
        "DATABASE_URL=",
        "ANTHROPIC_API_KEY=",
        "OPENAI_API_KEY=",
        "sk-ant",
        "@gmail.com",
        "@alte.edu.ge",
        "+995",
        "555-",
        "599-",
    ]:
        assert forbidden not in text
