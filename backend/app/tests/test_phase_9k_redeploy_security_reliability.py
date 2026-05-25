from app.scripts import production_security_reliability_smoke, verify_phase_9k_redeploy_security_reliability


def test_production_security_reliability_smoke_importable():
    assert production_security_reliability_smoke.PRODUCTION_BACKEND_URL.startswith("https://")
    assert production_security_reliability_smoke.CONTACT_FLOW_TEST_RUN is False


def test_phase_9k_redeploy_verifier_importable():
    assert verify_phase_9k_redeploy_security_reliability.IMAGE_TAG == "v0.9-security-reliability-fixes"


def test_phase_9k_redeploy_result_doc_exists():
    assert verify_phase_9k_redeploy_security_reliability.RESULT_DOC.exists()


def test_phase_9k_redeploy_records_no_contact_flow():
    text = verify_phase_9k_redeploy_security_reliability.RESULT_DOC.read_text(encoding="utf-8")
    assert "contact-flow test run: false" in text


def test_phase_9k_redeploy_records_no_contact_details():
    text = verify_phase_9k_redeploy_security_reliability.RESULT_DOC.read_text(encoding="utf-8")
    assert "no contact details sent: true" in text


def test_phase_9k_redeploy_records_no_intentional_crm_creation():
    text = verify_phase_9k_redeploy_security_reliability.RESULT_DOC.read_text(encoding="utf-8")
    assert "intentional lead/task/customer creation: no" in text


def test_phase_9k_redeploy_decision_state_exists():
    assert verify_phase_9k_redeploy_security_reliability.docs_record_decision_state().passed is True


def test_phase_9k_redeploy_public_launch_not_complete():
    assert verify_phase_9k_redeploy_security_reliability.public_launch_not_marked_complete().passed is True


def test_phase_9k_redeploy_actual_embed_not_complete():
    assert verify_phase_9k_redeploy_security_reliability.actual_embed_not_marked_complete().passed is True


def test_phase_9k_redeploy_no_forbidden_secret_patterns():
    assert verify_phase_9k_redeploy_security_reliability.production_assets_are_safe().passed is True


def test_phase_9k_redeploy_all_checks_pass():
    checks = verify_phase_9k_redeploy_security_reliability.run_checks()

    assert all(check.passed for check in checks)
