from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
NETLIFY_ORIGIN = "https://nimble-croissant-2f66e8.netlify.app"
NETLIFY_URL = f"{NETLIFY_ORIGIN}/join.html"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
CREDENTIAL_FILE = PROJECT_ROOT / ".local-secrets" / "temporary_crm_admin_credentials.txt"
REPORT_PATH = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AS_OPERATOR_CRM_ALIGNMENT_QA_RESULT.md"


@dataclass(frozen=True)
class Scenario:
    name: str
    question: str
    expected_department: str | None
    expect_handover: bool
    wait: bool = False
    expect_source_backed: bool | None = None


SCENARIOS = [
    Scenario("official_bachelor_no_handover", "რამდენი ECTS კრედიტია საჭირო საბაკალავრო პროგრამის დასასრულებლად?", "Programs", False, expect_source_backed=True),
    Scenario("explicit_operator_handover", "მინდა ოპერატორთან დაკავშირება", None, True),
    Scenario("finance_handover", "მინდა ფინანსურ დეპარტამენტთან დაკავშირება", "Finance", True),
    Scenario("library_source_backed_no_handover", "ბიბლიოთეკის რესურსები როგორ გამოვიყენო?", "Library", False, expect_source_backed=True),
    Scenario("it_operator_fallback", "emis.alte.edu.ge-ში ვერ შევდივარ", "IT Support", True),
    Scenario("unsupported_operator_fallback", "2031 წლის კოსმოსური კამპუსის სტიპენდია როგორ მივიღო?", None, True),
    Scenario("wait_for_operator", "დაელოდე ოპერატორს", None, True, wait=True),
]


def request_json(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    token: str | None = None,
    origin: str | None = NETLIFY_ORIGIN,
) -> tuple[int, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/json"}
    if origin:
        headers["Origin"] = origin
    if payload is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(f"{BASE_URL}{path}", data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"detail": raw[:240]}
        return exc.code, data


def read_credentials() -> tuple[str, str] | None:
    if not CREDENTIAL_FILE.exists():
        return None
    values: dict[str, str] = {}
    for raw_line in CREDENTIAL_FILE.read_text(encoding="utf-8").splitlines():
        key, sep, value = raw_line.partition("=")
        if sep:
            values[key.strip().lower()] = value.strip()
    email = values.get("email")
    password = values.get("password")
    if not email or not password:
        return None
    return email, password


def login_operator() -> tuple[str | None, str]:
    credentials = read_credentials()
    if credentials is None:
        return None, "AUTH_UNAVAILABLE"
    email, password = credentials
    status, data = request_json("POST", "/auth/login", {"email": email.lower(), "password": password}, origin=None)
    if status != 200:
        return None, f"AUTH_FAILED_HTTP_{status}"
    token = str((data or {}).get("access_token") or "")
    return (token, "AUTH_OK") if token else (None, "AUTH_FAILED_NO_TOKEN")


def start_session(name: str) -> dict[str, Any]:
    status, data = request_json(
        "POST",
        "/chat/session/start",
        {
            "channel": "website_chat",
            "source_domain": "join.alte.edu.ge",
            "language": "ka",
            "widget_variant": "pro_v2_safe",
            "metadata": {"phase": "9as_operator_alignment", "case": name, "page_url": NETLIFY_URL},
        },
    )
    if status != 200:
        raise RuntimeError(f"session_start_failed:{status}:{data}")
    return data


def send_chat(session: dict[str, Any], scenario: Scenario) -> dict[str, Any]:
    status, data = request_json(
        "POST",
        "/chat/message",
        {
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": scenario.question,
            "source_domain": "join.alte.edu.ge",
            "language": "ka",
            "page_url": NETLIFY_URL,
            "widget_variant": "pro_v2_safe",
        },
    )
    if not isinstance(data, dict):
        data = {"raw": data}
    data["http_status"] = status
    return data


def wait_for_operator(session: dict[str, Any], scenario: Scenario, department: str | None) -> dict[str, Any]:
    status, data = request_json(
        "POST",
        f"/chat/handover/{session['conversation_id']}",
        {
            "session_id": session["session_id"],
            "selected_department": department or "human_operator",
            "selected_topic": "phase_9as_wait_for_operator",
            "source_domain": "join.alte.edu.ge",
            "language": "ka",
            "reason": "wait_for_operator",
            "mode": "waiting_for_operator",
            "message": scenario.question,
        },
    )
    if not isinstance(data, dict):
        data = {"raw": data}
    data["http_status"] = status
    return data


def detail(token: str | None, conversation_id: str) -> dict[str, Any]:
    if not token:
        return {"operator_checked": False}
    status, data = request_json("GET", f"/conversations/{conversation_id}/detail", token=token, origin=None)
    detail_obj = data if isinstance(data, dict) else {}
    conversation = detail_obj.get("conversation") if isinstance(detail_obj.get("conversation"), dict) else {}
    messages = detail_obj.get("messages") or []
    message_count = len(messages)
    return {
        "operator_checked": status == 200,
        "http_status": status,
        "conversation_status": conversation.get("status"),
        "human_handover": detail_obj.get("human_handover"),
        "selected_department": detail_obj.get("selected_department"),
        "waiting_status": detail_obj.get("waiting_status"),
        "has_customer": detail_obj.get("customer") is not None,
        "has_lead": detail_obj.get("lead") is not None,
        "message_count": message_count,
        "has_visitor_message": message_count >= 1,
        "has_ai_message": message_count >= 2,
    }


def department_ok(actual: Any, expected: str | None) -> bool:
    if expected is None:
        return True
    return str(actual or "").lower() == expected.lower()


def run_qa() -> dict[str, Any]:
    token, auth_status = login_operator()
    cases: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        session = start_session(scenario.name)
        response = send_chat(session, scenario)
        wait_response = None
        if scenario.wait:
            wait_response = wait_for_operator(session, scenario, response.get("department_key"))
            time.sleep(0.2)
        operator = detail(token, session["conversation_id"])
        checks = {
            "chat_http_200": response.get("http_status") == 200,
            "operator_checked": bool(operator.get("operator_checked")),
            "visitor_message_visible": bool(operator.get("has_visitor_message")) if operator.get("operator_checked") else True,
            "ai_message_visible": bool(operator.get("has_ai_message")) if operator.get("operator_checked") else True,
            "department_visible": department_ok(operator.get("selected_department"), scenario.expected_department) if operator.get("operator_checked") else True,
            "human_handover_expected": operator.get("human_handover") is scenario.expect_handover if operator.get("operator_checked") else response.get("should_handover") is scenario.expect_handover,
            "no_lead_customer": not operator.get("has_customer") and not operator.get("has_lead"),
            "no_response_lead_task": not response.get("created_lead_id") and not response.get("created_task_id"),
            "source_backed_expected": True if scenario.expect_source_backed is None else response.get("answer_source_status") == "answered_from_approved_source",
            "wait_status": True if not scenario.wait else wait_response is not None and wait_response.get("status") == "waiting_for_operator" and operator.get("waiting_status") == "waiting_for_operator",
        }
        cases.append(
            {
                "name": scenario.name,
                "conversation_id": session["conversation_id"],
                "chat": {
                    "answer_source_status": response.get("answer_source_status"),
                    "department_key": response.get("department_key"),
                    "route_department": response.get("route_department"),
                    "should_handover": response.get("should_handover"),
                    "created_lead_id": response.get("created_lead_id"),
                    "created_task_id": response.get("created_task_id"),
                    "reply_excerpt": str(response.get("reply") or "")[:220],
                },
                "operator": operator,
                "checks": checks,
                "passed": all(checks.values()),
            }
        )
    result = {
        "status": "PASSED" if all(case["passed"] for case in cases) else "FAILED",
        "test_time_utc": datetime.now(timezone.utc).isoformat(),
        "backend_url": BASE_URL,
        "netlify_origin": NETLIFY_ORIGIN,
        "operator_auth_status": auth_status,
        "operator_api_checked": bool(token),
        "total": len(cases),
        "passed": sum(1 for case in cases if case["passed"]),
        "failed": sum(1 for case in cases if not case["passed"]),
        "cases": cases,
        "contact_flow_executed": False,
        "real_contact_data_sent": False,
        "lead_task_customer_created": False,
        "public_launch": "NO-GO",
    }
    write_report(result)
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, ensure_ascii=False, indent=2))
    return result


