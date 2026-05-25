import asyncio

from sqlalchemy import select

from app.models import AuditLog, Conversation, Customer, Lead, Task


def fetch_all(session_factory, query):
    async def run():
        async with session_factory() as session:
            return (await session.scalars(query)).all()

    return asyncio.run(run())


def test_repeated_handover_without_contact_creates_no_tasks(client, session_factory):
    session = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "ka"}).json()

    body = {"session_id": session["session_id"]}
    first = client.post(f"/chat/handover/{session['conversation_id']}", json=body)
    second = client.post(f"/chat/handover/{session['conversation_id']}", json=body)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["status"] == "contact_required"
    assert second.json()["status"] == "contact_required"
    assert first.json()["task_id"] is None
    assert second.json()["task_id"] is None
    assert fetch_all(session_factory, select(Customer)) == []
    assert fetch_all(session_factory, select(Lead)) == []
    assert fetch_all(session_factory, select(Task)) == []


def test_invalid_handover_conversation_is_rejected(client):
    response = client.post("/chat/handover/not-a-real-conversation")

    assert response.status_code == 404


def test_handover_requires_valid_session(client):
    session = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "ka"}).json()

    missing = client.post(f"/chat/handover/{session['conversation_id']}")
    wrong = client.post(f"/chat/handover/{session['conversation_id']}", json={"session_id": "wrong-session"})

    assert missing.status_code == 403
    assert wrong.status_code == 403


def test_handover_with_existing_customer_is_idempotent(client, session_factory):
    async def create_conversation_with_customer():
        async with session_factory() as session:
            session_id = "safe-session-id"
            customer = Customer(source_channel="website_chat", consent_status="implicit_chat_request")
            session.add(customer)
            await session.flush()
            conversation = Conversation(
                channel="website_chat",
                language="ka",
                ai_handled=True,
                customer_id=customer.id,
            )
            session.add(conversation)
            await session.flush()
            session.add(
                AuditLog(
                    actor_type="system",
                    action="chat_session_started",
                    entity_type="conversation",
                    entity_id=conversation.id,
                    metadata_json={"session_id": session_id, "source_domain": "alte.edu.ge"},
                )
            )
            await session.commit()
            return conversation.id, session_id

    conversation_id, session_id = asyncio.run(create_conversation_with_customer())

    first = client.post(f"/chat/handover/{conversation_id}", json={"session_id": session_id})
    second = client.post(f"/chat/handover/{conversation_id}", json={"session_id": session_id})

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["status"] == "handover_requested"
    assert second.json()["status"] == "handover_already_requested"
    assert first.json()["task_id"] == second.json()["task_id"]
    tasks = fetch_all(session_factory, select(Task))
    assert len(tasks) == 1
    assert tasks[0].title == "Human handover requested"
