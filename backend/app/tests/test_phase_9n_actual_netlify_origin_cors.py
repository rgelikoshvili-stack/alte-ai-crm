from app.scripts import verify_phase_9n_actual_netlify_origin_cors


def test_verifier_importable():
    assert verify_phase_9n_actual_netlify_origin_cors.ACTUAL_ORIGIN == "https://nimble-croissant-2f66e8.netlify.app"


def test_result_doc_exists():
    assert verify_phase_9n_actual_netlify_origin_cors.RESULT_DOC.exists()


def test_actual_netlify_origin_recorded():
    assert verify_phase_9n_actual_netlify_origin_cors.result_records_status().passed is True


def test_browser_smoke_pending_status_exists():
    assert verify_phase_9n_actual_netlify_origin_cors.hosted_smoke_pending().passed is True


def test_public_launch_not_complete():
    assert verify_phase_9n_actual_netlify_origin_cors.public_launch_not_complete().passed is True


def test_actual_alte_embed_not_complete():
    assert verify_phase_9n_actual_netlify_origin_cors.actual_alte_embed_not_complete().passed is True


def test_no_forbidden_secret_patterns():
    assert verify_phase_9n_actual_netlify_origin_cors.no_secret_patterns().passed is True


def test_phase_9n_actual_netlify_origin_all_checks_pass():
    checks = verify_phase_9n_actual_netlify_origin_cors.run_checks()

    assert all(check.passed for check in checks)
