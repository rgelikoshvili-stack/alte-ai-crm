from datetime import UTC, datetime, timedelta


def create_customer(client, email="operator@example.com", phone="599777888"):
    response = client.post(
        "/customers",
        json={"first_name": "Operator", "last_name": "User", "email": email, "phone": phone},
    )
    assert response.status_code == 200
    return response.json()


def create_pipeline_stage(client):
    pipeline_response = client.post("/pipelines", json={"name": "Admissions Pipeline"})
    assert pipeline_response.status_code == 200
    pipeline = pipeline_response.json()
    stage_response = client.post(
        "/pipeline-stages",
        json={"pipeline_id": pipeline["id"], "name": "New Lead", "order": 1},
    )
    assert stage_response.status_code == 200
    return pipeline, stage_response.json()


def create_lead(client, customer_id, **overrides):
    payload = {
        "customer_id": customer_id,
        "interest_area": "Admissions",
        "program": "Business",
        "status": "open",
        "priority": "high",
        "source_channel": "website_chat",
        "source_domain": "join.alte.edu.ge",
        "is_international_priority": True,
        "medical_track": False,
    }
    payload.update(overrides)
    response = client.post("/leads", json=payload)
    assert response.status_code == 200
    return response.json()


def test_dashboard_overview_returns_zeros_on_empty_db(client):
    response = client.get("/dashboard/overview")

    assert response.status_code == 200
    data = response.json()
    assert data["total_customers"] == 0
    assert data["total_leads"] == 0
    assert data["latest_conversations"] == []


def test_dashboard_overview_returns_counts(client):
    customer = create_customer(client)
    lead = create_lead(client, customer["id"])
    session = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "en"}).json()
    client.post(
        "/tasks",
        json={
            "lead_id": lead["id"],
            "customer_id": customer["id"],
            "title": "Follow up",
            "status": "open",
            "due_date": (datetime.now(UTC) - timedelta(days=1)).isoformat(),
        },
    )

    response = client.get("/dashboard/overview")

    assert response.status_code == 200
    data = response.json()
    assert data["total_customers"] == 1
    assert data["total_leads"] == 1
    assert data["total_conversations"] == 1
    assert data["open_tasks"] == 1
    assert data["overdue_tasks"] == 1
    assert data["latest_conversations"][0]["conversation_id"] == session["conversation_id"]


def test_inbox_filtering_and_pagination(client):
    session = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "en"}).json()
    client.post(
        "/chat/message",
        json={"conversation_id": session["conversation_id"], "message": "Hello contact", "source_domain": "alte.edu.ge"},
    )

    response = client.get("/inbox?limit=1&offset=0&channel=website_chat&q=Hello")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["channel"] == "website_chat"
    assert data[0]["last_message_text"]


def test_conversation_detail_includes_messages(client):
    session = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "en"}).json()
    client.post(
        "/chat/message",
        json={"conversation_id": session["conversation_id"], "message": "Hello", "source_domain": "alte.edu.ge"},
    )

    response = client.get(f"/conversations/{session['conversation_id']}/detail")

    assert response.status_code == 200
    assert len(response.json()["messages"]) == 2


def test_leads_filters_by_source_domain_and_medical_track(client):
    customer = create_customer(client)
    create_lead(client, customer["id"], medical_track=True, program="Medicine / 6-year MD")

    response = client.get("/leads?source_domain=join.alte.edu.ge&medical_track=true")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["medical_track"] is True


def test_lead_detail_includes_customer_tasks_and_stage_history(client):
    customer = create_customer(client)
    _, first_stage = create_pipeline_stage(client)
    _, second_stage = create_pipeline_stage(client)
    lead = create_lead(client, customer["id"], stage_id=first_stage["id"])
    client.patch(f"/leads/{lead['id']}/stage", json={"stage_id": second_stage["id"], "changed_by": "operator"})
    client.post("/tasks", json={"lead_id": lead["id"], "customer_id": customer["id"], "title": "Call lead"})

    response = client.get(f"/leads/{lead['id']}/detail")

    assert response.status_code == 200
    data = response.json()
    assert data["customer"]["id"] == customer["id"]
    assert len(data["tasks"]) == 1
    assert len(data["stage_history"]) == 1


def test_tasks_overdue_filter(client):
    customer = create_customer(client)
    client.post(
        "/tasks",
        json={
            "customer_id": customer["id"],
            "title": "Overdue task",
            "due_date": (datetime.now(UTC) - timedelta(days=1)).isoformat(),
        },
    )

    response = client.get("/tasks?overdue=true")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_pipeline_board_returns_stages_and_lead_counts(client):
    customer = create_customer(client)
    pipeline, stage = create_pipeline_stage(client)
    create_lead(client, customer["id"], stage_id=stage["id"])

    response = client.get(f"/pipelines/{pipeline['id']}/board")

    assert response.status_code == 200
    data = response.json()
    assert data["pipeline"]["id"] == pipeline["id"]
    assert data["stages"][0]["lead_count"] == 1


def test_knowledge_sources_filters_exclude_archived_by_default(client):
    client.post(
        "/knowledge/sources",
        json={"title": "Archived", "source_type": "faq", "status": "archived", "language": "en"},
    )

    response = client.get("/knowledge/sources")

    assert response.status_code == 200
    assert response.json() == []


def test_knowledge_snippet_search_excludes_draft_by_default(client):
    source = client.post(
        "/knowledge/sources",
        json={"title": "Approved", "source_type": "faq", "status": "approved", "language": "en"},
    ).json()
    client.post(
        "/knowledge/snippets",
        json={
            "source_id": source["id"],
            "title": "Draft tuition",
            "content": "Draft tuition content",
            "category": "tuition",
            "keywords": "tuition",
            "status": "draft",
            "language": "en",
        },
    )

    response = client.get("/knowledge/snippets/search?q=tuition&language=en")

    assert response.status_code == 200
    assert response.json() == []
