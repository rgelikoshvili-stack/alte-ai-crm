import asyncio
from datetime import date, timedelta

from sqlalchemy import select

from app.models import KnowledgeSnippet, KnowledgeSource
from app.scripts import seed_alte_knowledge as seed_module


def test_seed_script_loads_alte_seed_and_is_idempotent(session_factory, monkeypatch):
    monkeypatch.setattr(seed_module, "AsyncSessionLocal", session_factory)

    first = asyncio.run(seed_module.seed_alte_knowledge())
    second = asyncio.run(seed_module.seed_alte_knowledge())

    assert first["sources_created"] > 0
    assert first["snippets_created"] > 0
    assert second["sources_created"] == 0
    assert second["snippets_created"] == 0
    assert second["skipped_existing"] >= first["snippets_created"]

    async def count_seeded():
        async with session_factory() as session:
            sources = (await session.scalars(select(KnowledgeSource))).all()
            snippets = (await session.scalars(select(KnowledgeSnippet))).all()
            return sources, snippets

    sources, snippets = asyncio.run(count_seeded())
    assert any(source.source_key == "alte_contact_v1" for source in sources)
    assert any(snippet.source_key == "alte_finance_safe_v1" for snippet in snippets)


def test_contact_search_in_georgian_returns_approved_seed_snippet(client, session_factory, monkeypatch):
    monkeypatch.setattr(seed_module, "AsyncSessionLocal", session_factory)
    asyncio.run(seed_module.seed_alte_knowledge())

    response = client.get("/knowledge/snippets/search?query=კონტაქტი ტელეფონი&language=ka&category=contact")

    assert response.status_code == 200
    data = response.json()
    assert data
    assert data[0]["source"]["source_key"] == "alte_contact_v1"
    assert data[0]["snippet"]["status"] == "approved"


def test_finance_tuition_search_returns_safe_handover_not_exact_price(client, session_factory, monkeypatch):
    monkeypatch.setattr(seed_module, "AsyncSessionLocal", session_factory)
    asyncio.run(seed_module.seed_alte_knowledge())

    response = client.get("/knowledge/snippets/search?query=tuition fee price&language=en&category=finance")

    assert response.status_code == 200
    data = response.json()
    assert data
    content = data[0]["snippet"]["content"].lower()
    assert "must be verified" in content
    assert "gel" not in content
    assert data[0]["snippet"]["sensitivity"] == "high"


def test_join_source_domain_search_returns_international_context(client, session_factory, monkeypatch):
    monkeypatch.setattr(seed_module, "AsyncSessionLocal", session_factory)
    asyncio.run(seed_module.seed_alte_knowledge())

    response = client.get(
        "/knowledge/snippets/search?query=international medicine visa&language=en"
        "&source_domain=join.alte.edu.ge&category=international_admissions"
    )

    assert response.status_code == 200
    data = response.json()
    assert data
    assert data[0]["source"]["source_key"] == "alte_international_v1"
    assert data[0]["snippet"]["source_domain"] == "join.alte.edu.ge"


def test_medicine_query_returns_high_sensitivity_context(client, session_factory, monkeypatch):
    monkeypatch.setattr(seed_module, "AsyncSessionLocal", session_factory)
    asyncio.run(seed_module.seed_alte_knowledge())

    response = client.get("/knowledge/snippets/search?query=medicine md visa&language=en&sensitivity=high")

    assert response.status_code == 200
    data = response.json()
    assert data
    assert any(item["snippet"]["program_name"] == "Medicine / 6-year MD" for item in data)
    assert all(item["snippet"]["sensitivity"] == "high" for item in data)


def test_draft_snippets_excluded_by_default_with_seed_metadata(client):
    source = client.post(
        "/knowledge/sources",
        json={
            "source_key": "draft_source",
            "title": "Draft",
            "source_type": "manual",
            "status": "approved",
            "language": "en",
            "category": "finance",
        },
    ).json()
    client.post(
        "/knowledge/snippets",
        json={
            "source_id": source["id"],
            "source_key": "draft_source",
            "title": "Draft tuition",
            "content": "Draft tuition content.",
            "category": "finance",
            "keywords": "tuition",
            "status": "draft",
            "language": "en",
            "sensitivity": "high",
        },
    )

    response = client.get("/knowledge/snippets/search?query=tuition&language=en")

    assert response.status_code == 200
    assert response.json() == []


def test_archived_sources_excluded_by_default_with_seed_metadata(client):
    source = client.post(
        "/knowledge/sources",
        json={
            "source_key": "archived_source",
            "title": "Archived",
            "source_type": "manual",
            "status": "archived",
            "language": "en",
            "category": "contact",
        },
    ).json()
    client.post(
        "/knowledge/snippets",
        json={
            "source_id": source["id"],
            "source_key": "archived_source",
            "title": "Archived contact",
            "content": "Archived contact content.",
            "category": "contact",
            "keywords": "contact",
            "status": "approved",
            "language": "en",
        },
    )

    response = client.get("/knowledge/snippets/search?query=contact&language=en")

    assert response.status_code == 200
    assert response.json() == []


def test_stale_snippet_excluded_or_flagged_by_include_stale(client):
    source = client.post(
        "/knowledge/sources",
        json={
            "source_key": "stale_source",
            "title": "Stale",
            "source_type": "manual",
            "status": "approved",
            "language": "en",
            "category": "finance",
        },
    ).json()
    client.post(
        "/knowledge/snippets",
        json={
            "source_id": source["id"],
            "source_key": "stale_source",
            "title": "Stale tuition",
            "content": "Tuition details must be verified.",
            "category": "finance",
            "keywords": "tuition",
            "status": "approved",
            "language": "en",
            "effective_to": (date.today() - timedelta(days=1)).isoformat(),
        },
    )

    fresh_only = client.get("/knowledge/snippets/search?query=tuition&language=en")
    with_stale = client.get("/knowledge/snippets/search?query=tuition&language=en&include_stale=true")

    assert fresh_only.status_code == 200
    assert fresh_only.json() == []
    assert with_stale.status_code == 200
    assert with_stale.json()[0]["source_status"] == "source_stale"
    assert with_stale.json()[0]["is_stale"] is True
