from pathlib import Path
import importlib


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def read(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_phase_9x_verifier_importability():
    module = importlib.import_module("app.scripts.verify_phase_9x_manual_browser_workflow_package")
    assert hasattr(module, "run_checks")


def test_phase_9x_runbook_and_result_exist():
    assert (PROJECT_ROOT / "docs/deployment/PHASE_9X_MANUAL_BROWSER_WORKFLOW_RUNBOOK.md").exists()
    assert (PROJECT_ROOT / "docs/deployment/PHASE_9X_MANUAL_BROWSER_WORKFLOW_RESULT.md").exists()


def test_phase_9x_runbook_records_required_browser_flow():
    text = read("docs/deployment/PHASE_9X_MANUAL_BROWSER_WORKFLOW_RUNBOOK.md")
    for marker in [
        "https://nimble-croissant-2f66e8.netlify.app/join.html",
        "http://127.0.0.1:5173/",
        "Production API",
        "Operator reply",
        "Create knowledge candidate",
        "Open review",
    ]:
        assert marker in text


def test_phase_9x_result_records_operator_roundtrip_but_knowledge_pending():
    text = read("docs/deployment/PHASE_9X_MANUAL_BROWSER_WORKFLOW_RESULT.md")
    assert (
        "PHASE_9X_MANUAL_BROWSER_WORKFLOW_STATUS=OPERATOR_CHAT_ROUNDTRIP_CONFIRMED_PENDING_KNOWLEDGE_REVIEW"
        in text
    )
    assert "BACKEND_CHATBOT_OPERATOR_ROUNDTRIP_CONFIRMED_PENDING_KNOWLEDGE_REVIEW" in text
    assert "| Operator reply appears in chatbot | CONFIRMED |" in text
    assert "| Knowledge candidate can be created from operator reply | PENDING |" in text
    assert "PHASE_9X_MANUAL_BROWSER_WORKFLOW_STATUS=PASSED" not in text


def test_phase_9x_status_docs_keep_public_launch_no_go():
    text = "\n".join(
        read(path).lower()
        for path in [
            "README.md",
            "docs/NEXT_PHASES.md",
            "docs/deployment/PHASE_9P_PUBLIC_LAUNCH_DECISION.md",
        ]
    )
    assert "backend_chatbot_operator_roundtrip_confirmed_pending_knowledge_review" in text
    assert "public_launch_decision=go" not in text
    assert "actual_site_embed_execution_status=executed" not in text
    assert "real_domain_smoke_status=passed" not in text
    assert "knowledge candidate can be created from operator reply | confirmed" not in text


def test_phase_9x_frontend_has_safe_backend_markers():
    text = "\n".join(
        read(path)
        for path in [
            "test_site/alte-ai-chat-widget.js",
            "dist/widget/alte-ai-chat-widget.js",
            "widget/pro-v2.html",
            "widget/variants/pro-v2-chat.jsx",
            "frontend/app.js",
        ]
    )
    for marker in [
        "/chat/session/start",
        "/chat/message",
        "/chat/contact",
        "/chat/messages",
        "/knowledge/operator-reply-candidates/",
        "website_chat",
        "pro_v2_safe",
    ]:
        assert marker in text
    for forbidden in ["api.anthropic.com", "ANTHROPIC_API_KEY", "sk" + "-ant", "DATABASE_URL", "window.claude.complete"]:
        assert forbidden not in text
