from pathlib import Path
import importlib
import zipfile


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def read(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_phase_9w_verifier_importability():
    module = importlib.import_module("app.scripts.verify_phase_9w_chatbot_function_audit")
    assert hasattr(module, "run_checks")


def test_phase_9w_result_doc_exists_and_records_passed_smokes():
    text = read("docs/deployment/PHASE_9W_CHATBOT_FUNCTION_AUDIT_RESULT.md")
    assert "PHASE_9W_CHATBOT_FUNCTION_AUDIT_STATUS=AUTOMATED_FUNCTION_SMOKE_PASSED_PENDING_MANUAL_BROWSER_WORKFLOW" in text
    for marker in [
        "Session payload smoke | 2/2 PASS",
        "Test site API smoke | 10/10 PASS",
        "CORS smoke | 10/10 PASS",
        "Security/reliability smoke | 16/16 PASS",
        "Department routing/sidebar smoke | 28/28 PASS",
        "Finance no-contact smoke | 24/24 PASS",
        "Knowledge smoke | 25/25 PASS",
        "Local operator workflow smoke | 5/5 PASS",
    ]:
        assert marker in text


def test_phase_9w_decision_state_recorded_without_public_go():
    text = "\n".join(
        read(path).lower()
        for path in [
            "README.md",
            "docs/NEXT_PHASES.md",
            "docs/deployment/PHASE_9P_PUBLIC_LAUNCH_DECISION.md",
        ]
    )
    assert "backend_chatbot_function_audit_passed_pending_manual_browser_workflow" in text
    assert "public_launch_decision=go" not in text
    assert "actual_site_embed_execution_status=executed" not in text
    assert "real_domain_smoke_status=passed" not in text


def test_phase_9w_frontend_contains_backend_markers_and_no_provider_secrets():
    text = "\n".join(
        read(path)
        for path in [
            "test_site/alte-ai-chat-widget.js",
            "dist/widget/alte-ai-chat-widget.js",
            "widget/pro-v2.html",
            "widget/variants/pro-v2-chat.jsx",
            "widget/variants/pro-v2-modals.jsx",
        ]
    )
    for marker in [
        "/chat/session/start",
        "/chat/message",
        "website_chat",
        "pro_v2_safe",
        "selected_department",
        "selected_topic",
        "/chat/contact",
        "/chat/messages",
    ]:
        assert marker in text
    for forbidden in ["api.anthropic.com", "ANTHROPIC_API_KEY", "sk" + "-ant", "DATABASE_URL", "window.claude.complete"]:
        assert forbidden not in text


def test_phase_9w_netlify_zip_contains_widget_root_files():
    archive = PROJECT_ROOT / "dist" / "netlify_test_site_deploy.zip"
    assert archive.exists()
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
    assert "index.html" in names
    assert "join.html" in names
    assert "alte-ai-chat-widget.html" in names
    assert "variants/pro-v2-chat.jsx" in names
    assert "test_site/index.html" not in names

