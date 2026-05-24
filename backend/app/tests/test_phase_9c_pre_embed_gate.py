from app.scripts import verify_phase_9c_pre_embed_gate


def test_phase_9c_verifier_importable():
    assert verify_phase_9c_pre_embed_gate.DECISION_STATE
    assert verify_phase_9c_pre_embed_gate.FINAL_GATE.name == "FINAL_PRE_EMBED_APPROVAL_GATE.md"


def test_required_docs_exist():
    assert all(check.passed for check in verify_phase_9c_pre_embed_gate.required_docs_exist())


def test_no_go_pending_approvals_exists():
    assert verify_phase_9c_pre_embed_gate.required_statuses_exist().passed is True


def test_asset_url_pending_exists():
    text = verify_phase_9c_pre_embed_gate.ASSET_HOSTING.read_text(encoding="utf-8")
    assert "WIDGET_ASSET_HOSTING_STATUS=PENDING_FINAL_URL" in text


def test_privacy_approval_pending_exists():
    text = verify_phase_9c_pre_embed_gate.PRIVACY_RECORD.read_text(encoding="utf-8")
    assert "PRIVACY_DATA_APPROVAL_STATUS=PENDING" in text


def test_decision_state_exists():
    assert verify_phase_9c_pre_embed_gate.decision_state_documented().passed is True


def test_safe_pro_widget_does_not_contain_direct_anthropic_endpoint():
    assert verify_phase_9c_pre_embed_gate.safe_pro_widget_has_no_forbidden_frontend_ai().passed is True


def test_public_launch_not_marked_complete():
    assert verify_phase_9c_pre_embed_gate.public_launch_not_complete().passed is True


def test_actual_embed_not_marked_complete():
    assert verify_phase_9c_pre_embed_gate.actual_embed_not_complete().passed is True


def test_no_forbidden_secret_patterns():
    assert verify_phase_9c_pre_embed_gate.no_forbidden_patterns().passed is True


def test_phase_9c_all_checks_pass():
    checks = verify_phase_9c_pre_embed_gate.run_checks()

    assert all(check.passed for check in checks)
