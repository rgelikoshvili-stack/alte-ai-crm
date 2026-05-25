from app.scripts import verify_phase_9j_final_pre_embed_gate


def test_phase_9j_verifier_importable():
    assert (
        verify_phase_9j_final_pre_embed_gate.FINAL_GATE_STATUS
        == "PHASE_9J_FINAL_PRE_SITE_EMBED_STATUS=NO_GO_PENDING_FINAL_APPROVALS"
    )


def test_final_gate_docs_exist():
    assert verify_phase_9j_final_pre_embed_gate.FINAL_GATE_DOC.exists()
    assert verify_phase_9j_final_pre_embed_gate.APPROVAL_RECORD.exists()
    assert verify_phase_9j_final_pre_embed_gate.GO_NO_GO_CHECKLIST.exists()


def test_no_go_and_pending_statuses_exist():
    checks = verify_phase_9j_final_pre_embed_gate.statuses_recorded()

    assert all(check.passed for check in checks)


def test_phase_9j_decision_state_exists():
    assert verify_phase_9j_final_pre_embed_gate.statuses_recorded()[-1].passed is True


def test_actual_embed_not_marked_complete():
    assert verify_phase_9j_final_pre_embed_gate.actual_embed_not_complete().passed is True


def test_public_launch_not_marked_complete():
    assert verify_phase_9j_final_pre_embed_gate.public_launch_not_complete().passed is True


def test_privacy_approval_not_falsely_complete():
    assert verify_phase_9j_final_pre_embed_gate.privacy_approval_not_complete().passed is True


def test_official_content_approval_not_falsely_complete():
    assert verify_phase_9j_final_pre_embed_gate.official_content_approval_not_complete().passed is True


def test_final_asset_placeholder_and_snippets_exist():
    assert verify_phase_9j_final_pre_embed_gate.asset_placeholder_and_snippets_exist().passed is True


def test_widget_assets_have_no_direct_anthropic_endpoint():
    assert verify_phase_9j_final_pre_embed_gate.widget_assets_are_safe().passed is True


def test_no_forbidden_secret_patterns():
    assert verify_phase_9j_final_pre_embed_gate.no_forbidden_patterns().passed is True


def test_phase_9j_all_checks_pass():
    checks = verify_phase_9j_final_pre_embed_gate.run_checks()

    assert all(check.passed for check in checks)
