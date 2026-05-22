from datetime import date, timedelta


def create_source(client, status="approved", language="ka", title="Admissions Source"):
    response = client.post(
        "/knowledge/sources",
        json={
            "title": title,
            "source_type": "faq",
            "status": status,
            "language": language,
            "owner": "Admissions",
            "approved_by": "manager" if status == "approved" else None,
        },
    )
    assert response.status_code == 200
    return response.json()


def create_snippet(client, source_id, **overrides):
    payload = {
        "source_id": source_id,
        "title": "Business program admission requirements",
        "content": "Business program admission requires application and documents.",
        "category": "admissions",
        "program_name": "Business",
        "keywords": "business admission requirements application",
        "status": "approved",
        "language": "en",
    }
    payload.update(overrides)
    response = client.post("/knowledge/snippets", json=payload)
    assert response.status_code == 200
    return response.json()


def test_create_knowledge_source(client):
    source = create_source(client)

    assert source["title"] == "Admissions Source"
    assert source["status"] == "approved"


def test_create_approved_snippet(client):
    source = create_source(client, language="en")
    snippet = create_snippet(client, source["id"])

    assert snippet["source_id"] == source["id"]
    assert snippet["status"] == "approved"


def test_search_returns_approved_snippets(client):
    source = create_source(client, language="en")
    create_snippet(client, source["id"])

    response = client.get("/knowledge/snippets/search?query=business admission&language=en&include_stale=true")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["source_status"] == "answered_from_approved_source"


def test_archived_source_excluded(client):
    source = create_source(client, status="archived", language="en")
    create_snippet(client, source["id"])

    response = client.get("/knowledge/snippets/search?query=business admission&language=en&include_stale=true")

    assert response.status_code == 200
    assert response.json() == []


def test_draft_snippet_excluded_by_default(client):
    source = create_source(client, language="en")
    create_snippet(client, source["id"], status="draft")

    response = client.get("/knowledge/snippets/search?query=business admission&language=en&include_stale=true")

    assert response.status_code == 200
    assert response.json() == []


def test_language_filtering(client):
    source = create_source(client, language="en")
    create_snippet(client, source["id"], language="en")

    response = client.get("/knowledge/snippets/search?query=business admission&language=ka")

    assert response.status_code == 200
    assert response.json() == []


def test_program_keyword_matching(client):
    source = create_source(client, language="en")
    create_snippet(client, source["id"], program_name="Business")

    response = client.get("/knowledge/snippets/search?query=business&language=en&program_name=Business")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["score"] > 0


def test_stale_snippet_flagged(client):
    source = create_source(client, language="en")
    stale_date = (date.today() - timedelta(days=1)).isoformat()
    create_snippet(client, source["id"], effective_to=stale_date)

    response = client.get("/knowledge/snippets/search?query=business admission&language=en&include_stale=true")

    assert response.status_code == 200
    assert response.json()[0]["source_status"] == "source_stale"
