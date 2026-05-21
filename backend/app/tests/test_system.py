from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_returns_status_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "alte-ai-crm",
        "environment": "test",
        "version": "0.1.0",
    }


def test_version_returns_service_and_version() -> None:
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {
        "service": "alte-ai-crm",
        "version": "0.1.0",
    }
