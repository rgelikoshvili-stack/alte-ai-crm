from app.scripts import verify_phase_9d_department_handover


def test_phase_9d_verifier_importable():
    assert verify_phase_9d_department_handover.DECISION_STATE
    assert verify_phase_9d_department_handover.ROUTING_SERVICE.name == "department_routing_service.py"


def test_required_files_exist():
    assert all(check.passed for check in verify_phase_9d_department_handover.required_files_exist())


def test_routing_service_contains_departments():
    assert verify_phase_9d_department_handover.routing_service_contains_departments().passed is True


def test_safe_pro_widget_sends_department_context():
    assert verify_phase_9d_department_handover.safe_pro_widget_sends_context().passed is True


def test_safe_pro_widget_has_no_direct_anthropic_or_secret():
    assert verify_phase_9d_department_handover.safe_pro_widget_has_no_forbidden_frontend_ai().passed is True


def test_phase_9d_decision_state_exists():
    assert verify_phase_9d_department_handover.decision_state_documented().passed is True


def test_public_launch_not_marked_complete():
    assert verify_phase_9d_department_handover.public_launch_not_complete().passed is True


def test_no_forbidden_secret_patterns():
    assert verify_phase_9d_department_handover.no_forbidden_patterns().passed is True


def test_phase_9d_all_checks_pass():
    checks = verify_phase_9d_department_handover.run_checks()

    assert all(check.passed for check in checks)
