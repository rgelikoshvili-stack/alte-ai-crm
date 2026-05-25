from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

import httpx


PRODUCTION_BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"

CONTACT_FLOW_TEST_RUN = False
CONTACT_DETAILS_SENT = False
INTENTIONAL_LEAD_TASK_CUSTOMER_CREATION = False

EXACT_DEADLINE_PATTERNS = [
    re.compile(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b"),
    re.compile(r"\b20\d{2}[-/]\d{1,2}[-/]\d{1,2}\b"),
    re.compile(
        r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b",
        re.IGNORECASE,
    ),
]

CONSERVATIVE_TERMS = [
    "official",
    "confirm",
    "confirmation",
    "consult",
    "advisor",
    "operator",
    "department",
    "contact",
    "verify",
    "Admissions",
    "Finance",
    "International",
    "Medicine",
    "ოფიციალურ",
    "დადასტურ",
    "კონსულტ",
    "ოპერატორ",
    "დეპარტამენტ",
    "დაკავშირ",
]

DEPARTMENT_TERMS = {
    "admissions": ["admissions", "admission", "registry", "მიღება", "რეგისტრ"],
    "finance": ["finance", "tuition", "fee", "payment", "ფინანს", "საფასურ", "გადახდ"],
    "international": ["international", "foreign", "visa", "relocation", "საერთაშორისო", "უცხოელ", "ვიზა"],
    "medicine": ["medicine", "md", "medical", "dentistry", "მედიც", "სამედიცინო", "სტომატოლოგ"],
    "it_support": ["it", "technical", "portal", "login", "emis", "ტექნიკურ", "პორტალ"],
    "student_services": ["student services", "library", "career", "ombudsman", "სტუდენტ", "ბიბლიოთეკ", "კარიერ"],
}

TEST_CASES = [
    {
        "name": "finance_sidebar_ambiguous",
        "source_domain": "alte.edu.ge",
        "language": "ka",
        "selected_department": "finance",
        "selected_topic": "tuition",
        "message": "მაინტერესებს დეტალები",
        "expected_departments": {"finance"},
        "require_handover_or_route": True,
        "sensitive": True,
    },
    {
        "name": "tuition_direct",
        "source_domain": "alte.edu.ge",
        "language": "ka",
        "selected_department": "finance",
        "selected_topic": "tuition",
        "message": "რა ღირს სწავლა?",
        "expected_departments": {"finance"},
        "require_handover_or_route": True,
        "sensitive": True,
    },
    {
        "name": "deadline_admissions",
        "source_domain": "alte.edu.ge",
        "language": "ka",
        "selected_department": "admissions",
        "selected_topic": "deadlines",
        "message": "როდის არის მიღების ბოლო ვადა?",
        "expected_departments": {"admissions"},
        "deadline": True,
        "sensitive": True,
    },
    {
        "name": "international_documents",
        "source_domain": "join.alte.edu.ge",
        "language": "en",
        "selected_department": "international",
        "selected_topic": "international",
        "message": "What documents do international students need?",
        "expected_departments": {"international"},
        "sensitive": True,
    },
    {
        "name": "medicine_from_india",
        "source_domain": "join.alte.edu.ge",
        "language": "en",
        "selected_department": "medicine",
        "selected_topic": "medicine",
        "message": "I want to apply for medicine from India",
        "expected_departments": {"medicine", "international"},
        "sensitive": True,
    },
    {
        "name": "it_support",
        "source_domain": "alte.edu.ge",
        "language": "en",
        "selected_department": "it_support",
        "selected_topic": "it_support",
        "message": "I have a portal login problem",
        "expected_departments": {"it_support"},
    },
    {
        "name": "student_services",
        "source_domain": "alte.edu.ge",
        "language": "ka",
        "selected_department": "student_services",
        "selected_topic": "student_services",
        "message": "ბიბლიოთეკის შესახებ ინფორმაცია მინდა",
        "expected_departments": {"student_services"},
    },
    {
        "name": "human_operator_finance",
        "source_domain": "alte.edu.ge",
        "language": "ka",
        "selected_department": "finance",
        "selected_topic": "human_operator",
        "message": "მინდა ოპერატორთან საუბარი",
        "expected_departments": {"finance"},
        "expect_handover": True,
    },
    {
        "name": "medicine_sidebar_ambiguous",
        "source_domain": "alte.edu.ge",
        "language": "ka",
        "selected_department": "medicine",
        "selected_topic": "medicine",
        "message": "დეტალები მაინტერესებს",
        "expected_departments": {"medicine"},
        "require_handover_or_route": True,
    },
]


@dataclass
class SmokeAssertion:
    name: str
    passed: bool
    detail: str = ""


def start_session(client: httpx.Client, case: dict[str, Any]) -> dict[str, Any]:
    response = client.post(
        "/chat/session/start",
        json={
            "channel": "website_chat",
            "source_domain": case["source_domain"],
            "language": case["language"],
            "widget_variant": "safe_pro_sidebar",
        },
    )
    response.raise_for_status()
    return response.json()


def send_message(client: httpx.Client, session: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "conversation_id": session["conversation_id"],
        "session_id": session.get("session_id"),
        "message": case["message"],
        "source_domain": case["source_domain"],
        "language": case["language"],
        "selected_department": case["selected_department"],
        "selected_topic": case["selected_topic"],
        "widget_variant": "safe_pro_sidebar",
        "page_url": f"https://{case['source_domain']}/",
    }
    response = client.post("/chat/message", json=payload)
    response.raise_for_status()
    return response.json()


def response_preview(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "intent": payload.get("intent"),
        "confidence": payload.get("confidence"),
        "should_create_lead": payload.get("should_create_lead"),
        "should_handover": payload.get("should_handover"),
        "created_customer_id": payload.get("created_customer_id"),
        "created_lead_id": payload.get("created_lead_id"),
        "created_task_id": payload.get("created_task_id"),
        "route_department": payload.get("route_department"),
        "department_key": payload.get("department_key"),
        "handover_reason": payload.get("handover_reason"),
        "answer_source_status": payload.get("answer_source_status"),
        "missing_fields": payload.get("missing_fields"),
        "used_sources_count": len(payload.get("used_sources") or []),
    }


def normalized_department(payload: dict[str, Any], reply: str) -> str | None:
    key = payload.get("department_key")
    if isinstance(key, str) and key:
        return key
    route = str(payload.get("route_department") or "").lower()
    for department, terms in DEPARTMENT_TERMS.items():
        if department in route or any(term.lower() in route for term in terms):
            return department
    lowered_reply = reply.lower()
    for department, terms in DEPARTMENT_TERMS.items():
        if any(term.lower() in lowered_reply for term in terms):
            return department
    return None


def has_conservative_language(reply: str) -> bool:
    lowered = reply.lower()
    return any(term.lower() in lowered for term in CONSERVATIVE_TERMS)


def has_exact_deadline(reply: str) -> bool:
    return any(pattern.search(reply) for pattern in EXACT_DEADLINE_PATTERNS)


def assert_case(case: dict[str, Any], payload: dict[str, Any]) -> list[SmokeAssertion]:
    preview = response_preview(payload)
    reply = str(payload.get("reply") or "")
    routed_department = normalized_department(payload, reply)
    expected = case["expected_departments"]
    should_handover = payload.get("should_handover") is True

    assertions = [
        SmokeAssertion(
            f"{case['name']} route department",
            routed_department in expected,
            json.dumps({**preview, "normalized_department": routed_department}, ensure_ascii=False, sort_keys=True),
        ),
        SmokeAssertion(
            f"{case['name']} no contact lead/customer/task",
            preview["should_create_lead"] is not True
            and preview["created_customer_id"] is None
            and preview["created_lead_id"] is None
            and preview["created_task_id"] is None,
            json.dumps(preview, ensure_ascii=False, sort_keys=True),
        ),
    ]

    if case.get("expect_handover"):
        assertions.append(
            SmokeAssertion(
                f"{case['name']} handover requested",
                should_handover,
                json.dumps(preview, ensure_ascii=False, sort_keys=True),
            )
        )
    if case.get("require_handover_or_route"):
        assertions.append(
            SmokeAssertion(
                f"{case['name']} context preserved or handover",
                should_handover or routed_department in expected,
                json.dumps({**preview, "normalized_department": routed_department}, ensure_ascii=False, sort_keys=True),
            )
        )
    if case.get("deadline"):
        assertions.append(
            SmokeAssertion(
                f"{case['name']} no invented exact deadline",
                not has_exact_deadline(reply) or has_conservative_language(reply),
                f"exact_deadline={has_exact_deadline(reply)}, conservative={has_conservative_language(reply)}",
            )
        )
    if case.get("sensitive"):
        assertions.append(
            SmokeAssertion(
                f"{case['name']} sensitive answer conservative or routed",
                has_conservative_language(reply) or should_handover or routed_department in expected,
                f"conservative={has_conservative_language(reply)}, handover={should_handover}, route={routed_department}",
            )
        )

    return assertions


def run_smoke(base_url: str = PRODUCTION_BACKEND_URL, timeout: float = 60.0) -> dict[str, Any]:
    assertions: list[SmokeAssertion] = []
    case_results: list[dict[str, Any]] = []
    with httpx.Client(base_url=base_url, timeout=timeout) as client:
        for case in TEST_CASES:
            try:
                session = start_session(client, case)
                payload = send_message(client, session, case)
            except Exception as exc:  # pragma: no cover - live smoke failure path
                assertions.append(SmokeAssertion(f"{case['name']} request", False, str(exc)))
                case_results.append({**case, "error": str(exc)})
                continue

            preview = response_preview(payload)
            reply = str(payload.get("reply") or "")
            route = normalized_department(payload, reply)
            case_results.append(
                {
                    "name": case["name"],
                    "expected_departments": sorted(case["expected_departments"]),
                    "normalized_department": route,
                    **preview,
                }
            )
            assertions.extend(assert_case(case, payload))

    failures = [assertion.__dict__ for assertion in assertions if not assertion.passed]
    no_contact_guard_confirmed = all(
        result.get("should_create_lead") is not True
        and result.get("created_customer_id") is None
        and result.get("created_lead_id") is None
        and result.get("created_task_id") is None
        for result in case_results
        if "error" not in result
    )
    department_context_confirmed = all(
        result.get("normalized_department") in set(result.get("expected_departments") or [])
        for result in case_results
        if "error" not in result
    )
    handover_routing_confirmed = any(
        result.get("should_handover") is True and result.get("normalized_department") in set(result.get("expected_departments") or [])
        for result in case_results
        if "error" not in result
    )
    return {
        "base_url": base_url,
        "total_tests": len(assertions),
        "passed": len(assertions) - len(failures),
        "failed": len(failures),
        "status": "PASSED" if not failures else "FAILED_NEEDS_REVIEW",
        "failures": failures,
        "case_results": case_results,
        "no_contact_guard_confirmed": no_contact_guard_confirmed,
        "department_context_confirmed": department_context_confirmed,
        "handover_routing_confirmed": handover_routing_confirmed,
        "contact_flow_test_run": CONTACT_FLOW_TEST_RUN,
        "contact_details_sent": CONTACT_DETAILS_SENT,
        "intentional_lead_task_customer_creation": INTENTIONAL_LEAD_TASK_CUSTOMER_CREATION,
    }


def main() -> None:
    result = run_smoke()
    print(
        json.dumps(
            {
                "status": result["status"],
                "total_tests": result["total_tests"],
                "passed": result["passed"],
                "failed": result["failed"],
                "no_contact_guard_confirmed": result["no_contact_guard_confirmed"],
                "department_context_confirmed": result["department_context_confirmed"],
                "handover_routing_confirmed": result["handover_routing_confirmed"],
                "contact_flow_test_run": result["contact_flow_test_run"],
                "contact_details_sent": result["contact_details_sent"],
                "intentional_lead_task_customer_creation": result["intentional_lead_task_customer_creation"],
                "failures": result["failures"],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    if result["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
