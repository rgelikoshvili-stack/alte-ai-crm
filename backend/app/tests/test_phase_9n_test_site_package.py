from app.scripts import test_site_api_smoke, verify_phase_9n_test_site_package


def test_test_site_files_exist():
    required = [
        verify_phase_9n_test_site_package.TEST_INDEX,
        verify_phase_9n_test_site_package.TEST_JOIN,
        verify_phase_9n_test_site_package.TEST_WIDGET_JS,
        verify_phase_9n_test_site_package.TEST_README,
    ]

    assert all(path.exists() for path in required)


def test_smoke_script_importable():
    assert test_site_api_smoke.PRODUCTION_BACKEND_URL.startswith("https://")
    assert test_site_api_smoke.CONTACT_FLOW_TEST_RUN is False
    assert len(test_site_api_smoke.TEST_CASES) == 10


def test_verifier_importable():
    assert verify_phase_9n_test_site_package.PASSED_DECISION.endswith("SITE_EMBED")


def test_test_site_js_has_no_direct_anthropic_endpoint():
    assert verify_phase_9n_test_site_package.test_site_assets_are_safe().passed is True


def test_test_site_has_production_backend_url():
    assert verify_phase_9n_test_site_package.test_site_config_is_present().passed is True


def test_public_launch_not_marked_complete():
    assert verify_phase_9n_test_site_package.public_launch_not_complete().passed is True


def test_actual_alte_embed_not_marked_complete():
    assert verify_phase_9n_test_site_package.actual_alte_embed_not_complete().passed is True


def test_no_forbidden_secret_patterns():
    assert verify_phase_9n_test_site_package.no_forbidden_secret_patterns().passed is True


def test_phase_9n_test_site_all_checks_pass():
    checks = verify_phase_9n_test_site_package.run_checks()

    assert all(check.passed for check in checks)
