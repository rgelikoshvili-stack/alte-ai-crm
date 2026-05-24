from app.scripts import production_finance_no_contact_smoke
from app.scripts import verify_phase_8y_redeploy_finance_guard


def test_phase_8y_redeploy_scripts_importable():
    assert production_finance_no_contact_smoke.PRODUCTION_BACKEND_URL.startswith("https://")
    assert verify_phase_8y_redeploy_finance_guard.IMAGE_TAG == "v0.8-finance-no-contact-guard"


def test_phase_8y_redeploy_result_doc_exists():
    assert verify_phase_8y_redeploy_finance_guard.RESULT_DOC.exists()


def test_phase_8y_redeploy_result_records_no_contact_flow():
    text = verify_phase_8y_redeploy_finance_guard.RESULT_DOC.read_text(encoding="utf-8")
    assert "Contact-flow test not run: yes" in text


def test_phase_8y_redeploy_result_records_no_contact_details():
    text = verify_phase_8y_redeploy_finance_guard.RESULT_DOC.read_text(encoding="utf-8")
    assert "No contact details sent: yes" in text


def test_phase_8y_redeploy_result_records_no_intentional_lead_task_customer():
    text = verify_phase_8y_redeploy_finance_guard.RESULT_DOC.read_text(encoding="utf-8")
    assert "Intentional lead/task/customer creation: no" in text


def test_phase_8y_redeploy_decision_state_exists():
    assert verify_phase_8y_redeploy_finance_guard.decision_state_documented().passed is True


def test_phase_8y_redeploy_public_launch_not_complete():
    assert verify_phase_8y_redeploy_finance_guard.public_launch_not_complete().passed is True


def test_phase_8y_redeploy_no_forbidden_secret_patterns():
    assert verify_phase_8y_redeploy_finance_guard.no_forbidden_patterns().passed is True


def test_phase_8y_redeploy_all_checks_pass():
    checks = verify_phase_8y_redeploy_finance_guard.run_checks()

    assert all(check.passed for check in checks)
