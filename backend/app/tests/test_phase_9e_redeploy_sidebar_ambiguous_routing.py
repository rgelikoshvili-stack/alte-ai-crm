from app.scripts import verify_phase_9e_redeploy_sidebar_ambiguous_routing


def test_phase_9e_redeploy_verifier_importable():
    assert verify_phase_9e_redeploy_sidebar_ambiguous_routing.IMAGE_TAG == "v0.9-sidebar-ambiguous-routing-fix"


def test_phase_9e_redeploy_result_doc_exists():
    assert verify_phase_9e_redeploy_sidebar_ambiguous_routing.RESULT_DOC.exists()


def test_phase_9e_redeploy_result_records_no_contact_flow():
    text = verify_phase_9e_redeploy_sidebar_ambiguous_routing.RESULT_DOC.read_text(encoding="utf-8")
    assert "Contact-flow test not run: yes" in text


def test_phase_9e_redeploy_result_records_no_contact_details():
    text = verify_phase_9e_redeploy_sidebar_ambiguous_routing.RESULT_DOC.read_text(encoding="utf-8")
    assert "No contact details sent: yes" in text


def test_phase_9e_redeploy_result_records_no_intentional_lead_task_customer():
    text = verify_phase_9e_redeploy_sidebar_ambiguous_routing.RESULT_DOC.read_text(encoding="utf-8")
    assert "Intentional lead/task/customer creation: no" in text


def test_phase_9e_redeploy_result_records_previous_failures_fixed():
    text = verify_phase_9e_redeploy_sidebar_ambiguous_routing.RESULT_DOC.read_text(encoding="utf-8")
    assert "Finance ambiguous sidebar case: PASS" in text
    assert "Medicine ambiguous sidebar case: PASS" in text


def test_phase_9e_redeploy_decision_state_exists():
    assert verify_phase_9e_redeploy_sidebar_ambiguous_routing.decision_state_documented().passed is True


def test_phase_9e_redeploy_public_launch_not_complete():
    assert verify_phase_9e_redeploy_sidebar_ambiguous_routing.public_launch_not_complete().passed is True


def test_phase_9e_redeploy_no_forbidden_secret_patterns():
    assert verify_phase_9e_redeploy_sidebar_ambiguous_routing.no_forbidden_patterns().passed is True


def test_phase_9e_redeploy_all_checks_pass():
    checks = verify_phase_9e_redeploy_sidebar_ambiguous_routing.run_checks()

    assert all(check.passed for check in checks)
