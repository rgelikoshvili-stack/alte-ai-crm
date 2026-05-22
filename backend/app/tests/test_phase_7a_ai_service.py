import asyncio
import json

from sqlalchemy import select

from app.core.config import get_settings
from app.models import AIInteraction, KnowledgeSource
from app.schemas.chat import AIAnalysisResult
from app.services import ai_service


def valid_claude_payload(**overrides):
    payload = {
        "reply": "A consultant can help with your application.",
        "language": "en",
        "intent": "admission_interest",
        "confidence": 0.91,
        "should_create_lead": True,
        "should_handover": False,
        "department": "Admissions",
        "priority": "high",
        "missing_fields": [],
        "extracted_contact": {
            "first_name": "Nino",
            "last_name": "Beridze",
            "phone": "+995599000000",
            "email": "nino@example.com",
            "country": None,
            "city": None,
        },
        "interest_area": "Admissions",
        "program": "Business",
        "program_language": "en",
        "source_domain": "alte.edu.ge",
        "conversation_summary": "Business admissions interest with contact.",
        "used_sources": ["Admissions FAQ"],
        "risk_flags": [],
    }
    payload.update(overrides)
    return payload


def test_mock_mode_still_returns_ai_analysis(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    get_settings.cache_clear()
    try:
        analysis, meta = ai_service.analyze_with_ai("I want business admission", source_domain="alte.edu.ge")
    finally:
        get_settings.cache_clear()

    assert isinstance(analysis, AIAnalysisResult)
    assert meta["provider"] == "mock"
    assert analysis.intent == "admission_interest"


def test_claude_valid_json_parses_to_ai_analysis(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "claude")
    get_settings.cache_clear()
    monkeypatch.setattr(ai_service, "call_claude", lambda *args, **kwargs: json.dumps(valid_claude_payload()))
    try:
        analysis, meta = ai_service.analyze_with_ai("I want business admission", source_domain="alte.edu.ge")
    finally:
        monkeypatch.setenv("AI_PROVIDER", "mock")
        get_settings.cache_clear()

    assert meta["provider"] == "claude"
    assert analysis.intent == "admission_interest"
    assert analysis.confidence == 0.91
    assert analysis.extracted_contact.email == "nino@example.com"


def test_claude_invalid_json_returns_safe_fallback(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "claude")
    get_settings.cache_clear()
    monkeypatch.setattr(ai_service, "call_claude", lambda *args, **kwargs: "not json")
    try:
        analysis, meta = ai_service.analyze_with_ai("What is tuition?", source_domain="alte.edu.ge")
    finally:
        monkeypatch.setenv("AI_PROVIDER", "mock")
        get_settings.cache_clear()

    assert meta["fallback"] is True
    assert analysis.should_handover is True
    assert analysis.should_create_lead is False
    assert "ai_parse_failed" in analysis.risk_flags


def test_claude_low_confidence_forces_handover(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "claude")
    monkeypatch.setenv("AI_CONFIDENCE_THRESHOLD", "0.70")
    get_settings.cache_clear()
    monkeypatch.setattr(
        ai_service,
        "call_claude",
        lambda *args, **kwargs: json.dumps(valid_claude_payload(confidence=0.30, should_handover=False)),
    )
    try:
        analysis, _ = ai_service.analyze_with_ai("I want to apply", source_domain="alte.edu.ge")
    finally:
        monkeypatch.setenv("AI_PROVIDER", "mock")
        get_settings.cache_clear()

    assert analysis.should_handover is True
    assert analysis.should_create_lead is False
    assert "low_confidence" in analysis.risk_flags


def test_chat_missing_knowledge_for_factual_question_uses_safe_handover(client):
    session = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "en"}).json()

    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "message": "What is the exact tuition fee?",
            "source_domain": "alte.edu.ge",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "finance_question"
    assert data["should_handover"] is True
    assert data["answer_source_status"] == "no_approved_source_found"
    assert "exact tuition" not in data["reply"].lower()


def test_chat_message_persists_ai_interaction(client, session_factory):
    session = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "en"}).json()
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "message": "Where is Alte University?",
            "source_domain": "alte.edu.ge",
        },
    )
    assert response.status_code == 200

    async def fetch_interactions():
        async with session_factory() as db:
            return (await db.scalars(select(AIInteraction))).all()

    interactions = asyncio.run(fetch_interactions())
    assert len(interactions) == 1
    assert interactions[0].provider == "mock"
    assert interactions[0].intent == "general_info"


def test_claude_mode_chat_persists_interaction_with_mocked_response(client, session_factory, monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "claude")
    get_settings.cache_clear()
    monkeypatch.setattr(ai_service, "call_claude", lambda *args, **kwargs: json.dumps(valid_claude_payload()))
    session = client.post("/chat/session/start", json={"source_domain": "alte.edu.ge", "language": "en"}).json()

    try:
        response = client.post(
            "/chat/message",
            json={
                "conversation_id": session["conversation_id"],
                "message": "Nino Beridze, +995599000000, nino@example.com wants business admission",
                "source_domain": "alte.edu.ge",
            },
        )
    finally:
        monkeypatch.setenv("AI_PROVIDER", "mock")
        get_settings.cache_clear()

    assert response.status_code == 200

    async def fetch_interactions():
        async with session_factory() as db:
            return (await db.scalars(select(AIInteraction))).all()

    interactions = asyncio.run(fetch_interactions())
    assert len(interactions) == 1
    assert interactions[0].provider == "claude"
    assert interactions[0].raw_response_json["intent"] == "admission_interest"

