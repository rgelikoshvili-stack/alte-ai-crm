from app.scripts import verify_phase_9n_cors_test_origin_plan


def test_verifier_importable():
    assert verify_phase_9n_cors_test_origin_plan.DECISION_STATE.endswith("CORS_APPROVAL")


def test_cors_plan_docs_exist():
    required = [
        verify_phase_9n_cors_test_origin_plan.PLAN_DOC,
        verify_phase_9n_cors_test_origin_plan.HOSTING_PACKAGE,
        verify_phase_9n_cors_test_origin_plan.BROWSER_CHECKLIST_GEO,
        verify_phase_9n_cors_test_origin_plan.NETLIFY_DEPLOY_FIX_GEO,
        verify_phase_9n_cors_test_origin_plan.CORS_UPDATE_PLAN,
        verify_phase_9n_cors_test_origin_plan.CORS_SCRIPT,
        verify_phase_9n_cors_test_origin_plan.HOSTED_SMOKE_RESULT,
    ]

    assert all(path.exists() for path in required)


def test_test_origin_pending_status_exists():
    text = verify_phase_9n_cors_test_origin_plan.PLAN_DOC.read_text(encoding="utf-8")

    assert "PHASE_9N_CORS_TEST_ORIGIN_STATUS=APPROVED_PENDING_CORS_UPDATE" in text
    assert "https://alte-ai-chat-test.netlify.app" in text


def test_browser_smoke_pending_status_exists():
    text = verify_phase_9n_cors_test_origin_plan.HOSTED_SMOKE_RESULT.read_text(encoding="utf-8")

    assert "HOSTED_BROWSER_SMOKE_STATUS=BLOCKED_NETLIFY_TEST_SITE_NOT_DEPLOYED" in text


def test_public_launch_not_complete():
    assert verify_phase_9n_cors_test_origin_plan.public_launch_not_complete().passed is True


def test_real_alte_embed_not_complete():
    assert verify_phase_9n_cors_test_origin_plan.actual_alte_embed_not_complete().passed is True


def test_no_forbidden_secret_patterns():
    assert verify_phase_9n_cors_test_origin_plan.no_secret_patterns().passed is True


def test_phase_9n_cors_all_checks_pass():
    checks = verify_phase_9n_cors_test_origin_plan.run_checks()

    assert all(check.passed for check in checks)
