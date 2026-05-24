from app.scripts import verify_phase_9b_widget_design_concepts


def test_phase_9b_verifier_importable():
    assert verify_phase_9b_widget_design_concepts.SAFE_PRO_WIDGET.name == "alte-university-ai-chatbot-safe-pro.html"
    assert verify_phase_9b_widget_design_concepts.DECISION_STATE


def test_extracted_design_folder_exists():
    assert verify_phase_9b_widget_design_concepts.EVIDENCE_DIR.exists()
    assert verify_phase_9b_widget_design_concepts.VARIANTS_DIR.exists()
    assert verify_phase_9b_widget_design_concepts.PREVIEWS_DIR.exists()


def test_safe_pro_widget_exists():
    assert verify_phase_9b_widget_design_concepts.SAFE_PRO_WIDGET.exists()


def test_safe_pro_widget_does_not_call_anthropic_directly():
    assert verify_phase_9b_widget_design_concepts.safe_pro_widget_has_no_forbidden_frontend_ai().passed is True


def test_safe_pro_widget_contains_backend_chat_endpoints():
    assert verify_phase_9b_widget_design_concepts.safe_pro_widget_has_required_backend_wiring().passed is True


def test_standalone_safe_pro_demo_exists():
    assert verify_phase_9b_widget_design_concepts.STANDALONE_DEMO.exists()


def test_embed_snippet_doc_exists():
    assert verify_phase_9b_widget_design_concepts.EMBED_SNIPPET_DOC.exists()


def test_phase_9b_decision_state_exists():
    assert verify_phase_9b_widget_design_concepts.decision_state_documented().passed is True


def test_public_launch_not_marked_complete():
    assert verify_phase_9b_widget_design_concepts.public_launch_not_complete().passed is True


def test_phase_9b_no_forbidden_secret_patterns():
    assert verify_phase_9b_widget_design_concepts.no_forbidden_patterns().passed is True


def test_phase_9b_all_checks_pass():
    checks = verify_phase_9b_widget_design_concepts.run_checks()

    assert all(check.passed for check in checks)
