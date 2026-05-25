from app.scripts import verify_phase_9e_sidebar_ambiguous_routing_fix


def test_phase_9e_verifier_importable():
    assert verify_phase_9e_sidebar_ambiguous_routing_fix.DECISION_STATE.endswith("PENDING_REDEPLOY")


def test_phase_9e_fix_doc_exists():
    assert verify_phase_9e_sidebar_ambiguous_routing_fix.FIX_DOC.exists()


def test_phase_9e_decision_state_exists():
    assert verify_phase_9e_sidebar_ambiguous_routing_fix.docs_record_fix().passed is True


def test_phase_9e_redeploy_required_documented():
    text = verify_phase_9e_sidebar_ambiguous_routing_fix.FIX_DOC.read_text(encoding="utf-8")
    assert "Redeploy is required" in text


def test_phase_9e_public_launch_not_complete():
    assert verify_phase_9e_sidebar_ambiguous_routing_fix.public_launch_not_complete().passed is True


def test_phase_9e_no_forbidden_secret_patterns():
    assert verify_phase_9e_sidebar_ambiguous_routing_fix.no_forbidden_patterns().passed is True


def test_phase_9e_all_checks_pass():
    checks = verify_phase_9e_sidebar_ambiguous_routing_fix.run_checks()

    assert all(check.passed for check in checks)
