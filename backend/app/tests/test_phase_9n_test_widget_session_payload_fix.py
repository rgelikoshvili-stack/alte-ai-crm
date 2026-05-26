import zipfile

from app.scripts import test_site_session_payload_smoke, verify_phase_9n_test_widget_session_payload_fix


def test_verifier_importable():
    assert verify_phase_9n_test_widget_session_payload_fix.STATUS.endswith("READY_PENDING_NETLIFY_REDEPLOY")


def test_session_payload_smoke_importable():
    payload = test_site_session_payload_smoke.build_session_payload(
        {"source_domain": "alte.edu.ge", "language": "ka", "mode": "test_site"}
    )

    assert payload["channel"] == "website_chat"


def test_widget_js_contains_session_markers():
    assert verify_phase_9n_test_widget_session_payload_fix.widget_js_contains_markers().passed is True


def test_widget_html_uses_backend_channel_literal():
    assert verify_phase_9n_test_widget_session_payload_fix.widget_html_payload_is_compatible().passed is True


def test_widget_assets_have_no_direct_provider_or_secret_patterns():
    assert verify_phase_9n_test_widget_session_payload_fix.no_forbidden_patterns().passed is True


def test_deploy_zip_contains_updated_widget_js():
    assert verify_phase_9n_test_widget_session_payload_fix.zip_contains_updated_js_and_html().passed is True


def test_deploy_zip_html_uses_website_chat():
    with zipfile.ZipFile(verify_phase_9n_test_widget_session_payload_fix.ZIP_PATH) as archive:
        html = archive.read("alte-ai-chat-widget.html").decode("utf-8", errors="ignore")

    assert 'channel: "website_chat"' in html
    assert 'channel: "website",' not in html


def test_public_launch_not_complete():
    assert verify_phase_9n_test_widget_session_payload_fix.public_launch_not_complete().passed is True


def test_browser_smoke_not_falsely_passed():
    assert verify_phase_9n_test_widget_session_payload_fix.browser_smoke_not_passed().passed is True


def test_phase_9n_session_payload_fix_all_checks_pass():
    checks = verify_phase_9n_test_widget_session_payload_fix.run_checks()

    assert all(check.passed for check in checks)
