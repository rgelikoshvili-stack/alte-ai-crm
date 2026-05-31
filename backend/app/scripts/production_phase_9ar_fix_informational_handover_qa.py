from __future__ import annotations

import json
import re
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
REPORT_JSON = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AR_FIX_INFORMATIONAL_HANDOVER_POLLUTION_QA_RESULT.json"


DIRECT_CONTACT_PATTERNS = [
    re.compile(r"(type|enter|send|provide|share|write).{0,60}(phone|email|name|whatsapp)", re.I),
    re.compile(r"(phone|email|name|whatsapp).{0,60}(type|enter|send|provide|share|write)", re.I),
    re.compile(r"(ტელეფონი|ელ\.?ფოსტა|მეილი|სახელი|whatsapp).{0,60}(მომწერ|შეიყვან|გამოგზავნ|მიუთით|დაწერ)", re.I),
    re.compile(r"(მომწერ|შეიყვან|გამოგზავნ|მიუთით|დაწერ).{0,60}(ტელეფონი|ელ\.?ფოსტა|მეილი|სახელი|whatsapp)", re.I),
]


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
) -> tuple[int, dict[str, str], Any]:
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
            return response.status, dict(response.headers), json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"detail": raw[:200]}
        return exc.code, dict(exc.headers), data


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
        return None, "AUTH_UNAVAILABLE_CREDENTIAL_FILE_MISSING"
    email, password = credentials
    status, _, data = request_json("POST", "/auth/login", {"email": email.strip().lower(), "password": password}, origin=None)
    if status != 200:
        return None, f"AUTH_FAILED_HTTP_{status}"
    token = str((data or {}).get("access_token") or "")
    if not token:
        return None, "AUTH_FAILED_NO_TOKEN"
    return token, "AUTH_OK"


def start_session(case_id: str) -> dict[str, Any]:
    status, _, data = request_json(
        "POST",
        "/chat/session/start",
        {
            "channel": "website_chat",
            "source_domain": "join.alte.edu.ge",
            "language": "ka",
            "widget_variant": "pro_v2_safe",
            "metadata": {"page_url": NETLIFY_URL, "phase": "9ar_handover_pollution", "case": case_id},
        },
    )
    if status != 200:
        raise RuntimeError(f"session_start_failed:{status}:{data}")
    return data


