import zipfile

from app.scripts import verify_phase_9n_netlify_test_site_fix


def test_verifier_importable():
    assert verify_phase_9n_netlify_test_site_fix.DECISION_STATE.startswith("BACKEND_DEPLOYED_NETLIFY")


def test_netlify_toml_exists():
    assert verify_phase_9n_netlify_test_site_fix.NETLIFY_TOML.exists()


def test_redirects_exists():
    assert verify_phase_9n_netlify_test_site_fix.REDIRECTS.exists()


def test_deploy_zip_exists():
    assert verify_phase_9n_netlify_test_site_fix.ZIP_PATH.exists()


def test_zip_root_contains_expected_files():
    assert verify_phase_9n_netlify_test_site_fix.zip_root_is_valid().passed is True


def test_zip_root_is_not_nested_under_test_site():
    with zipfile.ZipFile(verify_phase_9n_netlify_test_site_fix.ZIP_PATH) as archive:
        names = [info.filename.replace("\\", "/") for info in archive.infolist()]

    assert all(not name.startswith("test_site/") for name in names)


def test_test_site_js_has_no_direct_anthropic_endpoint():
    assert verify_phase_9n_netlify_test_site_fix.package_assets_are_safe().passed is True


def test_public_launch_not_complete():
    assert verify_phase_9n_netlify_test_site_fix.public_launch_not_complete().passed is True


def test_actual_alte_embed_not_complete():
    assert verify_phase_9n_netlify_test_site_fix.actual_alte_embed_not_complete().passed is True


def test_browser_smoke_not_falsely_passed():
    assert verify_phase_9n_netlify_test_site_fix.browser_smoke_not_passed().passed is True


def test_no_forbidden_secret_patterns():
    assert verify_phase_9n_netlify_test_site_fix.package_assets_are_safe().passed is True


def test_phase_9n_netlify_fix_all_checks_pass():
    checks = verify_phase_9n_netlify_test_site_fix.run_checks()

    assert all(check.passed for check in checks)
