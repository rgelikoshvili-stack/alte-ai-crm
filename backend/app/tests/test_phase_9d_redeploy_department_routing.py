from app.scripts import production_department_routing_sidebar_smoke
from app.scripts import verify_phase_9d_redeploy_department_routing


def test_phase_9d_redeploy_scripts_importable():
    assert production_department_routing_sidebar_smoke.PRODUCTION_BACKEND_URL.startswith("https://")
    assert verify_phase_9d_redeploy_department_routing.IMAGE_TAG == "v0.9-department-routing-sidebar"


def test_phase_9d_redeploy_result_doc_exists():
    assert verify_phase_9d_redeploy_department_routing.RESULT_DOC.exists()


def test_phase_9d_redeploy_result_records_no_contact_flow():
    text = verify_phase_9d_redeploy_department_routing.RESULT_DOC.read_text(encoding="utf-8")
    assert "Contact-flow test not run: yes" in text


def test_phase_9d_redeploy_result_records_no_contact_details():
    text = verify_phase_9d_redeploy_department_routing.RESULT_DOC.read_text(encoding="utf-8")
    assert "No contact details sent: yes" in text


def test_phase_9d_redeploy_result_records_no_intentional_lead_task_customer():
    text = verify_phase_9d_redeploy_department_routing.RESULT_DOC.read_text(encoding="utf-8")
    assert "Intentional lead/task/customer creation: no" in text


def test_phase_9d_redeploy_decision_state_exists():
    assert verify_phase_9d_redeploy_department_routing.decision_state_documented().passed is True


def test_phase_9d_redeploy_safe_widget_still_safe():
    assert verify_phase_9d_redeploy_department_routing.safe_widget_still_backend_connected().passed is True


def test_phase_9d_redeploy_public_launch_not_complete():
    assert verify_phase_9d_redeploy_department_routing.public_launch_not_complete().passed is True


def test_phase_9d_redeploy_no_forbidden_secret_patterns():
    assert verify_phase_9d_redeploy_department_routing.no_forbidden_patterns().passed is True


def test_phase_9d_redeploy_all_checks_pass():
    checks = verify_phase_9d_redeploy_department_routing.run_checks()

    assert all(check.passed for check in checks)
