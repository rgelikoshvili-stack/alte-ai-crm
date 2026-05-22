import asyncio

from sqlalchemy import select

from app.models import Conversation, Customer, Lead, Task
from app.scripts import e2e_local_smoke, setup_local_demo


def test_diagnostics_local_demo_does_not_expose_database_url_or_secrets(client):
    response = client.get("/diagnostics/local-demo")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database_type"] in {"sqlite", "postgresql", "other"}
    assert "DATABASE_URL" not in str(data)
    assert "test-secret" not in str(data)
    assert "test-anthropic-key" not in str(data)
    assert "counts" in data
    assert set(data["counts"]) >= {
        "departments",
        "customers",
        "leads",
        "conversations",
        "messages",
        "tasks",
        "knowledge_sources",
        "knowledge_snippets",
    }


def test_setup_and_smoke_script_helpers_are_importable():
    assert setup_local_demo.mask_database_url("sqlite+aiosqlite:///./local.db") == "sqlite://***"
    assert setup_local_demo.next_commands()["demo_url"] == "http://127.0.0.1:5500/demo.html"
    payload = e2e_local_smoke.result_payload([], None, None, None)
    assert payload["passed"] is True


def test_local_demo_chat_flow_creates_customer_lead_task_and_updates_operator_views(client, session_factory):
    session = client.post(
        "/chat/session/start",
        json={"channel": "website_chat", "source_domain": "alte.edu.ge", "language": "ka"},
    ).json()
    interest = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": "მაინტერესებს ბიზნესის პროგრამაზე ჩარიცხვა",
            "source_domain": "alte.edu.ge",
            "language": "ka",
        },
    )
    contact = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": "ნინო ბერიძე, +995599000000, nino@example.com",
            "source_domain": "alte.edu.ge",
            "language": "ka",
        },
    )

    assert interest.status_code == 200
    assert contact.status_code == 200
    contact_data = contact.json()
    assert contact_data["created_lead_id"]
    assert contact_data["created_task_id"]

    inbox = client.get("/inbox")
    dashboard = client.get("/dashboard/overview")
    diagnostics = client.get("/diagnostics/local-demo")

    assert inbox.status_code == 200
    assert any(item["conversation_id"] == session["conversation_id"] for item in inbox.json())
    assert dashboard.status_code == 200
    assert dashboard.json()["total_conversations"] >= 1
    assert diagnostics.status_code == 200
    assert diagnostics.json()["counts"]["leads"] >= 1

    async def load_created():
        async with session_factory() as db:
            conversation = await db.get(Conversation, session["conversation_id"])
            customer = await db.scalar(select(Customer).where(Customer.email == "nino@example.com"))
            lead = await db.get(Lead, contact_data["created_lead_id"])
            task = await db.get(Task, contact_data["created_task_id"])
            return conversation, customer, lead, task

    conversation, customer, lead, task = asyncio.run(load_created())
    assert conversation is not None
    assert customer is not None
    assert lead is not None
    assert task is not None
    assert lead.customer_id == customer.id
