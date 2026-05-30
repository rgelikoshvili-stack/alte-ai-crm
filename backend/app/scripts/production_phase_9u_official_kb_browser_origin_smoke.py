from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

import httpx


BASE_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
NETLIFY_ORIGIN = "https://nimble-croissant-2f66e8.netlify.app"
TEST_URL = f"{NETLIFY_ORIGIN}/join.html"

DIRECT_CONTACT_REQUEST_PATTERNS = [
    re.compile(r"(type|enter|send|provide|share).{0,40}(phone|email|name)", re.IGNORECASE),
    re.compile(r"(phone|email|name).{0,40}(type|enter|send|provide|share)", re.IGNORECASE),
    re.compile(r"(მომწერ|გამოგზავნ|მიუთით|შეიყვან|დაწერ).{0,40}(ტელეფონ|ელფოსტ|მეილ|სახელ)", re.IGNORECASE),
    re.compile(r"(ტელეფონ|ელფოსტ|მეილ|სახელ).{0,40}(მომწერ|გამოგზავნ|მიუთით|შეიყვან|დაწერ)", re.IGNORECASE),
]


@dataclass(frozen=True)
class Case:
    case_id: str
    message: str
    expect_source_status: str | None
    must_include: list[str] = field(default_factory=list)
    must_include_any: list[list[str]] = field(default_factory=list)
    must_exclude: list[str] = field(default_factory=list)
    expect_handover: bool | None = None
    require_sources: bool = True


CASES = [
    Case(
        case_id="bachelor_ects_240_not_180",
        message="რამდენი ECTS კრედიტია საჭირო საბაკალავრო პროგრამის დასასრულებლად?",
        expect_source_status="answered_from_approved_source",
        must_include=["240"],
        must_exclude=["180"],
    ),
    Case(
        case_id="master_ects_120",
        message="რამდენი კრედიტია სამაგისტრო პროგრამა ალტე უნივერსიტეტში?",
        expect_source_status="answered_from_approved_source",
        must_include=["120"],
    ),
    Case(
        case_id="teaching_language_georgian_some_english",
        message="რა ენაზე მიმდინარეობს სწავლება ალტე უნივერსიტეტში?",
        expect_source_status="answered_from_approved_source",
        must_include=["ქართულ", "ინგლისურ"],
        must_exclude=["დაგეგმილ", "planned"],
    ),
    Case(
        case_id="status_suspension_max_5_years",
        message="რამდენი წლით შეიძლება სტუდენტის სტატუსის შეჩერება?",
        expect_source_status="answered_from_approved_source",
        must_include=["5"],
    ),
    Case(
        case_id="computer_science_spring_registration",
        message="როდის არის Computer Science-ის სტუდენტებისთვის გაზაფხულის სემესტრის რეგისტრაცია?",
        expect_source_status="answered_from_approved_source",
        must_include=["9", "14", "30"],
        must_include_any=[["მარტ", "March"]],
    ),
    Case(
        case_id="master_admission_documents",
        message="რა საბუთები მჭირდება მაგისტრატურაზე ჩასარიცხად?",
        expect_source_status="answered_from_approved_source",
        must_include_any=[
            ["პირადობის", "ID"],
            ["CV", "რეზიუმ"],
            ["3x4", "3 x 4", "3*4"],
            ["სამხედრო", "military"],
            ["ნოტარ", "notar"],
            ["დიპლომის დანართ", "supplement"],
        ],
    ),
    Case(
        case_id="unsupported_2031_space_campus_scholarship",
        message="2031 წლის კოსმოსური კამპუსის სტიპენდია როგორ მივიღო?",
        expect_source_status="no_approved_source_found",
        require_sources=False,
        must_include_any=[["approved source", "ოფიციალურ", "დამტკიცებულ", "წყარო"]],
        must_exclude=["სტიპენდიას მიიღებთ", "eligible", "deadline"],
    ),
    Case(
        case_id="operator_contact_safe_no_direct_details",
        message="მინდა ოპერატორთან დაკავშირება",
        expect_source_status=None,
        require_sources=False,
        expect_handover=True,
        must_exclude=["მომწერეთ ტელეფონი", "მომწერეთ ელფოსტა", "provide your phone", "provide your email"],
    ),
]


