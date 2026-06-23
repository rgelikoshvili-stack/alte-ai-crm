import asyncio

from sqlalchemy import func, select

from app.models import Customer, Lead, Task
from app.services.website_sync_preview_service import reset_website_sync_preview_state


def add_source(client, **overrides):
    payload = {
        "name": "Official Alte website",
        "base_url": "https://alte.edu.ge",
        "allowed_paths": ["/ka", "/en"],
        "source_group_hint": "finance_sources",
        "enabled": True,
        **overrides,
    }
    response = client.post("/api/knowledge/sync/website/sources", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def preview(client, source_id: str, url: str = "fixture://tuition", **overrides):
    response = client.post(
        "/api/knowledge/sync/website/preview",
        json={
            "source_id": source_id,
            "url": url,
            "mode": "single_url",
            "limit": 5,
            "dry_run": True,
            **overrides,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


async def crm_counts(session_factory):
    async with session_factory() as session:
        return {
            "customers": await session.scalar(select(func.count()).select_from(Customer)),
            "leads": await session.scalar(select(func.count()).select_from(Lead)),
            "tasks": await session.scalar(select(func.count()).select_from(Task)),
        }


def test_phase_10n_approve_draft_publishes_approved_chunks(client):
    reset_website_sync_preview_state()
    source = add_source(client)
    run = preview(client, source["id"])

    approve = client.post(f"/api/knowledge/sync/website/approve/{run['run_id']}", json={})
    assert approve.status_code == 200, approve.text
    payload = approve.json()
    assert payload["status"] == "approved"
    assert payload["approved_count"] == run["chunks_count"]
    assert payload["public_usable"] is True

    approved = client.get("/api/knowledge/sync/website/approved")
    assert approved.status_code == 200
    chunks = approved.json()
    assert len(chunks) == run["chunks_count"]
    assert all(chunk["status"] == "approved" for chunk in chunks)
    assert all(chunk["public_usable"] is True for chunk in chunks)
    assert all(chunk["priority"] == 100 for chunk in chunks)
    assert all("source_id" not in chunk["clean_source_label"].lower() for chunk in chunks)


def test_phase_10n_reject_draft_keeps_content_unsearchable(client):
    reset_website_sync_preview_state()
    source = add_source(client)
    run = preview(client, source["id"])

    reject = client.post(f"/api/knowledge/sync/website/reject/{run['run_id']}", json={})
    assert reject.status_code == 200, reject.text
    assert reject.json()["status"] == "rejected"

    approved = client.get("/api/knowledge/sync/website/approved")
    assert approved.status_code == 200
    assert approved.json() == []

    ask = client.post("/api/knowledge/ask", json={"question": "What is the Medicine tuition fee?", "language": "en"})
    assert ask.status_code == 200
    assert ask.json()["used_claude"] is False
    assert "12000 GEL" not in ask.json()["answer"]


def test_phase_10n_archive_approved_version_disables_public_use(client):
    reset_website_sync_preview_state()
    source = add_source(client)
    run = preview(client, source["id"])
    approve = client.post(f"/api/knowledge/sync/website/approve/{run['run_id']}", json={})
    assert approve.status_code == 200

    rollback = client.post(f"/api/knowledge/sync/website/rollback/website_sync:{run['run_id']}", json={})
    assert rollback.status_code == 200, rollback.text
    assert rollback.json()["status"] == "archived"
    assert rollback.json()["public_usable"] is False

    approved = client.get("/api/knowledge/sync/website/approved").json()
    assert approved
    assert all(chunk["status"] == "archived" for chunk in approved)
    assert all(chunk["public_usable"] is False for chunk in approved)

    ask = client.post("/api/knowledge/ask", json={"question": "What is the Medicine tuition fee?", "language": "en"})
    assert ask.status_code == 200
    assert "12000 GEL" not in ask.json()["answer"]


def test_phase_10n_draft_content_never_reaches_public_gateways(client, session_factory):
    reset_website_sync_preview_state()
    source = add_source(client)
    run = preview(client, source["id"])
    assert run["public_usable"] is False
    assert "12000 GEL" in run["extracted_text_preview"]

    ask = client.post("/api/knowledge/ask", json={"question": "What is the Medicine tuition fee?", "language": "en"})
    assert ask.status_code == 200
    assert ask.json()["used_claude"] is False
    assert "12000 GEL" not in ask.json()["answer"]

    session = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "en"}).json()
    chat = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "source_domain": "alte.edu.ge",
            "language": "en",
            "message": "What is the Medicine tuition fee?",
        },
    )
    assert chat.status_code == 200
    assert "12000 GEL" not in chat.json()["reply"]

    counts = asyncio.run(crm_counts(session_factory))
    assert counts == {"customers": 0, "leads": 0, "tasks": 0}


def test_phase_10n_approved_website_retrieval_wins_for_variable_question(client, session_factory):
    reset_website_sync_preview_state()
    source = add_source(client, source_group_hint="finance_sources")
    run = preview(client, source["id"], url="fixture://tuition-en")
    approve = client.post(f"/api/knowledge/sync/website/approve/{run['run_id']}", json={})
    assert approve.status_code == 200

    ask = client.post("/api/knowledge/ask", json={"question": "What is the Medicine tuition fee?", "language": "en"})
    assert ask.status_code == 200
    ask_payload = ask.json()
    assert ask_payload["status"] == "answered"
    assert ask_payload["used_claude"] is False
    assert "12000 GEL" in ask_payload["answer"]
    assert ask_payload["public_source_label"]
    assert "source_id" not in ask_payload["public_source_label"].lower()

    session = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "en"}).json()
    chat = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "source_domain": "alte.edu.ge",
            "language": "en",
            "message": "What is the Medicine tuition fee?",
        },
    )
    assert chat.status_code == 200, chat.text
    chat_payload = chat.json()
    assert "12000 GEL" in chat_payload["reply"]
    assert chat_payload["public_source_label"]
    assert "source_id" not in chat_payload["public_source_label"].lower()
    assert chat_payload["created_lead_id"] is None
    assert chat_payload["created_task_id"] is None

    counts = asyncio.run(crm_counts(session_factory))
    assert counts == {"customers": 0, "leads": 0, "tasks": 0}


def test_phase_10n_stable_program_question_still_uses_structured_kb(client):
    reset_website_sync_preview_state()
    source = add_source(client, source_group_hint="finance_sources")
    run = preview(client, source["id"])
    approve = client.post(f"/api/knowledge/sync/website/approve/{run['run_id']}", json={})
    assert approve.status_code == 200

    ask = client.post("/api/knowledge/ask", json={"question": "Tell me about the Medicine program", "language": "en"})
    assert ask.status_code == 200
    payload = ask.json()
    assert payload["used_claude"] is False
    assert "12000 GEL" not in payload["answer"]
    assert "360 ECTS" in payload["answer"]


def test_phase_10n_domain_and_private_path_guards_still_apply(client):
    reset_website_sync_preview_state()

    external = client.post(
        "/api/knowledge/sync/website/sources",
        json={"name": "External", "base_url": "https://example.com", "allowed_paths": [], "enabled": True},
    )
    assert external.status_code == 400

    admin_path = client.post(
        "/api/knowledge/sync/website/sources",
        json={"name": "Admin", "base_url": "https://alte.edu.ge/admin", "allowed_paths": [], "enabled": True},
    )
    assert admin_path.status_code == 400
