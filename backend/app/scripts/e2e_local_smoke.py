from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx

DEFAULT_BASE_URL = "http://127.0.0.1:8000"


@dataclass
class SmokeStep:
    name: str
    passed: bool
    detail: str = ""


def run_smoke(base_url: str = DEFAULT_BASE_URL, timeout: float = 10.0) -> dict[str, Any]:
    steps: list[SmokeStep] = []
    conversation_id: str | None = None
    session_id: str | None = None
    created_lead_id: str | None = None
    created_task_id: str | None = None

    with httpx.Client(base_url=base_url, timeout=timeout) as client:
        health = safe_request(steps, "GET /health", lambda: client.get("/health"))
        if health is None:
            return result_payload(steps, conversation_id, created_lead_id, created_task_id)

        session = safe_request(
            steps,
            "POST /chat/session/start",
            lambda: client.post(
                "/chat/session/start",
                json={"channel": "website_chat", "source_domain": "alte.edu.ge", "language": "ka"},
            ),
        )
        if session:
            payload = session.json()
            conversation_id = payload.get("conversation_id")
            session_id = payload.get("session_id")

        if conversation_id:
            safe_request(
                steps,
                "POST /chat/message admission interest",
                lambda: client.post(
                    "/chat/message",
                    json={
                        "conversation_id": conversation_id,
                        "session_id": session_id,
                        "message": "მაინტერესებს ბიზნესის პროგრამაზე ჩარიცხვა",
                        "source_domain": "alte.edu.ge",
                        "language": "ka",
                    },
                ),
            )
            contact_response = safe_request(
                steps,
                "POST /chat/message contact details",
                lambda: client.post(
                    "/chat/message",
                    json={
                        "conversation_id": conversation_id,
                        "session_id": session_id,
                        "message": "ნინო ბერიძე, +995599000000, nino@example.com",
                        "source_domain": "alte.edu.ge",
                        "language": "ka",
                    },
                ),
            )
            if contact_response:
                contact_payload = contact_response.json()
                created_lead_id = contact_payload.get("created_lead_id")
                created_task_id = contact_payload.get("created_task_id")

        safe_request(steps, "GET /inbox", lambda: client.get("/inbox"))
        safe_request(steps, "GET /dashboard/overview", lambda: client.get("/dashboard/overview"))
        safe_request(steps, "GET /analytics/overview", lambda: client.get("/analytics/overview"))

    return result_payload(steps, conversation_id, created_lead_id, created_task_id)


def safe_request(steps: list[SmokeStep], name: str, call):
    try:
        response = call()
        response.raise_for_status()
    except Exception as exc:  # pragma: no cover - exercised by manual smoke failures
        steps.append(SmokeStep(name=name, passed=False, detail=str(exc)))
        return None
    steps.append(SmokeStep(name=name, passed=True, detail=f"HTTP {response.status_code}"))
    return response


def result_payload(
    steps: list[SmokeStep],
    conversation_id: str | None,
    created_lead_id: str | None,
    created_task_id: str | None,
) -> dict[str, Any]:
    return {
        "passed": all(step.passed for step in steps),
        "conversation_id": conversation_id,
        "created_lead_id": created_lead_id,
        "created_task_id": created_task_id,
        "steps": [step.__dict__ for step in steps],
    }


def main() -> None:
    result = run_smoke()
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
