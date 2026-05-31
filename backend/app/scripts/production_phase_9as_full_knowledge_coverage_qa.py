from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
NETLIFY_ORIGIN = "https://nimble-croissant-2f66e8.netlify.app"
NETLIFY_URL = f"{NETLIFY_ORIGIN}/join.html"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATASET_PATH = PROJECT_ROOT / "backend" / "app" / "data" / "evaluation" / "phase_9as_full_knowledge_qa.json"
REPORT_PATH = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AS_FULL_KNOWLEDGE_COVERAGE_QA_RESULT.md"
CREDENTIAL_FILE = PROJECT_ROOT / ".local-secrets" / "temporary_crm_admin_credentials.txt"

MOJIBAKE_MARKERS = ["áƒ", "â†", "â€¢", "�"]
DIRECT_CONTACT_PATTERNS = [
    re.compile(r"(type|enter|send|provide|share|write).{0,70}(phone|email|name|whatsapp)", re.I),
    re.compile(r"(phone|email|name|whatsapp).{0,70}(type|enter|send|provide|share|write)", re.I),
    re.compile(r"(ტელეფონი|ელ\.?ფოსტა|მეილი|სახელი).{0,70}(მომწერ|შეიყვან|გამოგზავნ|მიუთით|დაწერ)", re.I),
    re.compile(r"(მომწერ|შეიყვან|გამოგზავნ|მიუთით|დაწერ).{0,70}(ტელეფონი|ელ\.?ფოსტა|მეილი|სახელი)", re.I),
]

DEPARTMENT_ALIASES = {
    None: {None, ""},
    "programs": {"programs", "Programs"},
    "admissions": {"admissions", "Admissions"},
    "academic_calendar": {"academic_calendar", "Academic Calendar", "study_process", "Study Process"},
    "study_process": {"study_process", "Study Process", "student_services", "Student Services"},
    "finance": {"finance", "Finance", "Finance / Tuition"},
    "library": {"library", "Library"},
    "it_support": {"it_support", "IT Support", "it", "IT"},
    "medicine": {"medicine", "Medicine / MD", "medicine_md"},
    "international": {"international", "International Admissions", "international_admissions"},
    "career": {"career", "Career", "student_services", "Student Services"},
    "human_operator": {"general", "General / Operator", "human_operator", "Human Operator", "admissions", "Admissions"},
}


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str = ""


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


def start_session(item: dict[str, Any]) -> dict[str, Any]:
    status, data = request_json(
        "POST",
        "/chat/session/start",
        {
            "channel": "website_chat",
            "source_domain": "join.alte.edu.ge",
            "language": item.get("language") or "ka",
            "widget_variant": "pro_v2_safe",
            "metadata": {"phase": "9as_full_knowledge", "case": item["id"], "page_url": NETLIFY_URL},
        },
    )
    if status != 200:
        raise RuntimeError(f"session_start_failed:{status}:{data}")
    return data


