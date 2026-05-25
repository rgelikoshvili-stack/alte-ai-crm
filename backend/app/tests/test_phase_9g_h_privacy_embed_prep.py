from app.scripts import verify_phase_9g_h_privacy_embed_prep


def test_phase_9g_h_verifier_importable():
    assert verify_phase_9g_h_privacy_embed_prep.STATUS.startswith("PHASE_9G_H_STATUS")


def test_privacy_docs_exist():
    assert verify_phase_9g_h_privacy_embed_prep.PRIVACY_PACKAGE.exists()
    assert verify_phase_9g_h_privacy_embed_prep.CONSENT_DOC.exists()
    assert verify_phase_9g_h_privacy_embed_prep.RETENTION_DOC.exists()


def test_embed_package_files_exist():
    assert verify_phase_9g_h_privacy_embed_prep.ALTE_SNIPPET.exists()
    assert verify_phase_9g_h_privacy_embed_prep.JOIN_SNIPPET.exists()
    assert verify_phase_9g_h_privacy_embed_prep.EMBED_README.exists()


def test_result_doc_exists():
    assert verify_phase_9g_h_privacy_embed_prep.RESULT_DOC.exists()


def test_privacy_status_pending():
    checks = verify_phase_9g_h_privacy_embed_prep.statuses_recorded()
    assert any(check.name == "Privacy approval remains pending" and check.passed for check in checks)


def test_asset_url_status_pending():
    checks = verify_phase_9g_h_privacy_embed_prep.statuses_recorded()
    assert any(check.name == "Final asset URL remains pending" and check.passed for check in checks)


def test_decision_state_exists():
    checks = verify_phase_9g_h_privacy_embed_prep.statuses_recorded()
    assert any(check.name == "Phase 9G-H decision state documented" and check.passed for check in checks)


def test_actual_embed_not_marked_complete():
    assert verify_phase_9g_h_privacy_embed_prep.actual_embed_not_complete().passed is True


def test_public_launch_not_marked_complete():
    assert verify_phase_9g_h_privacy_embed_prep.public_launch_not_complete().passed is True


def test_widget_has_no_direct_anthropic_endpoint():
    assert verify_phase_9g_h_privacy_embed_prep.widget_privacy_and_security().passed is True


def test_no_forbidden_secret_patterns():
    assert verify_phase_9g_h_privacy_embed_prep.no_forbidden_patterns().passed is True


def test_phase_9g_h_all_checks_pass():
    checks = verify_phase_9g_h_privacy_embed_prep.run_checks()

    assert all(check.passed for check in checks)
