from app.scripts import production_test_origin_cors_smoke, verify_phase_9n_cors_test_origin_execution


def test_production_test_origin_cors_smoke_importable():
    assert production_test_origin_cors_smoke.TEST_ORIGIN == "https://alte-ai-chat-test.netlify.app"
    assert "/chat/session/start" in production_test_origin_cors_smoke.ENDPOINTS


def test_execution_verifier_importable():
    assert verify_phase_9n_cors_test_origin_execution.TEST_ORIGIN == "https://alte-ai-chat-test.netlify.app"


def test_execution_result_doc_exists():
    assert verify_phase_9n_cors_test_origin_execution.RESULT_DOC.exists()


def test_test_origin_url_recorded():
    text = verify_phase_9n_cors_test_origin_execution.RESULT_DOC.read_text(encoding="utf-8")

    assert "https://alte-ai-chat-test.netlify.app" in text


def test_public_launch_not_complete():
    assert verify_phase_9n_cors_test_origin_execution.public_launch_not_complete().passed is True


def test_actual_alte_embed_not_complete():
    assert verify_phase_9n_cors_test_origin_execution.real_alte_embed_not_complete().passed is True


def test_no_forbidden_secret_patterns():
    assert verify_phase_9n_cors_test_origin_execution.no_secret_patterns().passed is True


def test_phase_9n_cors_execution_all_checks_pass():
    checks = verify_phase_9n_cors_test_origin_execution.run_checks()

    assert all(check.passed for check in checks)
