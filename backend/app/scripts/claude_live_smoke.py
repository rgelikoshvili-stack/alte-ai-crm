from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import get_settings
from app.api.routes_system import is_placeholder_key

DEFAULT_BASE_URL = "http://127.0.0.1:8000"


@dataclass
class SmokeStep:
    name: str
    passed: bool
    detail: str = ""


def validate_claude_live_settings() -> tuple[bool, str]:
    settings = get_settings()
    if settings.AI_PROVIDER.lower().strip() != "claude":
        return False, "Refusing to run: AI_PROVIDER must be claude."
    if is_placeholder_key(settings.ANTHROPIC_API_KEY):
        return False, "Refusing to run: ANTHROPIC_API_KEY is missing or placeholder."
    return True, "Claude live settings accepted."


def run_smoke(base_url: str = DEFAULT_BASE_URL, timeout: float = 20.0) -> dict[str, Any]:
    allowed, reason = validate_claude_live_settings()
    if not allowed:
        return {"passed": False, "reason": reason, "steps": []}

    steps: list[SmokeStep] = []
    conversation_id: str | None = None
    session_id: str | None = None
    created_lead_id: str | None = None
    created_task_id: str | None = None
    message_summaries: list[dict[str, Any]] = []

    with httpx.Client(base_url=base_url, timeout=timeout) as client:
        safe_request(steps, "GET /health", lambda: client.get("/health"))
        safe_request(steps, "GET /diagnostics/local-demo", lambda: client.get("/diagnostics/local-demo"))
        session_response = safe_request(
            steps,
            "POST /chat/session/start",
            lambda: client.post(
                "/chat/session/start",
                json={"channel": "website_chat", "source_domain": "alte.edu.ge", "language": "ka"},
            ),
        )
        if session_response:
            session = session_response.json()
            conversation_id = session.get("conversation_id")
            session_id = session.get("session_id")

        for name, message in [
            ("contact question", "სად მდებარეობს უნივერსიტეტი?"),
            ("admission interest", "მაინტერესებს ბიზნესის პროგრამაზე ჩარიცხვა"),
            ("contact details", "ნინო ბერიძე, +995599000000, nino@example.com"),
        ]:
            if not conversation_id:
                break
            response = safe_request(
                steps,
                f"POST /chat/message {name}",
                lambda msg=message: client.post(
                    "/chat/message",
                    json={
                        "conversation_id": conversation_id,
                        "session_id": session_id,
                        "message": msg,
                        "source_domain": "alte.edu.ge",
                        "language": "ka",
                    },
                ),
            )
            if response:
                payload = response.json()
                message_summaries.append(
                    {
                        "name": name,
                        "intent": payload.get("intent"),
                        "confidence": payload.get("confidence"),
                        "should_handover": payload.get("should_handover"),
                    }
                )
                created_lead_id = payload.get("created_lead_id") or created_lead_id
                created_task_id = payload.get("created_task_id") or created_task_id

        safe_request(steps, "GET /inbox", lambda: client.get("/inbox"))
        safe_request(steps, "GET /dashboard/overview", lambda: client.get("/dashboard/overview"))

    return {
        "passed": all(step.passed for step in steps),
        "conversation_id": conversation_id,
        "created_lead_id": created_lead_id,
        "created_task_id": created_task_id,
        "messages": message_summaries,
        "steps": [step.__dict__ for step in steps],
    }


def safe_request(steps: list[SmokeStep], name: str, call):
    try:
        response = call()
        response.raise_for_status()
    except Exception as exc:  # pragma: no cover - manual smoke failure path
        steps.append(SmokeStep(name=name, passed=False, detail=str(exc)))
        return None
    steps.append(SmokeStep(name=name, passed=True, detail=f"HTTP {response.status_code}"))
    return response


def main() -> None:
    result = run_smoke()
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
