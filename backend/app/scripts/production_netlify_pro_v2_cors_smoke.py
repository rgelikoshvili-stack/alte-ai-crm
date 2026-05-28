from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx


PRODUCTION_BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
NETLIFY_ORIGIN = "https://nimble-croissant-2f66e8.netlify.app"
RANDOM_ORIGIN = "https://evil.example.com"


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def cors_preflight(client: httpx.Client, path: str, origin: str) -> httpx.Response:
    return client.options(
        path,
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )


def assert_allowed_preflight(client: httpx.Client, path: str) -> list[Check]:
    response = cors_preflight(client, path, NETLIFY_ORIGIN)
    allow_origin = response.headers.get("access-control-allow-origin")
    allow_methods = response.headers.get("access-control-allow-methods", "")
    allow_headers = response.headers.get("access-control-allow-headers", "")
    return [
        Check(f"preflight_{path}_not_400", response.status_code < 400, f"status={response.status_code}"),
        Check(f"preflight_{path}_exact_origin", allow_origin == NETLIFY_ORIGIN, f"allow_origin={allow_origin}"),
        Check(f"preflight_{path}_no_wildcard", allow_origin != "*", f"allow_origin={allow_origin}"),
        Check(f"preflight_{path}_allows_post", "POST" in allow_methods.upper(), f"methods={allow_methods}"),
        Check(f"preflight_{path}_allows_content_type", "content-type" in allow_headers.lower(), f"headers={allow_headers}"),
    ]


def assert_random_origin_blocked(client: httpx.Client, path: str) -> Check:
    response = cors_preflight(client, path, RANDOM_ORIGIN)
    allow_origin = response.headers.get("access-control-allow-origin")
    return Check(f"preflight_{path}_random_origin_blocked", allow_origin != RANDOM_ORIGIN and allow_origin != "*", f"allow_origin={allow_origin}")


def post_json(client: httpx.Client, path: str, payload: dict[str, Any]) -> httpx.Response:
    return client.post(
        path,
        json=payload,
        headers={"Origin": NETLIFY_ORIGIN, "Content-Type": "application/json"},
    )


def run_smoke() -> dict[str, Any]:
    checks: list[Check] = []
    with httpx.Client(base_url=PRODUCTION_BACKEND_URL, timeout=60.0) as client:
        for path in ["/chat/session/start", "/chat/message"]:
            checks.extend(assert_allowed_preflight(client, path))
            checks.append(assert_random_origin_blocked(client, path))

        session_payload = {
            "channel": "website_chat",
            "source_domain": "join.alte.edu.ge",
            "language": "en",
            "widget_variant": "pro_v2_safe",
            "metadata": {"page_url": f"{NETLIFY_ORIGIN}/join.html", "mode": "test_site"},
        }
        session_response = post_json(client, "/chat/session/start", session_payload)
        checks.append(
            Check(
                "post_session_start_success",
                session_response.status_code == 200,
                f"status={session_response.status_code}; body={session_response.text[:160]}",
            )
        )
        checks.append(
            Check(
                "post_session_start_cors_origin",
                session_response.headers.get("access-control-allow-origin") == NETLIFY_ORIGIN,
                f"allow_origin={session_response.headers.get('access-control-allow-origin')}",
            )
        )

        session_data: dict[str, Any] = {}
        if session_response.status_code == 200:
            session_data = session_response.json()

        if session_data.get("conversation_id"):
            message_response = post_json(
                client,
                "/chat/message",
                {
                    "conversation_id": session_data["conversation_id"],
                    "session_id": session_data.get("session_id"),
                    "message": "What programs are available?",
                    "source_domain": "join.alte.edu.ge",
                    "language": "en",
                    "selected_department": "programs",
                    "selected_topic": "programs",
                    "widget_variant": "pro_v2_safe",
                    "page_url": f"{NETLIFY_ORIGIN}/join.html",
                },
            )
            checks.append(
                Check(
                    "post_chat_message_reachable",
                    message_response.status_code == 200,
                    f"status={message_response.status_code}; body={message_response.text[:160]}",
                )
            )
            checks.append(
                Check(
                    "post_chat_message_cors_origin",
                    message_response.headers.get("access-control-allow-origin") == NETLIFY_ORIGIN,
                    f"allow_origin={message_response.headers.get('access-control-allow-origin')}",
                )
            )
        else:
            checks.append(Check("post_chat_message_reachable", False, "blocked because session start did not succeed"))
            checks.append(Check("post_chat_message_cors_origin", False, "blocked because session start did not succeed"))

    failures = [check.__dict__ for check in checks if not check.passed]
    return {
        "status": "PASS" if not failures else "FAILED_NEEDS_REVIEW",
        "total_tests": len(checks),
        "passed": len(checks) - len(failures),
        "failed": len(failures),
        "failures": failures,
        "origin": NETLIFY_ORIGIN,
        "checked_endpoints": ["/chat/session/start", "/chat/message"],
        "forbidden_endpoint_used": False,
        "no_contact_details_sent": True,
        "contact_flow_test_run": False,
        "intentional_lead_task_customer_creation": False,
    }


def main() -> None:
    result = run_smoke()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
