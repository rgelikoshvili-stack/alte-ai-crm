from datetime import UTC, date, datetime, timedelta


def create_customer(client, country="Georgia"):
    response = client.post(
        "/customers",
        json={
            "first_name": "Ana",
            "last_name": "Operator",
            "email": "ana.analytics@example.com",
            "phone": "599111222",
            "country": country,
        },
    )
    assert response.status_code == 200
    return response.json()


def create_lead(client, customer_id, **overrides):
    payload = {
        "customer_id": customer_id,
        "program": "Business",
        "status": "open",
        "priority": "urgent",
        "source_channel": "website_chat",
        "source_domain": "join.alte.edu.ge",
        "is_international_priority": True,
        "medical_track": True,
        "lead_score": 91,
        "qualification_status": "hot",
    }
    payload.update(overrides)
    response = client.post("/leads", json=payload)
    assert response.status_code == 200
    return response.json()


def create_ai_message(client, metadata):
    conversation = client.post("/conversations", json={"channel": "website_chat", "status": "open"}).json()
    response = client.post(
        f"/conversations/{conversation['id']}/messages",
        json={"sender_type": "ai", "text": "AI reply", "metadata_json": metadata},
    )
    assert response.status_code == 200
    return conversation


def test_analytics_overview_returns_zeros_on_empty_db(client):
    response = client.get("/analytics/overview")

    assert response.status_code == 200
    data = response.json()
    assert data["total_leads"] == 0
    assert data["average_lead_score"] == 0.0
    assert data["knowledge_no_source_count"] == 0


def test_analytics_overview_counts_leads_tasks_and_ai_source_status(client):
    customer = create_customer(client)
    create_lead(client, customer["id"])
    client.post(
        "/tasks",
        json={
            "customer_id": customer["id"],
            "title": "Overdue SLA",
            "priority": "urgent",
            "due_date": (datetime.now(UTC) - timedelta(hours=2)).isoformat(),
        },
    )
    create_ai_message(
        client,
        {
            "intent": "tuition_fee",
            "confidence": 0.8,
            "answer_source_status": "no_approved_source_found",
            "qualification": {"handover_required": True},
        },
    )

    response = client.get("/analytics/overview")

    assert response.status_code == 200
    data = response.json()
    assert data["total_leads"] == 1
    assert data["hot_leads"] == 1
    assert data["average_lead_score"] == 91.0
    assert data["overdue_tasks"] == 1
    assert data["knowledge_no_source_count"] == 1


def test_lead_analytics_groups_core_dimensions(client):
    customer = create_customer(client, country="India")
    create_lead(client, customer["id"], program="Medicine / 6-year MD")

    response = client.get("/analytics/leads")

    assert response.status_code == 200
    data = response.json()
    assert {"key": "open", "count": 1} in data["leads_by_status"]
    assert {"key": "join.alte.edu.ge", "count": 1} in data["leads_by_source_domain"]
    assert {"key": "India", "count": 1} in data["leads_by_country"]
    assert data["international_priority_count"] == 1
    assert data["medical_track_count"] == 1


def test_sla_analytics_counts_overdue_due_today_and_handover(client):
    customer = create_customer(client)
    client.post(
        "/tasks",
        json={
            "customer_id": customer["id"],
            "title": "Due today",
            "priority": "urgent",
            "due_date": (datetime.now(UTC) + timedelta(hours=3)).isoformat(),
        },
    )
    client.post("/conversations", json={"channel": "website_chat", "status": "open", "human_handover": True})

    response = client.get("/analytics/sla")

    assert response.status_code == 200
    data = response.json()
    assert data["due_today_tasks"] == 1
    assert data["urgent_open_tasks"] == 1
    assert data["open_handover_conversations"] == 1


def test_knowledge_analytics_counts_status_language_stale_and_ai_events(client):
    source = client.post(
        "/knowledge/sources",
        json={"title": "Admissions FAQ", "source_type": "faq", "status": "approved", "language": "en"},
    ).json()
    client.post(
        "/knowledge/snippets",
        json={
            "source_id": source["id"],
            "title": "Old tuition",
            "content": "Old content",
            "category": "tuition",
            "keywords": "tuition",
            "effective_to": date(2020, 1, 1).isoformat(),
            "status": "approved",
            "language": "en",
        },
    )
    create_ai_message(client, {"answer_source_status": "answered_from_approved_source", "confidence": 0.9})

    response = client.get("/analytics/knowledge")

    assert response.status_code == 200
    data = response.json()
    assert data["total_sources"] == 1
    assert {"key": "approved", "count": 1} in data["sources_by_status"]
    assert data["stale_snippets"] == 1
    assert data["answered_from_source_events"] == 1


def test_ai_analytics_counts_intents_statuses_and_confidence(client):
    create_ai_message(
        client,
        {
            "intent": "application",
            "confidence": 0.75,
            "answer_source_status": "answered_from_approved_source",
            "qualification": {"handover_required": True},
        },
    )

    response = client.get("/analytics/ai")

    assert response.status_code == 200
    data = response.json()
    assert data["total_ai_messages"] == 1
    assert data["average_confidence"] == 0.75
    assert {"key": "application", "count": 1} in data["intents"]
    assert data["handover_recommended_count"] == 1