def send_chat(session: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    status, data = request_json(
        "POST",
        "/chat/message",
        {
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": item["question"],
            "source_domain": "join.alte.edu.ge",
            "language": item.get("language") or "ka",
            "page_url": NETLIFY_URL,
            "widget_variant": "pro_v2_safe",
        },
    )
    if not isinstance(data, dict):
        data = {"raw": data}
    data["http_status"] = status
    return data


def request_wait(session: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    status, data = request_json(
        "POST",
        f"/chat/handover/{session['conversation_id']}",
        {
            "session_id": session["session_id"],
            "selected_department": item.get("expected_department") or "human_operator",
            "selected_topic": "phase_9as_wait_for_operator",
            "source_domain": "join.alte.edu.ge",
            "language": item.get("language") or "ka",
            "reason": "wait_for_operator",
            "mode": "waiting_for_operator",
            "message": item["question"],
        },
    )
    if not isinstance(data, dict):
        data = {"raw": data}
    data["http_status"] = status
    return data


def operator_detail(token: str | None, conversation_id: str) -> dict[str, Any]:
    if not token:
        return {"operator_checked": False}
    status, data = request_json("GET", f"/conversations/{conversation_id}/detail", token=token, origin=None)
    detail = data if isinstance(data, dict) else {}
    conversation = detail.get("conversation") if isinstance(detail.get("conversation"), dict) else {}
    return {
        "operator_checked": status == 200,
        "http_status": status,
        "conversation_status": conversation.get("status"),
        "human_handover": detail.get("human_handover"),
        "selected_department": detail.get("selected_department"),
        "waiting_status": detail.get("waiting_status"),
        "has_customer": detail.get("customer") is not None,
        "has_lead": detail.get("lead") is not None,
        "message_count": len(detail.get("messages") or []),
    }


def contains_no_mojibake(text: str) -> bool:
    return not any(marker in text for marker in MOJIBAKE_MARKERS)


def no_direct_contact_request(text: str) -> bool:
    return not any(pattern.search(text) for pattern in DIRECT_CONTACT_PATTERNS)


def no_crm_created(response: dict[str, Any], detail: dict[str, Any]) -> bool:
    response_clean = not response.get("created_lead_id") and not response.get("created_task_id")
    detail_clean = not detail.get("has_customer") and not detail.get("has_lead")
    return response_clean and detail_clean


def reply_body_for_token_checks(reply: str) -> str:
    if "\n\nწყარო:" in reply:
        return reply.split("\n\nწყარო:", 1)[0]
    for marker in ["\n\nSource:", "\n\náƒ¬áƒ§áƒáƒ áƒ:"]:
        if marker in reply:
            return reply.split(marker, 1)[0]
    return reply


def department_matches(actual_key: str | None, actual_label: str | None, expected: str | None) -> bool:
    if expected is None:
        return True
    allowed = DEPARTMENT_ALIASES.get(expected, {expected})
    return actual_key in allowed or actual_label in allowed


def expected_status_checks(item: dict[str, Any], response: dict[str, Any]) -> list[Check]:
    status = item["expected_status"]
    source_status = response.get("answer_source_status")
    if status == "ANSWERABLE":
        return [
            Check("source-backed answer", source_status == "answered_from_approved_source", str(source_status)),
            Check("no clarification for answerable", response.get("clarification_needed") is not True, str(response.get("clarification_needed"))),
        ]
    if status == "CLARIFICATION_REQUIRED":
        return [Check("clarification required", response.get("clarification_needed") is True, str(response.get("clarification_needed")))]
    if status == "UNSUPPORTED_OPERATOR":
        return [
            Check("unsupported fallback or handover", source_status == "no_approved_source_found" or response.get("should_handover") is True, str(source_status)),
            Check("handover offered", response.get("should_handover") is True, str(response.get("should_handover"))),
        ]
    if status == "ROUTE_ONLY":
        return [Check("route response HTTP OK", response.get("http_status") == 200, str(response.get("http_status")))]
    return [Check("known expected status", False, status)]


def validate_item(item: dict[str, Any], response: dict[str, Any], detail: dict[str, Any], wait_response: dict[str, Any] | None) -> list[Check]:
    reply = str(response.get("reply") or "")
    token_reply = reply_body_for_token_checks(reply)
    checks = [
        Check("chat HTTP 200", response.get("http_status") == 200, str(response.get("http_status"))),
        Check("no mojibake", contains_no_mojibake(reply), reply[:180]),
        Check("no direct contact request", no_direct_contact_request(reply), reply[:180]),
        Check(
            "department route",
            department_matches(response.get("department_key"), response.get("route_department"), item.get("expected_department")),
            f"{response.get('department_key')} / {response.get('route_department')}",
        ),
        Check(
            "source group",
            item.get("expected_source_group") is None or response.get("source_group") == item.get("expected_source_group"),
            str(response.get("source_group")),
        ),
        Check(
            "should_handover expected",
            item.get("should_handover_expected") is None or response.get("should_handover") is item.get("should_handover_expected"),
            str(response.get("should_handover")),
        ),
        Check(
            "no lead/task/customer",
            no_crm_created(response, detail),
            f"lead={response.get('created_lead_id')} task={response.get('created_task_id')} customer={detail.get('has_customer')} lead_detail={detail.get('has_lead')}",
        ),
    ]
    checks.extend(expected_status_checks(item, response))
    for token in item.get("expected_must_include") or []:
        checks.append(Check(f"must include {token}", str(token).lower() in token_reply.lower(), token_reply[:220]))
    for token in item.get("expected_must_not_include") or []:
        checks.append(Check(f"must not include {token}", str(token).lower() not in token_reply.lower(), token_reply[:220]))
    if detail.get("operator_checked") and item.get("human_handover_expected") is not None:
        checks.append(
            Check(
                "operator human_handover expected",
                detail.get("human_handover") is item.get("human_handover_expected"),
                str(detail.get("human_handover")),
            )
        )
    if wait_response is not None:
        checks.extend(
            [
                Check("wait HTTP 200", wait_response.get("http_status") == 200, str(wait_response.get("http_status"))),
                Check("wait status", wait_response.get("status") == "waiting_for_operator", str(wait_response.get("status"))),
                Check("wait created no CRM records", not wait_response.get("task_id") and not wait_response.get("customer_id") and not wait_response.get("lead_id"), str(wait_response)),
            ]
        )
    return checks


def sanitize_case(item: dict[str, Any], response: dict[str, Any], detail: dict[str, Any], checks: list[Check]) -> dict[str, Any]:
    return {
        "id": item["id"],
        "category": item["category"],
        "expected_status": item["expected_status"],
        "http_status": response.get("http_status"),
        "answer_source_status": response.get("answer_source_status"),
        "source_group": response.get("source_group"),
        "department_key": response.get("department_key"),
        "route_department": response.get("route_department"),
        "should_handover": response.get("should_handover"),
        "clarification_needed": response.get("clarification_needed"),
        "operator_checked": detail.get("operator_checked"),
        "operator_human_handover": detail.get("human_handover"),
        "operator_selected_department": detail.get("selected_department"),
        "passed": all(check.passed for check in checks),
        "failed_checks": [check.__dict__ for check in checks if not check.passed],
        "reply_excerpt": str(response.get("reply") or "")[:240],
    }


def write_report(result: dict[str, Any]) -> None:
    category_lines = []
    for category, stats in sorted(result["categories"].items()):
        category_lines.append(f"| {category} | {stats['total']} | {stats['passed']} | {stats['failed']} |")
    failure_lines = []
    for case in result["cases"]:
        if case["passed"]:
            continue
        details = "; ".join(f"{check['name']}={check['detail']}" for check in case["failed_checks"][:5])
        failure_lines.append(f"- `{case['id']}` ({case['category']}): {details}")
    if not failure_lines:
        failure_lines.append("- None")
    status = "PASSED" if result["failed"] == 0 else "FAILED"
    recommendation = (
        "No critical knowledge/routing failures were found in this run."
        if status == "PASSED"
        else "Review failed cases before approval; keep public launch blocked."
    )
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# Phase 9AS Full Knowledge Coverage QA Result",
                "",
                f"PHASE_9AS_FULL_KNOWLEDGE_QA_STATUS={status}",
                "",
                f"Test time UTC: {result['test_time_utc']}",
                f"Backend URL: {BASE_URL}",
                f"Netlify Origin: {NETLIFY_ORIGIN}",
                f"Dataset: `{DATASET_PATH.relative_to(PROJECT_ROOT)}`",
                f"Operator API auth: {result['operator_auth_status']}",
                "",
                "## Summary",
                "",
                f"- Total questions: {result['total']}",
                f"- Passed: {result['passed']}",
                f"- Failed: {result['failed']}",
                f"- Skipped: {result['skipped']}",
                "- Contact flow executed: NO",
                "- Real contact data sent: NO",
                "- Lead/task/customer created: NO",
                "- Public launch: NO-GO",
                "",
                "## Per-Category Results",
                "",
                "| Category | Total | Passed | Failed |",
                "| --- | ---: | ---: | ---: |",
                *category_lines,
                "",
                "## Failures",
                "",
                *failure_lines,
                "",
                "## Checks Covered",
                "",
                "- Source-backed correctness",
                "- Expected source group",
                "- Department/routing",
                "- Clarification behavior",
                "- Unsupported no-hallucination fallback",
                "- Handover expectation",
                "- Operator `human_handover` state when API auth is available",
                "- No lead/task/customer creation",
                "- No direct phone/email/name request in chat answer",
                "- No Georgian mojibake",
                "",
                "## Final Recommendation",
                "",
                recommendation,
                "",
            ]
        ),
        encoding="utf-8",
    )


