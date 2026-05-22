import asyncio

from app.core.config import get_settings
from app.models import AuditLog, User
from app.services.credential_response_sanitizer import (
    assert_no_forbidden_response_fields,
    mask_value,
    sanitize_response,
)
from app.services.security_service import create_access_token, hash_password, verify_password


def test_password_hash_and_verify():
    stored = hash_password("safe-password")
    assert stored != "safe-password"
    assert verify_password("safe-password", stored)
    assert not verify_password("wrong-password", stored)


def test_token_round_trip_with_me_endpoint(client, session_factory):
    async def create_user():
        async with session_factory() as session:
            user = User(
                name="Admin User",
                email="admin@alte.edu.ge",
                role="admin",
                password_hash=hash_password("password123"),
            )
            session.add(user)
            await session.commit()

    asyncio.run(create_user())

    response = client.post("/auth/login", json={"email": "admin@alte.edu.ge", "password": "password123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["user"]["email"] == "admin@alte.edu.ge"
    assert "password_hash" not in me.text


def test_login_failure_is_audited(client, session_factory):
    response = client.post("/auth/login", json={"email": "missing@alte.edu.ge", "password": "bad"})
    assert response.status_code == 401

    async def audit_count():
        async with session_factory() as session:
            from sqlalchemy import select

            return (await session.scalars(select(AuditLog).where(AuditLog.action == "login_failed"))).all()

    assert len(asyncio.run(audit_count())) == 1


def test_auth_required_blocks_operator_endpoint_without_token(client, monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    get_settings.cache_clear()
    try:
        response = client.get("/dashboard/overview")
        assert response.status_code == 401
    finally:
        monkeypatch.setenv("AUTH_REQUIRED", "false")
        get_settings.cache_clear()


def test_auth_required_allows_admin_token_for_operator_endpoint(client, monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    get_settings.cache_clear()
    token = create_access_token(subject="user-1", role="admin")
    try:
        response = client.get("/dashboard/overview", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.headers.get("X-Correlation-ID")
    finally:
        monkeypatch.setenv("AUTH_REQUIRED", "false")
        get_settings.cache_clear()


def test_auth_required_denies_role_without_permission(client, monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    get_settings.cache_clear()
    token = create_access_token(subject="user-1", role="operator")
    try:
        response = client.get("/dashboard/overview", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403
    finally:
        monkeypatch.setenv("AUTH_REQUIRED", "false")
        get_settings.cache_clear()


def test_public_chat_remains_open_when_auth_required(client, monkeypatch):
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    get_settings.cache_clear()
    try:
        response = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "ka"})
        assert response.status_code == 200
    finally:
        monkeypatch.setenv("AUTH_REQUIRED", "false")
        get_settings.cache_clear()


def test_response_sanitizer_removes_secret_fields():
    payload = {
        "user": {"email": "admin@alte.edu.ge", "password_hash": "raw"},
        "access_token": "secret",
        "nested": [{"client_secret": "secret"}, {"safe": True}],
    }
    sanitized = sanitize_response(payload)
    assert sanitized == {"user": {"email": "admin@alte.edu.ge"}, "nested": [{}, {"safe": True}]}
    assert_no_forbidden_response_fields(sanitized)
    assert mask_value("abcdef123456") == "****3456"
