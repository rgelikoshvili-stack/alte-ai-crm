from app.scripts import verify_finance_no_contact_guard
from app.scripts import verify_phase_8y_finance_no_contact_guard


def test_phase_8y_verifiers_importable():
    assert verify_finance_no_contact_guard.TEST_FILE.name == "test_finance_no_contact_guard.py"
    assert verify_phase_8y_finance_no_contact_guard.DECISION_STATE


def test_phase_8y_finance_guard_tests_exist():
    assert verify_phase_8y_finance_no_contact_guard.TEST_FILE.exists()


def test_phase_8y_docs_record_redeploy_required():
    assert verify_phase_8y_finance_no_contact_guard.docs_record_fix().passed is True


def test_phase_8y_decision_state_exists():
    assert verify_phase_8y_finance_no_contact_guard.decision_state_documented().passed is True


def test_phase_8y_no_forbidden_secret_patterns():
    assert verify_phase_8y_finance_no_contact_guard.no_forbidden_patterns().passed is True


def test_finance_no_contact_guard_checks_pass():
    checks = verify_finance_no_contact_guard.run_checks()

    assert all(check.passed for check in checks)
