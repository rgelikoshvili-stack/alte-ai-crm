from app.scripts import verify_phase_8z_safe_widget_ui


def test_phase_8z_verifier_importable():
    assert verify_phase_8z_safe_widget_ui.SAFE_WIDGET.name == "alte-university-ai-chatbot-safe.html"
    assert verify_phase_8z_safe_widget_ui.DECISION_STATE


def test_safe_widget_exists():
    assert verify_phase_8z_safe_widget_ui.SAFE_WIDGET.exists()


def test_safe_widget_does_not_call_anthropic_directly():
    assert verify_phase_8z_safe_widget_ui.safe_widget_has_no_forbidden_frontend_ai().passed is True


def test_safe_widget_contains_backend_chat_endpoints():
    assert verify_phase_8z_safe_widget_ui.safe_widget_has_required_backend_wiring().passed is True


def test_uploaded_ui_review_docs_exist():
    assert verify_phase_8z_safe_widget_ui.UI_REVIEW_DOC.exists()
    assert verify_phase_8z_safe_widget_ui.INTEGRATION_DOC.exists()


def test_phase_8z_decision_state_exists():
    assert verify_phase_8z_safe_widget_ui.decision_state_documented().passed is True


def test_phase_8z_no_forbidden_secret_patterns():
    assert verify_phase_8z_safe_widget_ui.no_forbidden_patterns().passed is True


def test_phase_8z_all_checks_pass():
    checks = verify_phase_8z_safe_widget_ui.run_checks()

    assert all(check.passed for check in checks)