def run_qa() -> dict[str, Any]:
    token, auth_status = login_operator()
    items = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    cases: list[dict[str, Any]] = []
    categories: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "passed": 0, "failed": 0})
    for item in items:
        session = start_session(item)
        response = send_chat(session, item)
        wait_response = None
        if item.get("action") == "wait_for_operator":
            wait_response = request_wait(session, item)
            time.sleep(0.2)
        detail = operator_detail(token, session["conversation_id"])
        checks = validate_item(item, response, detail, wait_response)
        case = sanitize_case(item, response, detail, checks)
        cases.append(case)
        stats = categories[item["category"]]
        stats["total"] += 1
        stats["passed" if case["passed"] else "failed"] += 1
    result = {
        "status": "PASSED" if all(case["passed"] for case in cases) else "FAILED",
        "test_time_utc": datetime.now(timezone.utc).isoformat(),
        "total": len(cases),
        "passed": sum(1 for case in cases if case["passed"]),
        "failed": sum(1 for case in cases if not case["passed"]),
        "skipped": 0,
        "categories": dict(categories),
        "operator_auth_status": auth_status,
        "operator_api_checked": bool(token),
        "cases": cases,
        "contact_flow_executed": False,
        "real_contact_data_sent": False,
        "lead_task_customer_created": False,
        "public_launch": "NO-GO",
    }
    write_report(result)
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, ensure_ascii=False, indent=2))
    return result


def main() -> int:
    result = run_qa()
    return 0 if result["status"] == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(main())
