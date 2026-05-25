from app.core.config import get_settings
from app.services.permission_service import permission_for_request, role_has_permission
from app.services.security_service import create_access_token


def test_missing_permission_mapping_denies_by_default():
    assert role_has_permission("admin", None) is False
    assert role_has_permission("operator", None) is False


def test_mapped_permissions_still_work():
    assert role_has_permission("admin", "dashboard:read") is True
    assert role_has_permission("operator", "inbox:read") is True
    assert role_has_permission("operator", "dashboard:read") is False


def test_unknown_protected_path_is_denied(client, monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    get_settings.cache_clear()
    token = create_access_token(subject="user-1", role="admin")
    try:
        response = client.get("/new-protected-endpoint", headers={"Authorization": f"Bearer {token}"})
    finally:
        monkeypatch.setenv("AUTH_REQUIRED", "false")
        get_settings.cache_clear()

    assert response.status_code == 403


def test_public_chat_widget_endpoints_still_bypass_auth(client, monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    get_settings.cache_clear()
    try:
        session = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "ka"})
        message = client.post(
            "/chat/message",
            json={
                "conversation_id": session.json()["conversation_id"],
                "session_id": session.json()["session_id"],
                "message": "სად მდებარეობს უნივერსიტეტი?",
                "source_domain": "alte.edu.ge",
                "language": "ka",
            },
        )
    finally:
        monkeypatch.setenv("AUTH_REQUIRED", "false")
        get_settings.cache_clear()

    assert session.status_code == 200
    assert message.status_code == 200
