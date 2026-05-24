from app.scripts import verify_phase_9d_sidebar_widget_ui


def test_verifier_importable():
    assert verify_phase_9d_sidebar_widget_ui.DECISION_STATE


def test_sidebar_widget_exists():
    assert verify_phase_9d_sidebar_widget_ui.SAFE_PRO_WIDGET.exists()


def test_archived_pip_widget_exists():
    assert verify_phase_9d_sidebar_widget_ui.PIP_ARCHIVE.exists()


def test_sidebar_widget_contains_department_menu():
    assert verify_phase_9d_sidebar_widget_ui.sidebar_structure_present().passed is True


def test_sidebar_widget_sends_selected_department_context():
    text = verify_phase_9d_sidebar_widget_ui.SAFE_PRO_WIDGET.read_text(encoding="utf-8")
    assert "selected_department" in text
    assert "selected_topic" in text
    assert "safe_pro_sidebar" in text


def test_sidebar_widget_has_no_direct_anthropic_endpoint():
    assert verify_phase_9d_sidebar_widget_ui.safe_widget_has_no_forbidden_frontend_ai().passed is True


def test_sidebar_widget_contains_backend_chat_endpoints():
    assert verify_phase_9d_sidebar_widget_ui.backend_wiring_present().passed is True


def test_decision_doc_exists():
    assert verify_phase_9d_sidebar_widget_ui.DECISION_DOC.exists()


def test_decision_state_exists():
    assert verify_phase_9d_sidebar_widget_ui.decision_state_documented().passed is True


def test_public_launch_not_marked_complete():
    assert verify_phase_9d_sidebar_widget_ui.public_launch_not_complete().passed is True


def test_no_forbidden_secret_patterns():
    assert verify_phase_9d_sidebar_widget_ui.no_forbidden_patterns().passed is True


def test_all_checks_pass():
    assert all(check.passed for check in verify_phase_9d_sidebar_widget_ui.run_checks())