def send_chat(session: dict[str, Any], message: str) -> dict[str, Any]:
    status, _, data = request_json(
        "POST",
        "/chat/message",
        {
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": message,
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


def request_wait(session: dict[str, Any], message: str, department: str | None) -> dict[str, Any]:
    status, _, data = request_json(
        "POST",
        f"/chat/handover/{session['conversation_id']}",
        {
            "session_id": session["session_id"],
            "selected_department": department or "human_operator",
            "selected_topic": "phase_9ar_wait_for_operator",
            "source_domain": "join.alte.edu.ge",
            "language": "ka",
            "reason": "wait_for_operator",
            "mode": "waiting_for_operator",
            "message": message,
        },
    )
    if not isinstance(data, dict):
        data = {"raw": data}
    data["http_status"] = status
    return data


def operator_get(token: str | None, path: str) -> tuple[int | None, Any]:
    if not token:
        return None, {"detail": "operator_auth_unavailable"}
    status, _, data = request_json("GET", path, token=token, origin=None)
    return status, data


def no_direct_contact_request(reply: str) -> bool:
    return not any(pattern.search(reply) for pattern in DIRECT_CONTACT_PATTERNS)


def no_crm_created(response: dict[str, Any]) -> bool:
    return not response.get("created_lead_id") and not response.get("created_task_id")


def check(name: str, passed: bool, detail: str = "") -> Check:
    return Check(name=name, passed=passed, detail=detail)


def run_case(case_id: str, message: str) -> tuple[dict[str, Any], dict[str, Any]]:
    session = start_session(case_id)
    response = send_chat(session, message)
    return session, response


def detail_summary(token: str | None, conversation_id: str) -> tuple[list[Check], dict[str, Any]]:
    status, detail = operator_get(token, f"/conversations/{conversation_id}/detail")
    detail_obj = detail if isinstance(detail, dict) else {}
    conversation = detail_obj.get("conversation") if isinstance(detail_obj.get("conversation"), dict) else {}
    return [
        check("operator detail HTTP 200", status == 200, str(status)),
        check("operator detail conversation id", conversation.get("id") == conversation_id, str(conversation.get("id"))),
    ], {
        "http_status": status,
        "conversation_status": conversation.get("status"),
        "human_handover": detail_obj.get("human_handover"),
        "selected_department": detail_obj.get("selected_department"),
        "waiting_status": detail_obj.get("waiting_status"),
        "has_customer": detail_obj.get("customer") is not None,
        "has_lead": detail_obj.get("lead") is not None,
        "message_count": len(detail_obj.get("messages") or []),
    }


def run_qa() -> dict[str, Any]:
    token, auth_status = login_operator()
    checks: list[Check] = []
    cases: list[dict[str, Any]] = []

    bachelor_session, bachelor = run_case("bachelor_ects", "რამდენი ECTS კრედიტია საჭირო საბაკალავრო პროგრამის დასასრულებლად?")
    bachelor_reply = str(bachelor.get("reply") or "")
    bachelor_checks, bachelor_detail = detail_summary(token, bachelor_session["conversation_id"])
    checks.extend(
        [
            check("bachelor HTTP 200", bachelor.get("http_status") == 200, str(bachelor.get("http_status"))),
            check("bachelor source backed", bachelor.get("answer_source_status") == "answered_from_approved_source", str(bachelor.get("answer_source_status"))),
            check("bachelor includes 240", "240" in bachelor_reply, bachelor_reply[:160]),
            check("bachelor should_handover false", bachelor.get("should_handover") is False, str(bachelor.get("should_handover"))),
            check("bachelor department public", bachelor.get("department_key") in {"programs", "admissions"}, str(bachelor.get("department_key"))),
            check("bachelor no CRM response records", no_crm_created(bachelor)),
            check("bachelor no direct contact request", no_direct_contact_request(bachelor_reply), bachelor_reply[:160]),
            *bachelor_checks,
            check("bachelor operator human_handover false", bachelor_detail.get("human_handover") is False, str(bachelor_detail.get("human_handover"))),
            check("bachelor operator department public", bachelor_detail.get("selected_department") in {"Programs", "Admissions", "programs", "admissions"}, str(bachelor_detail.get("selected_department"))),
            check("bachelor no operator customer/lead", not bachelor_detail.get("has_customer") and not bachelor_detail.get("has_lead"), str(bachelor_detail)),
        ]
    )
    cases.append({"name": "bachelor_ects", "chat": sanitize_chat(bachelor), "operator": bachelor_detail})

    master_session, master = run_case("master_ects", "რამდენი კრედიტია სამაგისტრო პროგრამა ალტე უნივერსიტეტში?")
    master_reply = str(master.get("reply") or "")
    checks.extend(
        [
            check("master HTTP 200", master.get("http_status") == 200, str(master.get("http_status"))),
            check("master source backed", master.get("answer_source_status") == "answered_from_approved_source", str(master.get("answer_source_status"))),
            check("master includes 120", "120" in master_reply, master_reply[:160]),
            check("master should_handover false", master.get("should_handover") is False, str(master.get("should_handover"))),
            check("master no CRM response records", no_crm_created(master)),
        ]
    )
    cases.append({"name": "master_ects", "conversation_id": master_session["conversation_id"], "chat": sanitize_chat(master)})

    clarification_session, clarification = run_case("clarification", "სწავლა მაინტერესებს")
    checks.extend(
        [
            check("clarification HTTP 200", clarification.get("http_status") == 200, str(clarification.get("http_status"))),
            check("clarification needed", clarification.get("clarification_needed") is True, str(clarification.get("clarification_needed"))),
            check("clarification should_handover false", clarification.get("should_handover") is False, str(clarification.get("should_handover"))),
            check("clarification no CRM response records", no_crm_created(clarification)),
        ]
    )
    cases.append({"name": "clarification", "conversation_id": clarification_session["conversation_id"], "chat": sanitize_chat(clarification)})

    unsupported_session, unsupported = run_case("unsupported", "2031 წლის კოსმოსური კამპუსის სტიპენდია როგორ მივიღო?")
    unsupported_reply = str(unsupported.get("reply") or "")
    checks.extend(
        [
            check("unsupported HTTP 200", unsupported.get("http_status") == 200, str(unsupported.get("http_status"))),
            check("unsupported no approved source", unsupported.get("answer_source_status") == "no_approved_source_found", str(unsupported.get("answer_source_status"))),
            check("unsupported should_handover true", unsupported.get("should_handover") is True, str(unsupported.get("should_handover"))),
            check("unsupported no hallucination", "კოსმოსური კამპუსის სტიპენდია არის" not in unsupported_reply and "70%" not in unsupported_reply, unsupported_reply[:160]),
            check("unsupported no CRM response records", no_crm_created(unsupported)),
        ]
    )
    cases.append({"name": "unsupported", "conversation_id": unsupported_session["conversation_id"], "chat": sanitize_chat(unsupported)})

    operator_session, operator = run_case("explicit_operator", "მინდა ოპერატორთან დაკავშირება")
    checks.extend(
        [
            check("explicit operator HTTP 200", operator.get("http_status") == 200, str(operator.get("http_status"))),
            check("explicit operator should_handover true", operator.get("should_handover") is True, str(operator.get("should_handover"))),
            check("explicit operator no CRM response records", no_crm_created(operator)),
        ]
    )
    cases.append({"name": "explicit_operator", "conversation_id": operator_session["conversation_id"], "chat": sanitize_chat(operator)})

    wait_response = request_wait(operator_session, "მინდა ოპერატორთან დაკავშირება", operator.get("department_key"))
    time.sleep(0.2)
    wait_checks, wait_detail = detail_summary(token, operator_session["conversation_id"])
    checks.extend(
        [
            check("wait response HTTP 200", wait_response.get("http_status") == 200, str(wait_response.get("http_status"))),
            check("wait status waiting", wait_response.get("status") == "waiting_for_operator", str(wait_response.get("status"))),
            check("wait no task/customer/lead", not wait_response.get("task_id") and not wait_response.get("customer_id") and not wait_response.get("lead_id"), str(wait_response)),
            *wait_checks,
            check("operator detail waiting status", wait_detail.get("waiting_status") == "waiting_for_operator", str(wait_detail.get("waiting_status"))),
            check("operator detail human handover true after wait", wait_detail.get("human_handover") is True, str(wait_detail.get("human_handover"))),
        ]
    )
    cases.append({"name": "wait_for_operator", "wait_response": wait_response, "operator": wait_detail})

    result = {
        "status": "PASSED" if all(item.passed for item in checks) else "FAILED",
        "test_time_utc": datetime.now(timezone.utc).isoformat(),
        "backend_url": BASE_URL,
        "origin": NETLIFY_ORIGIN,
        "operator_api_auth_status": auth_status,
        "operator_api_checked": bool(token),
        "checks_total": len(checks),
        "checks_passed": sum(1 for item in checks if item.passed),
        "checks_failed": sum(1 for item in checks if not item.passed),
        "checks": [item.__dict__ for item in checks],
        "cases": cases,
        "contact_flow_executed": False,
        "real_contact_data_sent": False,
        "lead_task_customer_created_intentionally": False,
        "visitor_side_operator_reply_polling": "NOT_ACTIVE",
        "sanitized": True,
    }
    REPORT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def sanitize_chat(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "http_status": payload.get("http_status"),
        "answer_source_status": payload.get("answer_source_status"),
        "department_key": payload.get("department_key"),
        "route_department": payload.get("route_department"),
        "should_handover": payload.get("should_handover"),
        "clarification_needed": payload.get("clarification_needed"),
        "created_lead_id": payload.get("created_lead_id"),
        "created_task_id": payload.get("created_task_id"),
        "reply_excerpt": str(payload.get("reply") or "")[:180],
    }


def main() -> int:
    result = run_qa()
    return 0 if result["status"] == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(main())
