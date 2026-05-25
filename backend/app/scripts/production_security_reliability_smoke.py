from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx


PRODUCTION_BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"

CONTACT_FLOW_TEST_RUN = False
CONTACT_DETAILS_SENT = False
INTENTIONAL_LEAD_TASK_CUSTOMER_CREATION = False
CHAT_SAFE_FALLBACK_READY_LOCAL_ONLY = True


@dataclass
class SmokeCheck:
    name: str
    passed: bool
    detail: str = ""


def get_status(client: httpx.Client, path: str) -> int:
    return client.get(path).status_code


def start_session(client: httpx.Client, *, source_domain: str = "alte.edu.ge", language: str = "ka") -> dict[str, Any]:
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
    message: str,
    source_domain: str = "alte.edu.ge",
    language: str = "ka",
    selected_department: str | None = None,
    selected_topic: str | None = None,
) -> dict[str, Any]:
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": message,
            "source_domain": source_domain,
            "language": language,
            "selected_department": selected_department,
            "selected_topic": selected_topic,
            "widget_variant": "phase_9k_redeploy_safe_smoke",
        },
    )
    response.raise_for_status()
    return response.json()


def request_handover(client: httpx.Client, session: dict[str, Any]) -> dict[str, Any]:
    response = client.post(
        f"/chat/handover/{session['conversation_id']}",
        json={"session_id": session["session_id"]},
    )
    response.raise_for_status()
    return response.json()


def no_crm_creation(payload: dict[str, Any]) -> bool:
    return not payload.get("created_lead_id") and not payload.get("created_task_id") and payload.get("should_create_lead") is False


def check_endpoints(client: httpx.Client) -> list[SmokeCheck]:
    checks: list[SmokeCheck] = []
    health = get_status(client, "/health")
    version = get_status(client, "/version")
    diagnostics = client.get("/diagnostics/ai")
    dashboard = get_status(client, "/dashboard/overview")
    checks.append(SmokeCheck("health_200", health == 200, str(health)))
    checks.append(SmokeCheck("version_200", version == 200, str(version)))
    checks.append(SmokeCheck("diagnostics_ai_200", diagnostics.status_code == 200, str(diagnostics.status_code)))
    if diagnostics.status_code == 200:
        data = diagnostics.json()
        checks.append(SmokeCheck("claude_enabled", data.get("claude_enabled") is True, safe_preview(data)))
        checks.append(SmokeCheck("diagnostics_no_warnings", data.get("warnings") == [], safe_preview(data)))
    checks.append(SmokeCheck("dashboard_without_auth_blocked", dashboard in {401, 403}, str(dashboard)))
    return checks


def check_chat_general(client: httpx.Client) -> list[SmokeCheck]:
    session = start_session(client)
    data = send_message(
        client,
        session,
        message="რა პროგრამები აქვს ალტე უნივერსიტეტს?",
        selected_department="admissions",
        selected_topic="programs",
    )
    reply = str(data.get("reply") or "")
    return [
        SmokeCheck("chat_general_200_safe_reply", bool(reply), response_preview(data)),
        SmokeCheck("chat_general_no_crm_creation", no_crm_creation(data), response_preview(data)),
    ]


def check_department_routing(client: httpx.Client) -> list[SmokeCheck]:
    checks: list[SmokeCheck] = []
    cases = [
        {
            "name": "finance_no_contact",
            "selected_department": "finance",
            "selected_topic": "tuition",
            "message": "მაინტერესებს დეტალები",
            "expected": {"finance", "Finance"},
        },
        {
            "name": "medicine_no_contact",
            "selected_department": "medicine",
            "selected_topic": "medicine",
            "message": "დეტალები მაინტერესებს",
            "expected": {"medicine", "Medicine / MD", "International Admissions"},
        },
    ]
    for case in cases:
        session = start_session(client)
        data = send_message(
            client,
            session,
            message=case["message"],
            selected_department=case["selected_department"],
            selected_topic=case["selected_topic"],
        )
        route = data.get("department_key") or data.get("route_department") or ""
        checks.append(
            SmokeCheck(
                f"{case['name']}_routes_or_handovers",
                data.get("should_handover") is True or str(route) in case["expected"],
                response_preview(data),
            )
        )
        checks.append(SmokeCheck(f"{case['name']}_no_crm_creation", no_crm_creation(data), response_preview(data)))
    return checks


def check_handover_spam_guard(client: httpx.Client) -> list[SmokeCheck]:
    session = start_session(client)
    first = request_handover(client, session)
    second = request_handover(client, session)
    safe_statuses = {first.get("status"), second.get("status")}
    no_tasks = not first.get("task_id") and not second.get("task_id")
    return [
        SmokeCheck("handover_first_no_500", bool(first.get("status")), safe_preview(first)),
        SmokeCheck("handover_second_no_500", bool(second.get("status")), safe_preview(second)),
        SmokeCheck("handover_no_contact_no_task", no_tasks, safe_preview({"first": first, "second": second})),
        SmokeCheck(
            "handover_idempotent_or_contact_required",
            safe_statuses.issubset({"contact_required", "handover_already_requested", "handover_requested"}),
            safe_preview({"statuses": sorted(str(item) for item in safe_statuses)}),
        ),
    ]


def response_preview(payload: dict[str, Any]) -> str:
    return safe_preview(
        {
            "intent": payload.get("intent"),
            "confidence": payload.get("confidence"),
            "should_create_lead": payload.get("should_create_lead"),
            "should_handover": payload.get("should_handover"),
            "created_lead_id": bool(payload.get("created_lead_id")),
            "created_task_id": bool(payload.get("created_task_id")),
            "route_department": payload.get("route_department"),
            "department_key": payload.get("department_key"),
            "answer_source_status": payload.get("answer_source_status"),
        }
    )


def safe_preview(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def run_smoke() -> dict[str, Any]:
    checks: list[SmokeCheck] = []
    with httpx.Client(base_url=PRODUCTION_BACKEND_URL, timeout=60.0) as client:
        checks.extend(check_endpoints(client))
        checks.extend(check_chat_general(client))
        checks.extend(check_department_routing(client))
        checks.extend(check_handover_spam_guard(client))

    failures = [check for check in checks if not check.passed]
    return {
        "total_tests": len(checks),
        "passed": len(checks) - len(failures),
        "failed": len(failures),
        "failures": [{"name": check.name, "detail": check.detail} for check in failures],
        "auth_guard_confirmed": any(check.name == "dashboard_without_auth_blocked" and check.passed for check in checks),
        "chat_safe_fallback_ready_local_only": CHAT_SAFE_FALLBACK_READY_LOCAL_ONLY,
        "handover_spam_guard_confirmed": all(
            check.passed for check in checks if check.name.startswith("handover_")
        ),
        "no_contact_details_sent": not CONTACT_DETAILS_SENT,
        "contact_flow_test_run": CONTACT_FLOW_TEST_RUN,
        "intentional_lead_task_customer_creation": INTENTIONAL_LEAD_TASK_CUSTOMER_CREATION,
    }


def main() -> None:
    result = run_smoke()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if result["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
