from app.scripts import verify_phase_9i_asset_hosting_decision


def test_phase_9i_verifier_importable():
    assert verify_phase_9i_asset_hosting_decision.PLACEHOLDER_URL == "https://alte.edu.ge/assets/alte-ai-chat-widget.js"


def test_dist_widget_assets_exist():
    assert verify_phase_9i_asset_hosting_decision.ASSET_HTML.exists()
    assert verify_phase_9i_asset_hosting_decision.ASSET_JS.exists()


def test_embed_snippets_contain_placeholder_url():
    assert verify_phase_9i_asset_hosting_decision.snippets_use_placeholder().passed is True


def test_handoff_and_status_docs_exist():
    assert verify_phase_9i_asset_hosting_decision.HANDOFF_DOC.exists()
    assert verify_phase_9i_asset_hosting_decision.RESULT_DOC.exists()


def test_phase_9i_decision_state_exists():
    assert verify_phase_9i_asset_hosting_decision.decision_state_documented().passed is True


def test_actual_embed_not_marked_complete():
    assert verify_phase_9i_asset_hosting_decision.actual_upload_embed_not_complete().passed is True


def test_public_launch_not_marked_complete():
    assert verify_phase_9i_asset_hosting_decision.public_launch_not_complete().passed is True


def test_final_widget_asset_has_no_direct_anthropic_endpoint():
    assert verify_phase_9i_asset_hosting_decision.assets_are_safe_and_backend_connected().passed is True


def test_no_forbidden_secret_patterns():
    assert verify_phase_9i_asset_hosting_decision.no_forbidden_patterns().passed is True


def test_phase_9i_all_checks_pass():
    checks = verify_phase_9i_asset_hosting_decision.run_checks()

    assert all(check.passed for check in checks)
