from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any

import httpx


DEFAULT_BASE_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"


@dataclass
class SmokeStep:
    name: str
    passed: bool
    detail: str = ""


def safe_request(steps: list[SmokeStep], name: str, call):
    try:
        response = call()
        response.raise_for_status()
    except Exception as exc:  # pragma: no cover - manual smoke failure path
        steps.append(SmokeStep(name=name, passed=False, detail=str(exc)))
        return None
    steps.append(SmokeStep(name=name, passed=True, detail=f"HTTP {response.status_code}"))
    return response


def preview_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "intent": payload.get("intent"),
        "confidence": payload.get("confidence"),
        "should_handover": payload.get("should_handover"),
        "should_create_lead": payload.get("should_create_lead"),
        "created_lead_id": payload.get("created_lead_id"),
        "created_task_id": payload.get("created_task_id"),
        "missing_fields": payload.get("missing_fields"),
    }


def start_session(client: httpx.Client, source_domain: str, language: str) -> dict[str, Any]:
    response = client.post(
        "/chat/session/start",
        json={"channel": "website_chat", "source_domain": source_domain, "language": language},
    )
    response.raise_for_status()
    return response.json()


def send_message(
    client: httpx.Client,
    session: dict[str, Any],
    *,
    source_domain: str,
    language: str,
    message: str,
) -> dict[str, Any]:
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session.get("conversation_id"),
            "session_id": session.get("session_id"),
            "message": message,
            "source_domain": source_domain,
            "language": language,
        },
    )
    response.raise_for_status()
    return response.json()


def run_smoke(
    *,
    base_url: str = DEFAULT_BASE_URL,
    include_contact_flow: bool = False,
    timeout: float = 30.0,
) -> dict[str, Any]:
    steps: list[SmokeStep] = []
    message_results: list[dict[str, Any]] = []

    with httpx.Client(base_url=base_url, timeout=timeout) as client:
        safe_request(steps, "GET /health", lambda: client.get("/health"))
        safe_request(steps, "GET /version", lambda: client.get("/version"))
        safe_request(steps, "GET /diagnostics/ai", lambda: client.get("/diagnostics/ai"))

        for case in [
            {
                "source_domain": "alte.edu.ge",
                "language": "ka",
                "messages": ["გამარჯობა", "რა ღირს სწავლა?"],
            },
            {
                "source_domain": "join.alte.edu.ge",
                "language": "en",
                "messages": ["I want to apply for medicine from India"],
            },
        ]:
            session_response = safe_request(
                steps,
                f"POST /chat/session/start {case['source_domain']} {case['language']}",
                lambda c=case: client.post(
                    "/chat/session/start",
                    json={
                        "channel": "website_chat",
                        "source_domain": c["source_domain"],
                        "language": c["language"],
                    },
                ),
            )
            if not session_response:
                continue
            session = session_response.json()
            for message in case["messages"]:
                response = safe_request(
                    steps,
                    f"POST /chat/message {case['source_domain']} {message}",
                    lambda c=case, msg=message, sess=session: client.post(
                        "/chat/message",
                        json={
                            "conversation_id": sess.get("conversation_id"),
                            "session_id": sess.get("session_id"),
                            "message": msg,
                            "source_domain": c["source_domain"],
                            "language": c["language"],
                        },
                    ),
                )
                if response:
                    payload = response.json()
                    preview = preview_payload(payload)
                    message_results.append(
                        {
                            "source_domain": case["source_domain"],
                            "language": case["language"],
                            "message": message,
                            **preview,
                        }
                    )
                    if not include_contact_flow and (
                        preview["created_lead_id"] is not None or preview["created_task_id"] is not None
                    ):
                        steps.append(
                            SmokeStep(
                                name=f"Assert no lead/task side effect for {case['source_domain']} {message}",
                                passed=False,
                                detail="Default safe smoke must not create leads or tasks.",
                            )
                        )
                    if (
                        not include_contact_flow
                        and preview["intent"] in {"admission_interest", "international_admission", "medicine_admission"}
                        and preview["should_create_lead"] is True
                    ):
                        steps.append(
                            SmokeStep(
                                name=f"Assert no-contact lead guard for {case['source_domain']} {message}",
                                passed=False,
                                detail="No-contact admissions smoke should ask for contact before lead creation.",
                            )
                        )

        if include_contact_flow:
            session = start_session(client, "alte.edu.ge", "ka")
            payload = send_message(
                client,
                session,
                source_domain="alte.edu.ge",
                language="ka",
                message="ტესტ მომხმარებელი, +995599000000, test@example.com",
            )
            steps.append(SmokeStep("POST /chat/message contact flow", True, "HTTP 200"))
            message_results.append(
                {
                    "source_domain": "alte.edu.ge",
                    "language": "ka",
                    "message": "controlled contact flow",
                    **preview_payload(payload),
                }
            )

    return {
        "passed": all(step.passed for step in steps),
        "base_url": base_url,
        "include_contact_flow": include_contact_flow,
        "steps": [step.__dict__ for step in steps],
        "messages": message_results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run standalone chatbot backend/API smoke without browser CORS.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--include-contact-flow", action="store_true")
    args = parser.parse_args()

    result = run_smoke(base_url=args.base_url, include_contact_flow=args.include_contact_flow)
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
