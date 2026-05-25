import asyncio

from sqlalchemy import select

from app.core.config import get_settings
from app.models import Lead, Task
from app.services import ai_service


def fetch_all(session_factory, query):
    async def run():
        async with session_factory() as session:
            return (await session.scalars(query)).all()

    return asyncio.run(run())


def set_claude_env(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "claude")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    get_settings.cache_clear()


def test_claude_provider_exception_returns_structured_fallback(monkeypatch):
    set_claude_env(monkeypatch)
    monkeypatch.setattr(ai_service, "call_claude", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom secret")))

    try:
        analysis, meta = ai_service.analyze_with_ai("რა ღირს სწავლა?", language_hint="ka")
    finally:
        get_settings.cache_clear()

    assert meta["fallback"] is True
    assert meta["error_type"] == "RuntimeError"
    assert analysis.reply == "ამ მომენტში AI სერვისთან კავშირი შეფერხებულია. ამ საკითხზე დაგაკავშირებთ შესაბამის დეპარტამენტთან."
    assert analysis.confidence == 0.0
    assert analysis.should_handover is True
    assert analysis.should_create_lead is False
    assert analysis.used_sources == []
    assert "ai_provider_error" in analysis.risk_flags
    assert "boom" not in analysis.reply
    assert "secret" not in analysis.reply.lower()


def test_chat_message_provider_failure_returns_safe_ka_response(client, session_factory, monkeypatch):
    set_claude_env(monkeypatch)
    monkeypatch.setattr(ai_service, "call_claude", lambda *args, **kwargs: (_ for _ in ()).throw(ConnectionError("provider down")))
    session = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "ka"}).json()

    try:
        response = client.post(
            "/chat/message",
            json={
                "conversation_id": session["conversation_id"],
                "session_id": session["session_id"],
                "message": "საფასური მაინტერესებს",
                "source_domain": "alte.edu.ge",
                "language": "ka",
            },
        )
    finally:
        get_settings.cache_clear()

    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "ამ მომენტში AI სერვისთან კავშირი შეფერხებულია. ამ საკითხზე დაგაკავშირებთ შესაბამის დეპარტამენტთან."
    assert data["should_handover"] is True
    assert data["should_create_lead"] is False
    assert data["created_lead_id"] is None
    assert data["created_task_id"] is None
    assert fetch_all(session_factory, select(Lead)) == []
    assert fetch_all(session_factory, select(Task)) == []
    assert "provider down" not in data["reply"]


def test_chat_message_provider_failure_returns_safe_en_response(client, monkeypatch):
    set_claude_env(monkeypatch)
    monkeypatch.setattr(ai_service, "call_claude", lambda *args, **kwargs: (_ for _ in ()).throw(TimeoutError("timeout token")))
    session = client.post("/chat/session/start", json={"source_domain": "join.alte.edu.ge", "language": "en"}).json()

    try:
        response = client.post(
            "/chat/message",
            json={
                "conversation_id": session["conversation_id"],
                "session_id": session["session_id"],
                "message": "I need admissions help",
                "source_domain": "join.alte.edu.ge",
                "language": "en",
            },
        )
    finally:
        get_settings.cache_clear()

    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "The AI service is temporarily unavailable. I can connect you with the relevant department."
    assert data["should_handover"] is True
    assert data["should_create_lead"] is False
    assert data["created_task_id"] is None
    assert "timeout" not in data["reply"].lower()
