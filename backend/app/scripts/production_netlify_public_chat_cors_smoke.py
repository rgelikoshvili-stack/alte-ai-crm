from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx


BASE_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
ORIGIN = "https://nimble-croissant-2f66e8.netlify.app"
BLOCKED_ORIGIN = "https://evil.example.com"


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def preflight(client: httpx.Client, path: str, origin: str = ORIGIN) -> httpx.Response:
    return client.options(
        f"{BASE_URL}{path}",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )


def safe_keys(payload: dict[str, Any]) -> list[str]:
    return sorted(str(key) for key in payload.keys())


def exact_origin_check(name: str, response: httpx.Response) -> Check:
    allow_origin = response.headers.get("access-control-allow-origin")
    return Check(
        name,
        allow_origin == ORIGIN,
        f"status={response.status_code}; allow_origin={allow_origin}",
    )


def no_wildcard_check(name: str, response: httpx.Response) -> Check:
    allow_origin = response.headers.get("access-control-allow-origin")
    return Check(name, allow_origin != "*", f"allow_origin={allow_origin}")


def main() -> int:
    checks: list[Check] = []
    session_data: dict[str, Any] | None = None
    message_data: dict[str, Any] | None = None
    handover_preflight_path = "/chat/handover/smoke-preflight-only"

    with httpx.Client(timeout=30.0) as client:
        for path in ["/chat/session/start", "/chat/message", handover_preflight_path]:
            try:
                response = preflight(client, path)
                checks.append(Check(f"preflight_{path}_not_400", response.status_code != 400, f"status={response.status_code}"))
                checks.append(exact_origin_check(f"preflight_{path}_exact_origin", response))
                checks.append(no_wildcard_check(f"preflight_{path}_no_wildcard", response))
            except httpx.RequestError as exc:
                checks.append(Check(f"preflight_{path}_request", False, exc.__class__.__name__))

        try:
            blocked = preflight(client, "/chat/message", BLOCKED_ORIGIN)
            blocked_allow = blocked.headers.get("access-control-allow-origin")
            checks.append(
                Check(
                    "random_origin_blocked",
                    blocked_allow not in {BLOCKED_ORIGIN, "*"},
                    f"status={blocked.status_code}; allow_origin={blocked_allow}",
                )
            )
        except httpx.RequestError as exc:
            checks.append(Check("random_origin_blocked_request", False, exc.__class__.__name__))

        session_payload = {
            "channel": "website_chat",
            "widget_variant": "pro_v2_safe",
            "source_domain": "join.alte.edu.ge",
            "language": "en",
        }
        try:
            session_response = client.post(
                f"{BASE_URL}/chat/session/start",
                headers={"Origin": ORIGIN, "Content-Type": "application/json"},
                json=session_payload,
            )
            checks.append(exact_origin_check("session_start_post_exact_origin", session_response))
            checks.append(no_wildcard_check("session_start_post_no_wildcard", session_response))
            checks.append(Check("session_start_post_200", session_response.status_code == 200, f"status={session_response.status_code}"))
            if session_response.status_code == 200:
                session_data = session_response.json()
                checks.append(Check("session_start_keys", bool(session_data.get("conversation_id") and session_data.get("session_id")), json.dumps(safe_keys(session_data))))
        except httpx.RequestError as exc:
            checks.append(Check("session_start_post_request", False, exc.__class__.__name__))

        if session_data:
            message_payload = {
                "conversation_id": session_data["conversation_id"],
                "session_id": session_data["session_id"],
                "message": "What documents do international students need?",
                "language": "en",
                "source_domain": "join.alte.edu.ge",
                "selected_department": "international",
                "selected_topic": "international_admissions",
                "page_url": f"{ORIGIN}/join.html",
                "widget_variant": "pro_v2_safe",
            }
            try:
                message_response = client.post(
                    f"{BASE_URL}/chat/message",
                    headers={"Origin": ORIGIN, "Content-Type": "application/json"},
                    json=message_payload,
                )
                checks.append(exact_origin_check("message_post_exact_origin", message_response))
                checks.append(no_wildcard_check("message_post_no_wildcard", message_response))
                checks.append(Check("message_post_200", message_response.status_code == 200, f"status={message_response.status_code}"))
                if message_response.status_code == 200:
                    message_data = message_response.json()
                    checks.append(Check("message_reply_present", bool(message_data.get("reply")), json.dumps(safe_keys(message_data))))
                    for key in ["created_customer_id", "created_lead_id", "created_task_id"]:
                        checks.append(Check(f"{key}_absent_or_empty", not message_data.get(key), f"{key}={message_data.get(key)}"))
            except httpx.RequestError as exc:
                checks.append(Check("message_post_request", False, exc.__class__.__name__))
        else:
            checks.append(Check("message_post_skipped_no_session", False, "session_start_failed"))

    print(json.dumps({
        "origin": ORIGIN,
        "base_url": BASE_URL,
        "checks": [check.__dict__ for check in checks],
        "no_wildcard": all(check.passed for check in checks if check.name.endswith("_no_wildcard")),
        "no_contact_details_sent": True,
        "handover_post_called": False,
        "intentional_lead_task_customer_creation": False,
        "message_response_keys": safe_keys(message_data) if message_data else [],
    }, ensure_ascii=False, indent=2))

    failed = [check for check in checks if not check.passed]
    if failed:
        print("production_netlify_public_chat_cors_smoke=FAIL")
        return 1
    print("production_netlify_public_chat_cors_smoke=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
