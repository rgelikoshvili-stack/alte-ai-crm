import importlib

from sqlalchemy import select

from app.models import Customer, Lead, Task
from app.schemas.chat import ChatSessionStartRequest


def test_diagnosis_script_importability():
    importlib.import_module("app.scripts.production_chat_session_start_500_diagnosis")


def test_verifier_importability():
    importlib.import_module("app.scripts.verify_phase_9w_chat_session_start_fix")


def test_session_schema_accepts_pro_v2_payload():
    payload = ChatSessionStartRequest(
        source_domain="join.alte.edu.ge",
        language="en",
        channel="website_chat",
        widget_variant="pro_v2_safe",
        metadata={"mode": "test_site", "page_url": "https://nimble-croissant-2f66e8.netlify.app/join.html"},
    )

    assert payload.channel == "website_chat"
    assert payload.source_domain == "join.alte.edu.ge"
    assert payload.language == "en"
    assert payload.widget_variant == "pro_v2_safe"
    assert payload.metadata["mode"] == "test_site"


def test_session_start_accepts_pro_v2_join_domain_without_contact_or_crm_creation(client, session_factory):
    response = client.post(
        "/chat/session/start",
        json={
            "source_domain": "join.alte.edu.ge",
            "language": "en",
            "channel": "website_chat",
            "widget_variant": "pro_v2_safe",
            "metadata": {"mode": "test"},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"]
    assert data["session_id"]
    assert data["source_domain"] == "join.alte.edu.ge"

    import asyncio

    async def count_crm_rows():
        async with session_factory() as session:
            leads = (await session.scalars(select(Lead))).all()
            customers = (await session.scalars(select(Customer))).all()
            tasks = (await session.scalars(select(Task))).all()
            return len(leads), len(customers), len(tasks)

    assert asyncio.run(count_crm_rows()) == (0, 0, 0)


def test_session_start_accepts_alte_domain_and_metadata_optional(client):
    response = client.post(
        "/chat/session/start",
        json={
            "source_domain": "alte.edu.ge",
            "language": "ka",
            "channel": "website_chat",
            "widget_variant": "pro_v2_safe",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"]
    assert data["session_id"]
    assert data["source_domain"] == "alte.edu.ge"


def test_error_response_does_not_expose_secrets(client):
    response = client.post("/chat/message", json={"conversation_id": "missing", "message": "hello"})

    assert response.status_code in {404, 500}
    text = response.text.lower()
    assert "database_url" not in text
    assert "password" not in text
    assert "sk-ant" not in text
    assert "anthropic_api_key" not in text
