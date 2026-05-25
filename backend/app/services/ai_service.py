from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import ValidationError

from app.core.ai_client import get_ai_client
from app.core.config import get_settings
from app.engines.mock_ai_analyzer import analyze_message
from app.schemas.chat import AIAnalysisResult
from app.services.ai_prompts import ALTE_CLAUDE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def analyze_with_ai(
    message: str,
    *,
    source_domain: str | None = None,
    language_hint: str | None = None,
    conversation_history: list[dict[str, str]] | None = None,
    knowledge_context: list[dict[str, Any]] | None = None,
) -> tuple[AIAnalysisResult, dict[str, Any]]:
    settings = get_settings()
    provider = settings.AI_PROVIDER.lower().strip()
    if provider != "claude":
        analysis = analyze_message(message, source_domain)
        return analysis, {"provider": "mock", "model": "mock", "raw_response": None, "fallback": False}

    try:
        raw_text = call_claude(
            message,
            source_domain=source_domain,
            language_hint=language_hint,
            conversation_history=conversation_history or [],
            knowledge_context=knowledge_context or [],
        )
        raw_json = parse_json_object(raw_text)
        analysis = AIAnalysisResult.model_validate(raw_json)
        if analysis.confidence < settings.AI_CONFIDENCE_THRESHOLD:
            analysis.should_handover = True
            analysis.should_create_lead = False
            if "low_confidence" not in analysis.risk_flags:
                analysis.risk_flags.append("low_confidence")
        if knowledge_context and not analysis.used_sources:
            analysis.used_sources = [str(item.get("title") or item.get("id")) for item in knowledge_context]
        return analysis, {
            "provider": "claude",
            "model": settings.AI_MODEL,
            "raw_response": raw_json,
            "fallback": False,
        }
    except (ValueError, ValidationError, TypeError, RuntimeError) as exc:
        logger.warning("AI provider response fallback: %s", type(exc).__name__)
        analysis = fallback_analysis(message, source_domain, "ai_provider_error", language_hint=language_hint)
        if "ai_parse_failed" not in analysis.risk_flags:
            analysis.risk_flags.append("ai_parse_failed")
        return analysis, {
            "provider": "claude",
            "model": settings.AI_MODEL,
            "raw_response": None,
            "fallback": True,
            "error_type": type(exc).__name__,
        }
    except Exception as exc:  # Provider SDK/network/timeouts must never surface to chat users.
        logger.warning("AI provider unavailable fallback: %s", type(exc).__name__)
        return fallback_analysis(message, source_domain, "ai_provider_error", language_hint=language_hint), {
            "provider": "claude",
            "model": settings.AI_MODEL,
            "raw_response": None,
            "fallback": True,
            "error_type": type(exc).__name__,
        }


def call_claude(
    message: str,
    *,
    source_domain: str | None,
    language_hint: str | None,
    conversation_history: list[dict[str, str]],
    knowledge_context: list[dict[str, Any]],
) -> str:
    settings = get_settings()
    handle = get_ai_client()
    prompt_payload = {
        "message": message,
        "source_domain": source_domain,
        "language_hint": language_hint,
        "conversation_history": conversation_history,
        "knowledge_context": knowledge_context,
        "schema": {
            "reply": "str",
            "language": "ka|en|unknown",
            "intent": "str",
            "confidence": "float 0..1",
            "should_create_lead": "bool",
            "should_handover": "bool",
            "department": "str|null",
            "priority": "low|normal|high|urgent",
            "missing_fields": ["str"],
            "extracted_contact": {
                "first_name": "str|null",
                "last_name": "str|null",
                "phone": "str|null",
                "email": "str|null",
                "country": "str|null",
                "city": "str|null",
            },
            "interest_area": "str|null",
            "program": "str|null",
            "program_language": "str|null",
            "source_domain": "str|null",
            "conversation_summary": "str|null",
            "used_sources": ["str"],
            "risk_flags": ["str"],
        },
    }
    response = handle.client.messages.create(
        model=settings.AI_MODEL,
        max_tokens=settings.AI_MAX_TOKENS,
        system=ALTE_CLAUDE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(prompt_payload, ensure_ascii=False)}],
        timeout=settings.AI_TIMEOUT_SECONDS,
    )
    return extract_response_text(response)


def extract_response_text(response: Any) -> str:
    content = getattr(response, "content", None)
    if isinstance(content, list) and content:
        first = content[0]
        text = getattr(first, "text", None)
        if text is not None:
            return str(text)
        if isinstance(first, dict) and first.get("text") is not None:
            return str(first["text"])
    if isinstance(response, str):
        return response
    raise ValueError("Claude response did not include text content")


def parse_json_object(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end < start:
            raise ValueError("No JSON object found in Claude response")
        parsed = json.loads(text[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("Claude response JSON is not an object")
    return parsed


def fallback_analysis(
    message: str,
    source_domain: str | None,
    flag: str,
    *,
    language_hint: str | None = None,
) -> AIAnalysisResult:
    language = language_hint if language_hint in {"ka", "en"} else ("ka" if any("\u10a0" <= char <= "\u10ff" for char in message) else "en")
    reply = (
        "ამ მომენტში AI სერვისთან კავშირი შეფერხებულია. ამ საკითხზე დაგაკავშირებთ შესაბამის დეპარტამენტთან."
        if language == "ka"
        else "The AI service is temporarily unavailable. I can connect you with the relevant department."
    )
    return AIAnalysisResult(
        reply=reply,
        language=language,
        intent="human_request",
        confidence=0.0,
        should_create_lead=False,
        should_handover=True,
        department=infer_fallback_department(message),
        priority="normal",
        missing_fields=[],
        source_domain=source_domain,
        conversation_summary=f"Safe AI fallback for message: {message[:180]}",
        used_sources=[],
        risk_flags=[flag],
    )


def infer_fallback_department(message: str) -> str:
    lowered = message.lower()
    if any(token in lowered for token in ("finance", "tuition", "fee", "payment", "საფას", "გადახდ")):
        return "Finance"
    if any(token in lowered for token in ("international", "visa", "join", "ინდო", "უცხო")):
        return "International Admissions"
    if any(token in lowered for token in ("student", "schedule", "სტუდენტ", "ცხრილ")):
        return "Student Services"
    return "Admissions"
