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
REPORT_PATH = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AT_KNOWLEDGE_FIXES_QA_RESULT.md"
CREDENTIAL_FILE = PROJECT_ROOT / ".local-secrets" / "temporary_crm_admin_credentials.txt"


@dataclass(frozen=True)
class Scenario:
    name: str
    question: str
    expected_source_status: str | None
    expected_department: str | None
    must_include: tuple[str, ...] = ()
    must_not_include: tuple[str, ...] = ()
    expected_handover: bool | None = None
    check_operator: bool = False


SCENARIOS = [
    Scenario("cs_calendar", "როდის იწყება კომპიუტერული მეცნიერების გაზაფხულის სემესტრის რეგისტრაცია?", "answered_from_approved_source", "academic_calendar", ("9", "14", "30"), ("AI service is temporarily unavailable",), False),
    Scenario("master_documents", "მაგისტრატურაზე ჩასაბარებლად რა დოკუმენტებია საჭირო?", "answered_from_approved_source", "admissions", ("CV",), ("AI service is temporarily unavailable",), False),
    Scenario("bachelor_ects", "რამდენი ECTS კრედიტია საჭირო საბაკალავრო პროგრამის დასასრულებლად?", "answered_from_approved_source", "programs", ("240",), ("180",), False, True),
    Scenario("fake_scholarship", "2031 წლის კოსმოსური კამპუსის სტიპენდია როგორ მივიღო?", "no_approved_source_found", None, ("დამტკიცებულ",), ("70%",), True),
    Scenario("fake_tuition", "ზუსტად რა ღირს 2031 წლის AI კოსმოსური პროგრამის სწავლა?", "no_approved_source_found", "finance", ("დამტკიცებულ",), ("ლარი",), True),
    Scenario("it_emis", "emis.alte.edu.ge-ში ვერ შევდივარ", "no_approved_source_found", "it_support", (), (), True, True),
    Scenario("career_empty_source", "კარიერისა და სტაჟირების შესაძლებლობებზე ვის მივმართო?", "no_approved_source_found", "career", (), (), True),
]


def request_json(method: str, path: str, payload: dict[str, Any] | None = None, token: str | None = None, origin: str | None = NETLIFY_ORIGIN) -> tuple[int, Any]:
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
            data = {"detail": raw[:200]}
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
            "metadata": {"phase": "9at_knowledge_fixes", "case": name, "page_url": NETLIFY_URL},
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


def operator_detail(token: str | None, conversation_id: str) -> dict[str, Any]:
    if not token:
        return {"operator_checked": False}
    status, data = request_json("GET", f"/conversations/{conversation_id}/detail", token=token, origin=None)
    detail = data if isinstance(data, dict) else {}
    return {
        "operator_checked": status == 200,
        "http_status": status,
        "human_handover": detail.get("human_handover"),
        "selected_department": detail.get("selected_department"),
        "has_customer": detail.get("customer") is not None,
        "has_lead": detail.get("lead") is not None,
    }


def department_ok(actual: str | None, expected: str | None) -> bool:
    if expected is None:
        return True
    aliases = {
        "academic_calendar": {"academic_calendar", "study_process", "Academic Calendar", "Study Process"},
        "admissions": {"admissions", "Admissions"},
        "programs": {"programs", "Programs"},
        "finance": {"finance", "Finance"},
        "it_support": {"it_support", "IT Support"},
        "career": {"career", "Career", "student_services", "Student Services"},
    }
    return actual in aliases.get(expected, {expected})


def run_qa() -> dict[str, Any]:
    token, auth_status = login_operator()
    cases = []
    for scenario in SCENARIOS:
        session = start_session(scenario.name)
        response = send_chat(session, scenario)
        time.sleep(0.1)
        detail = operator_detail(token, session["conversation_id"]) if scenario.check_operator else {"operator_checked": False}
        reply = str(response.get("reply") or "")
        checks = {
            "chat_http_200": response.get("http_status") == 200,
            "source_status": scenario.expected_source_status is None or response.get("answer_source_status") == scenario.expected_source_status,
            "department": department_ok(response.get("department_key"), scenario.expected_department),
            "handover": scenario.expected_handover is None or response.get("should_handover") is scenario.expected_handover,
            "must_include": all(token in reply for token in scenario.must_include),
            "must_not_include": all(token not in reply for token in scenario.must_not_include),
            "no_lead_task_response": not response.get("created_lead_id") and not response.get("created_task_id"),
            "operator_handover": True if not scenario.check_operator else detail.get("operator_checked") and detail.get("human_handover") is scenario.expected_handover,
            "operator_no_customer_lead": True if not scenario.check_operator else not detail.get("has_customer") and not detail.get("has_lead"),
        }
        cases.append(
            {
                "name": scenario.name,
                "passed": all(checks.values()),
                "checks": checks,
                "chat": {
                    "answer_source_status": response.get("answer_source_status"),
                    "department_key": response.get("department_key"),
                    "route_department": response.get("route_department"),
                    "should_handover": response.get("should_handover"),
                    "created_lead_id": response.get("created_lead_id"),
                    "created_task_id": response.get("created_task_id"),
                    "reply_excerpt": reply[:220],
                },
                "operator": detail,
            }
        )
    result = {
        "status": "PASSED" if all(case["passed"] for case in cases) else "FAILED",
        "test_time_utc": datetime.now(timezone.utc).isoformat(),
        "backend_url": BASE_URL,
        "operator_auth_status": auth_status,
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
                "# Phase 9AT Knowledge Fixes Production QA Result",
                "",
                f"PHASE_9AT_PRODUCTION_QA_STATUS={result['status']}",
                "",
                f"Test time UTC: {result['test_time_utc']}",
                f"Backend URL: {BASE_URL}",
                f"Operator API auth: {result['operator_auth_status']}",
                "",
                "## Summary",
                "",
                f"- Total: {result['total']}",
                f"- Passed: {result['passed']}",
                f"- Failed: {result['failed']}",
                "- CONTACT_FLOW_EXECUTED=NO",
                "- REAL_CONTACT_DATA_SENT=NO",
                "- LEAD_TASK_CUSTOMER_CREATED=NO",
                "- Public launch: NO-GO",
                "",
                "## Failures",
                "",
                *failures,
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