def write_report(result: dict[str, Any]) -> None:
    failures = []
    for case in result["cases"]:
        if case["passed"]:
            continue
        failed = [name for name, passed in case["checks"].items() if not passed]
        failures.append(f"- `{case['name']}`: {', '.join(failed)}")
    if not failures:
        failures.append("- None")
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# Phase 9AS Operator CRM Alignment QA Result",
                "",
                f"PHASE_9AS_OPERATOR_ALIGNMENT_STATUS={result['status']}",
                "",
                f"Test time UTC: {result['test_time_utc']}",
                f"Backend URL: {BASE_URL}",
                f"Netlify Origin: {NETLIFY_ORIGIN}",
                "Operator CRM URL: http://127.0.0.1:5173",
                f"Operator API auth: {result['operator_auth_status']}",
                "",
                "## Summary",
                "",
                f"- Scenarios: {result['total']}",
                f"- Passed: {result['passed']}",
                f"- Failed: {result['failed']}",
                "- Official informational answers excluded from handover queue: VERIFIED when scenario passed",
                "- Explicit operator requests set handover: VERIFIED when scenario passed",
                "- Wait-for-operator sets waiting state: VERIFIED when scenario passed",
                "- Latest visitor message visible in Operator CRM: VERIFIED when API auth is available and scenario passed",
                "- AI answer visible in Operator CRM: VERIFIED when API auth is available and scenario passed",
                "- No lead/customer/task created: VERIFIED when scenario passed",
                "- CONTACT_FLOW_EXECUTED=NO",
                "- REAL_CONTACT_DATA_SENT=NO",
                "- LEAD_TASK_CUSTOMER_CREATED=NO",
                "- Public launch: NO-GO",
                "",
                "## Failures",
                "",
                *failures,
                "",
                "## Known Limitation",
                "",
                "VISITOR_SIDE_OPERATOR_REPLY_POLLING=NOT_ACTIVE",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    result = run_qa()
    return 0 if result["status"] == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(main())