def assert_cors_preflight(client: httpx.Client) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for path in ["/chat/session/start", "/chat/message"]:
        response = client.options(
            f"{BASE_URL}{path}",
            headers={
                "Origin": NETLIFY_ORIGIN,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        checks.append(
            {
                "name": f"preflight_{path}",
                "status_code": response.status_code,
                "allow_origin_exact": response.headers.get("access-control-allow-origin") == NETLIFY_ORIGIN,
                "no_wildcard": response.headers.get("access-control-allow-origin") != "*",
            }
        )
    return checks


def start_session(client: httpx.Client) -> dict[str, Any]:
    response = client.post(
        f"{BASE_URL}/chat/session/start",
        headers={"Origin": NETLIFY_ORIGIN, "Content-Type": "application/json"},
        json={
            "channel": "website_chat",
            "widget_variant": "pro_v2_safe",
            "source_domain": "join.alte.edu.ge",
            "language": "ka",
            "metadata": {"page_url": TEST_URL, "phase": "9u_official_kb_browser_origin_smoke"},
        },
    )
    response.raise_for_status()
    return response.json()


def send_message(client: httpx.Client, session: dict[str, Any], case: Case) -> tuple[dict[str, Any], str | None]:
    response = client.post(
        f"{BASE_URL}/chat/message",
        headers={"Origin": NETLIFY_ORIGIN, "Content-Type": "application/json"},
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": case.message,
            "language": "ka",
            "source_domain": "join.alte.edu.ge",
            "page_url": TEST_URL,
            "widget_variant": "pro_v2_safe",
        },
    )
    allow_origin = response.headers.get("access-control-allow-origin")
    response.raise_for_status()
    return response.json(), allow_origin


def has_direct_contact_request(reply: str) -> bool:
    return any(pattern.search(reply) for pattern in DIRECT_CONTACT_REQUEST_PATTERNS)


def evaluate_case(case: Case, payload: dict[str, Any], allow_origin: str | None) -> dict[str, Any]:
    reply = str(payload.get("reply") or "")
    used_sources = payload.get("used_sources") or []
    checks = {
        "cors_exact_origin": allow_origin == NETLIFY_ORIGIN,
        "source_status": case.expect_source_status is None
        or payload.get("answer_source_status") == case.expect_source_status,
        "sources": not case.require_sources or len(used_sources) > 0,
        "must_include": all(token in reply for token in case.must_include),
        "must_include_any": all(any(token in reply for token in group) for group in case.must_include_any),
        "must_exclude": not any(token in reply for token in case.must_exclude),
        "handover": case.expect_handover is None or payload.get("should_handover") is case.expect_handover,
        "no_direct_contact_request": not has_direct_contact_request(reply),
        "no_created_lead": payload.get("created_lead_id") is None,
        "no_created_task": payload.get("created_task_id") is None,
        "no_lead_creation_flag": payload.get("should_create_lead") is not True,
    }
    passed = all(checks.values())
    return {
        "case_id": case.case_id,
        "passed": passed,
        "checks": checks,
        "answer_source_status": payload.get("answer_source_status"),
        "used_sources_count": len(used_sources),
        "should_handover": payload.get("should_handover"),
        "should_create_lead": payload.get("should_create_lead"),
        "created_lead": payload.get("created_lead_id") is not None,
        "created_task": payload.get("created_task_id") is not None,
        "reply_excerpt": reply[:500],
    }


def main() -> int:
    results: list[dict[str, Any]] = []
    with httpx.Client(timeout=180.0) as client:
        health = client.get(f"{BASE_URL}/health")
        health.raise_for_status()
        cors_checks = assert_cors_preflight(client)
        for case in CASES:
            session = start_session(client)
            payload, allow_origin = send_message(client, session, case)
            results.append(evaluate_case(case, payload, allow_origin))

    failed = [row for row in results if not row["passed"]]
    output = {
        "test_url": TEST_URL,
        "base_url": BASE_URL,
        "origin": NETLIFY_ORIGIN,
        "mode": "browser_origin_http_requests_after_in_app_browser_unavailable",
        "cors_checks": cors_checks,
        "total": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "no_contact_details_sent": True,
        "handover_endpoint_called": False,
        "intentional_lead_task_customer_creation": False,
        "results": results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 1 if failed or not all(all(item[key] for key in ["allow_origin_exact", "no_wildcard"]) for item in cors_checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
