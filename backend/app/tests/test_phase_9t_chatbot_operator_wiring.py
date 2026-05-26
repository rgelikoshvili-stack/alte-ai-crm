import asyncio
import importlib
from pathlib import Path

from sqlalchemy import select

from app.models import Conversation, Customer, Lead, Message, Task
from app.schemas.crm import MessageCreate
from app.services.conversation_service import create_message

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_phase_9t_verifier_importability():
    module = importlib.import_module("app.scripts.verify_phase_9t_chatbot_operator_wiring")
    assert hasattr(module, "run_checks")


def test_phase_9t_local_workflow_smoke_importability():
    module = importlib.import_module("app.scripts.local_pro_v2_operator_workflow_smoke")
    assert hasattr(module, "main")


def fetch_one(session_factory, query):
    async def run():
        async with session_factory() as session:
            return await session.scalar(query)

    return asyncio.run(run())


def fetch_all(session_factory, query):
    async def run():
        async with session_factory() as session:
            return (await session.scalars(query)).all()

    return asyncio.run(run())


def test_chat_contact_submission_links_conversation_and_creates_operator_task(client, session_factory):
    session = client.post(
        "/chat/session/start",
        json={"source_domain": "alte.edu.ge", "language": "ka", "channel": "website_chat"},
    ).json()

    response = client.post(
        f"/chat/contact/{session['conversation_id']}",
        json={
            "session_id": session["session_id"],
            "full_name": "Test Visitor",
            "phone": "+995 500 00 00 00",
            "interest_area": "admissions",
            "selected_department": "admissions",
            "selected_topic": "operator",
            "source_domain": "alte.edu.ge",
            "language": "ka",
            "consent": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "contact_received_handover_requested"
    assert data["customer_id"]
    assert data["lead_id"]
    assert data["task_id"]

    conversation = fetch_one(session_factory, select(Conversation).where(Conversation.id == session["conversation_id"]))
    assert conversation.customer_id == data["customer_id"]
    assert conversation.lead_id == data["lead_id"]
    assert conversation.human_handover is True

    assert len(fetch_all(session_factory, select(Customer))) == 1
    assert len(fetch_all(session_factory, select(Lead))) == 1
    tasks = fetch_all(session_factory, select(Task))
    assert len(tasks) == 1
    assert tasks[0].title == "Human handover requested"


def test_chat_contact_submission_requires_valid_session_and_contact(client):
    session = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "ka"}).json()

    wrong_session = client.post(
        f"/chat/contact/{session['conversation_id']}",
        json={"session_id": "wrong", "phone": "+995 500 00 00 01", "consent": True},
    )
    missing_contact = client.post(
        f"/chat/contact/{session['conversation_id']}",
        json={"session_id": session["session_id"], "full_name": "Test Visitor", "consent": True},
    )

    assert wrong_session.status_code == 403
    assert missing_contact.status_code == 400


def test_public_chat_messages_returns_operator_replies_for_valid_session(client, session_factory):
    session = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "en"}).json()

    async def add_operator_reply():
        async with session_factory() as db:
            await create_message(
                db,
                session["conversation_id"],
                MessageCreate(sender_type="operator", text="Operator reply from CRM"),
            )

    asyncio.run(add_operator_reply())

    allowed = client.get(f"/chat/messages/{session['conversation_id']}?session_id={session['session_id']}")
    blocked = client.get(f"/chat/messages/{session['conversation_id']}?session_id=wrong")

    assert allowed.status_code == 200
    assert any(row["sender_type"] == "operator" and row["text"] == "Operator reply from CRM" for row in allowed.json())
    assert blocked.status_code == 403

    messages = fetch_all(session_factory, select(Message))
    assert any(message.sender_type == "operator" for message in messages)


def test_phase_9t_frontend_markers_and_no_provider_secrets():
    text = "\n".join(
        (PROJECT_ROOT / path).read_text(encoding="utf-8")
        for path in [
            "widget/pro-v2.html",
            "widget/variants/pro-v2-chat.jsx",
            "widget/variants/pro-v2-modals.jsx",
        ]
    )
    for marker in [
        "/chat/session/start",
        "/chat/message",
        "/chat/contact/",
        "/chat/messages/",
        "selected_department",
        "selected_topic",
        "website_chat",
        "pro_v2_safe",
    ]:
        assert marker in text
    for forbidden in ["api.anthropic.com", "ANTHROPIC_API_KEY", "sk" + "-ant", "DATABASE_URL"]:
        assert forbidden not in text


def test_phase_9t_docs_keep_public_launch_no_go():
    text = "\n".join(
        (PROJECT_ROOT / path).read_text(encoding="utf-8").lower()
        for path in [
            "docs/deployment/PHASE_9T_CHATBOT_OPERATOR_WIRING_RESULT.md",
            "docs/NEXT_PHASES.md",
            "docs/deployment/PHASE_9P_PUBLIC_LAUNCH_DECISION.md",
        ]
    )
    assert "backend_local_pro_v2_operator_wiring_ready_pending_browser_workflow_test" in text
    assert "public_launch_decision=go" not in text
    assert "public launch complete" not in text
