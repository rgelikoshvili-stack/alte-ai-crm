import asyncio

from sqlalchemy import select

from app.models import AuditLog, LeadStageHistory


def fetch_one(session_factory, query):
    async def run():
        async with session_factory() as session:
            return await session.scalar(query)

    return asyncio.run(run())


def create_customer(client, phone="+995599000001", email="student@example.com"):
    response = client.post(
        "/customers",
        json={
            "first_name": "Nino",
            "last_name": "Beridze",
            "phone": phone,
            "email": email,
            "source_channel": "website_chat",
            "consent_status": "granted",
        },
    )
    assert response.status_code == 200
    return response.json()


def create_pipeline_with_stage(client, name="Admissions", stage="New Lead"):
    pipeline_response = client.post("/pipelines", json={"name": name})
    assert pipeline_response.status_code == 200
    pipeline = pipeline_response.json()
    stage_response = client.post(
        "/pipeline-stages",
        json={"pipeline_id": pipeline["id"], "name": stage, "order": 1},
    )
    assert stage_response.status_code == 200
    return pipeline, stage_response.json()


def test_create_department(client):
    response = client.post(
        "/departments",
        json={
            "name": "Admissions",
            "description": "Student admissions",
            "default_queue": "admissions",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Admissions"
    assert data["is_active"] is True


def test_create_customer(client):
    data = create_customer(client)

    assert data["first_name"] == "Nino"
    assert data["phone"] == "+995599000001"


def test_duplicate_customer_by_phone_reuses_existing_customer(client):
    first = create_customer(client, phone="+995599000002", email="first@example.com")
    second_response = client.post(
        "/customers",
        json={
            "first_name": "Updated",
            "phone": "+995599000002",
            "email": "second@example.com",
        },
    )

    assert second_response.status_code == 200
    second = second_response.json()
    assert second["id"] == first["id"]
    assert second["first_name"] == "Updated"


def test_duplicate_customer_by_email_reuses_existing_customer(client):
    first = create_customer(client, phone="+995599000003", email="same@example.com")
    second_response = client.post(
        "/customers",
        json={
            "first_name": "Email",
            "email": "same@example.com",
        },
    )

    assert second_response.status_code == 200
    second = second_response.json()
    assert second["id"] == first["id"]
    assert second["first_name"] == "Email"


def test_create_join_domain_international_priority_lead(client):
    customer = create_customer(client)
    response = client.post(
        "/leads",
        json={
            "customer_id": customer["id"],
            "interest_area": "International admission",
            "source_domain": "join.alte.edu.ge",
            "is_international_priority": True,
            "priority": "high",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["source_domain"] == "join.alte.edu.ge"
    assert data["is_international_priority"] is True
    assert data["priority"] == "high"


def test_create_medical_lead(client):
    customer = create_customer(client)
    response = client.post(
        "/leads",
        json={
            "customer_id": customer["id"],
            "interest_area": "Medicine",
            "program": "6-year MD",
            "medical_track": True,
            "priority": "urgent",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["medical_track"] is True
    assert data["program"] == "6-year MD"


def test_change_lead_stage_creates_history(client, session_factory):
    customer = create_customer(client)
    _, first_stage = create_pipeline_with_stage(client, stage="New Lead")
    _, second_stage = create_pipeline_with_stage(client, name="Medicine", stage="Eligibility Check")
    lead_response = client.post(
        "/leads",
        json={"customer_id": customer["id"], "stage_id": first_stage["id"]},
    )
    assert lead_response.status_code == 200
    lead = lead_response.json()

    response = client.patch(
        f"/leads/{lead['id']}/stage",
        json={"stage_id": second_stage["id"], "changed_by": "operator-1"},
    )

    assert response.status_code == 200
    assert response.json()["stage_id"] == second_stage["id"]
    history = fetch_one(
        session_factory,
        select(LeadStageHistory).where(LeadStageHistory.lead_id == lead["id"]),
    )
    assert history is not None
    assert history.from_stage_id == first_stage["id"]
    assert history.to_stage_id == second_stage["id"]


def test_create_task_creates_audit_log(client, session_factory):
    response = client.post("/tasks", json={"title": "Follow up applicant", "priority": "normal"})

    assert response.status_code == 200
    task = response.json()
    audit = fetch_one(
        session_factory,
        select(AuditLog).where(AuditLog.action == "task_created", AuditLog.entity_id == task["id"]),
    )
    assert audit is not None


def test_create_conversation_and_message(client):
    customer = create_customer(client)
    conversation_response = client.post(
        "/conversations",
        json={"customer_id": customer["id"], "channel": "website_chat", "language": "ka"},
    )
    assert conversation_response.status_code == 200
    conversation = conversation_response.json()

    message_response = client.post(
        f"/conversations/{conversation['id']}/messages",
        json={"sender_type": "user", "text": "მაინტერესებს მიღება"},
    )

    assert message_response.status_code == 200
    assert message_response.json()["text"] == "მაინტერესებს მიღება"


def test_create_deadline_tracking_record(client):
    response = client.post(
        "/deadlines",
        json={
            "deadline_type": "academic_calendar",
            "title": "Fall enrollment deadline",
            "deadline_date": "2026-09-01",
            "program": "all",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["deadline_type"] == "academic_calendar"
    assert data["is_active"] is True
