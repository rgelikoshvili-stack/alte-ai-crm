from app.scripts import verify_phase_9k_security_reliability_fixes


def test_phase_9k_verifier_importable():
    assert (
        verify_phase_9k_security_reliability_fixes.STATUS
        == "PHASE_9K_SECURITY_RELIABILITY_STATUS=CODE_FIXED_PENDING_REDEPLOY"
    )


def test_phase_9k_result_doc_exists():
    assert verify_phase_9k_security_reliability_fixes.RESULT_DOC.exists()


def test_phase_9k_decision_state_exists():
    assert verify_phase_9k_security_reliability_fixes.docs_record_decision_state().passed is True


def test_public_launch_not_marked_complete():
    assert verify_phase_9k_security_reliability_fixes.public_launch_not_marked_complete().passed is True


def test_actual_embed_not_marked_complete():
    assert verify_phase_9k_security_reliability_fixes.actual_embed_not_marked_complete().passed is True


def test_archive_security_note_exists():
    assert verify_phase_9k_security_reliability_fixes.ARCHIVE_NOTE.exists()
    assert verify_phase_9k_security_reliability_fixes.archive_note_marks_evidence_non_production().passed is True


def test_no_forbidden_secret_patterns_in_production_assets():
    assert verify_phase_9k_security_reliability_fixes.production_assets_are_safe().passed is True


def test_phase_9k_all_checks_pass():
    checks = verify_phase_9k_security_reliability_fixes.run_checks()

    assert all(check.passed for check in checks)
