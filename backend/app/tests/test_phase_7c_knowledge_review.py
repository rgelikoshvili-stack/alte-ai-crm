import asyncio
from datetime import date, timedelta

from sqlalchemy import select

from app.models import AuditLog, KnowledgeSnippet


def create_source(client, **overrides):
    payload = {
        "source_key": "phase7c_source",
        "title": "Phase 7C Source",
        "source_type": "manual",
        "status": "approved",
        "language": "en",
        "category": "finance",
        "sensitivity": "high",
        "review_required": True,
    }
    payload.update(overrides)
    response = client.post("/knowledge/sources", json=payload)
    assert response.status_code == 200
    return response.json()


def create_snippet(client, source_id, **overrides):
    payload = {
        "source_id": source_id,
        "source_key": "phase7c_source",
        "title": "Tuition review item",
        "content": "Exact tuition must be verified by Finance.",
        "category": "finance",
        "keywords": "tuition fee finance",
        "status": "draft",
        "language": "en",
        "sensitivity": "high",
        "review_required": True,
    }
    payload.update(overrides)
    response = client.post("/knowledge/snippets", json=payload)
    assert response.status_code == 200
    return response.json()


def test_review_queue_returns_review_required_high_sensitivity_items(client):
    source = create_source(client)
    snippet = create_snippet(client, source["id"])

    response = client.get("/knowledge/review-queue?sensitivity=high&review_required=true")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["snippet"]["id"] == snippet["id"]
    assert "review_required" in data[0]["reasons"]
    assert "high_sensitivity" in data[0]["reasons"]


def test_review_queue_filters_stale_items(client):
    source = create_source(client, review_required=False)
    stale_to = (date.today() - timedelta(days=1)).isoformat()
    snippet = create_snippet(
        client,
        source["id"],
        status="approved",
        review_required=False,
        effective_to=stale_to,
    )

    response = client.get("/knowledge/review-queue?stale=true")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["snippet"]["id"] == snippet["id"]
    assert data[0]["is_stale"] is True
    assert "source_stale" in data[0]["reasons"]


def test_patch_source_updates_metadata_and_audits(client, session_factory):
    source = create_source(client, category="admissions", review_required=False)

    response = client.patch(
        f"/knowledge/sources/{source['id']}",
        json={"category": "finance", "review_required": True, "sensitivity": "high"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "finance"
    assert data["review_required"] is True

    async def load_audit():
        async with session_factory() as session:
            return await session.scalar(
                select(AuditLog).where(
                    AuditLog.action == "knowledge_source_updated",
                    AuditLog.entity_id == source["id"],
                )
            )

    audit = asyncio.run(load_audit())
    assert audit is not None


def test_patch_snippet_updates_metadata_and_audits(client, session_factory):
    source = create_source(client)
    snippet = create_snippet(client, source["id"])

    response = client.patch(
        f"/knowledge/snippets/{snippet['id']}",
        json={"title": "Updated tuition review", "review_required": False},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated tuition review"
    assert data["review_required"] is False

    async def load_audit():
        async with session_factory() as session:
            return await session.scalar(
                select(AuditLog).where(
                    AuditLog.action == "knowledge_snippet_updated",
                    AuditLog.entity_id == snippet["id"],
                )
            )

    audit = asyncio.run(load_audit())
    assert audit is not None


def test_approve_snippet_sets_approved_and_audits(client, session_factory):
    source = create_source(client, status="draft")
    snippet = create_snippet(client, source["id"], status="draft")

    response = client.patch(f"/knowledge/snippets/{snippet['id']}/approve?approved_by=qa")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["review_required"] is False

    async def load_state():
        async with session_factory() as session:
            stored = await session.get(KnowledgeSnippet, snippet["id"])
            audit = await session.scalar(
                select(AuditLog).where(
                    AuditLog.action == "knowledge_snippet_approved",
                    AuditLog.entity_id == snippet["id"],
                )
            )
            return stored, audit

    stored, audit = asyncio.run(load_state())
    assert stored.status == "approved"
    assert audit is not None


def test_archive_snippet_hides_from_search_and_audits(client, session_factory):
    source = create_source(client, review_required=False, sensitivity="low")
    snippet = create_snippet(
        client,
        source["id"],
        status="approved",
        review_required=False,
        sensitivity="low",
        keywords="contact archived",
        category="contact",
    )

    response = client.patch(f"/knowledge/snippets/{snippet['id']}/archive")
    search = client.get("/knowledge/snippets/search?query=archived&language=en&category=contact")

    assert response.status_code == 200
    assert response.json()["status"] == "archived"
    assert search.status_code == 200
    assert search.json() == []

    async def load_audit():
        async with session_factory() as session:
            return await session.scalar(
                select(AuditLog).where(
                    AuditLog.action == "knowledge_snippet_archived",
                    AuditLog.entity_id == snippet["id"],
                )
            )

    audit = asyncio.run(load_audit())
    assert audit is not None


def test_archived_sources_can_be_filtered_explicitly(client):
    create_source(client, status="archived")

    default_response = client.get("/knowledge/sources")
    archived_response = client.get("/knowledge/sources?status=archived")

    assert default_response.status_code == 200
    assert default_response.json() == []
    assert archived_response.status_code == 200
    assert len(archived_response.json()) == 1
