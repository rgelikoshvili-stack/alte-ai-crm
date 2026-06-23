import asyncio

from sqlalchemy import func, select

from app.models import Customer, Lead, Task
from app.services.website_sync_preview_service import (
    classify_freshness,
    extract_readable_html,
    reset_website_sync_preview_state,
)


def add_source(client, **overrides):
    payload = {
        "name": "Official Alte admissions",
        "base_url": "https://alte.edu.ge",
        "allowed_paths": ["/ka"],
        "source_group_hint": "admissions_rules",
        "enabled": True,
        **overrides,
    }
    response = client.post("/api/knowledge/sync/website/sources", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def preview(client, source_id: str, url: str = "fixture://admissions-deadlines", **overrides):
    payload = {
        "source_id": source_id,
        "url": url,
        "mode": "single_url",
        "limit": 3,
        "dry_run": True,
        **overrides,
    }
    response = client.post("/api/knowledge/sync/website/preview", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


async def crm_counts(session_factory):
    async with session_factory() as session:
        return {
            "customers": await session.scalar(select(func.count()).select_from(Customer)),
            "leads": await session.scalar(select(func.count()).select_from(Lead)),
            "tasks": await session.scalar(select(func.count()).select_from(Task)),
        }


def test_phase_10m_add_and_list_website_source(client):
    reset_website_sync_preview_state()
    source = add_source(client)

    response = client.get("/api/knowledge/sync/website/sources")
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 1
    assert rows[0]["id"] == source["id"]
    assert rows[0]["base_url"] == "https://alte.edu.ge/"
    assert rows[0]["enabled"] is True


def test_phase_10m_rejects_unapproved_domain_and_private_paths(client):
    reset_website_sync_preview_state()

    external = client.post(
        "/api/knowledge/sync/website/sources",
        json={"name": "External", "base_url": "https://example.com", "allowed_paths": [], "enabled": True},
    )
    assert external.status_code == 400
    assert "not approved" in external.text

    admin_path = client.post(
        "/api/knowledge/sync/website/sources",
        json={"name": "Admin", "base_url": "https://alte.edu.ge/admin", "allowed_paths": [], "enabled": True},
    )
    assert admin_path.status_code == 400
    assert "blocked" in admin_path.text

    source = add_source(client, allowed_paths=["/ka"])
    login_preview = client.post(
        "/api/knowledge/sync/website/preview",
        json={"source_id": source["id"], "url": "https://alte.edu.ge/login", "mode": "single_url", "dry_run": True},
    )
    assert login_preview.status_code == 400
    assert "blocked" in login_preview.text


def test_phase_10m_preview_fixture_creates_draft_run_public_unusable(client):
    reset_website_sync_preview_state()
    source = add_source(client)
    run = preview(client, source["id"])

    assert run["status"] == "draft"
    assert run["public_usable"] is False
    assert run["source_url"] == "fixture://admissions-deadlines"
    assert run["canonical_url"] == "https://alte.edu.ge/ka/admissions"
    assert run["page_title"] == "Admissions deadlines"
    assert run["language"] == "ka"
    assert run["freshness_class"] == "variable"
    assert run["source_group_guess"] == "admissions_rules"
    assert run["chunks_count"] >= 1
    assert "script" not in run["extracted_text_preview"].lower()
    assert "Footer" not in run["extracted_text_preview"]
    assert "draft_not_public_usable" in run["risk_flags"]

    runs = client.get("/api/knowledge/sync/website/runs")
    assert runs.status_code == 200
    assert runs.json()[0]["run_id"] == run["run_id"]

    diff = client.get(f"/api/knowledge/sync/website/diff/{run['run_id']}")
    assert diff.status_code == 200
    assert diff.json()["approval_status"] == "disabled_preview_only"

    approve = client.post(f"/api/knowledge/sync/website/approve/{run['run_id']}")
    assert approve.status_code == 501


def test_phase_10m_extractor_removes_noisy_layout():
    html = """
    <html><head><title>Clean title</title><style>.bad{}</style></head>
    <body><header>Header text</header><nav>Navigation</nav><main><h1>Useful content</h1>
    <p>Library users may access reading spaces.</p></main><footer>Footer text</footer><script>alert(1)</script></body></html>
    """
    extracted = extract_readable_html(html)
    assert extracted.title == "Clean title"
    assert "Useful content" in extracted.text
    assert "Library users" in extracted.text
    assert "Header text" not in extracted.text
    assert "Navigation" not in extracted.text
    assert "Footer text" not in extracted.text
    assert "alert" not in extracted.text


def test_phase_10m_freshness_classifier_variable_and_stable():
    variable_cases = [
        "2028 წლის აკადემიური კალენდარი როდის არის?",
        "What is the application deadline?",
        "Medicine tuition fee is 12000 GEL",
        "გრანტი და დაფინანსება განახლებულია",
    ]
    for text in variable_cases:
        assert classify_freshness(text) == "variable"

    stable_cases = [
        "The Computer Science bachelor program is 240 ECTS credits and covers algorithms.",
        "Academic integrity is a general policy principle.",
        "Library users may access reading spaces and student services.",
    ]
    for text in stable_cases:
        assert classify_freshness(text) == "stable"


def test_phase_10m_draft_content_is_not_used_by_public_chatbot_or_knowledge_ask(client, session_factory):
    reset_website_sync_preview_state()
    source = add_source(client, source_group_hint="finance_sources")
    run = preview(client, source["id"], url="fixture://tuition")
    assert run["public_usable"] is False
    assert "12000 GEL" in run["extracted_text_preview"]

    ask = client.post("/api/knowledge/ask", json={"question": "What is the Medicine tuition fee?", "language": "en"})
    assert ask.status_code == 200
    ask_payload = ask.json()
    assert ask_payload["used_claude"] is False
    assert "12000 GEL" not in ask_payload["answer"]

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


def test_phase_10m_preview_does_not_create_crm_records(client, session_factory):
    reset_website_sync_preview_state()
    before = asyncio.run(crm_counts(session_factory))
    source = add_source(client)
    preview(client, source["id"])
    after = asyncio.run(crm_counts(session_factory))
    assert after == before
