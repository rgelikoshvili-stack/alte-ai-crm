from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx


PRODUCTION_BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"

CONTACT_FLOW_TEST_RUN = False
CONTACT_DETAILS_SENT = False
INTENTIONAL_LEAD_TASK_CUSTOMER_CREATION = False

TEST_CASES: list[dict[str, Any]] = [
    {
        "name": "ka_admissions_programs",
        "source_domain": "alte.edu.ge",
        "language": "ka",
        "selected_department": "admissions",
        "selected_topic": "programs",
        "message": "რა პროგრამები აქვს ალტე უნივერსიტეტს?",
        "expected_departments": {"admissions", "general"},
        "sensitive": False,
    },
    {
        "name": "ka_finance_tuition",
        "source_domain": "alte.edu.ge",
        "language": "ka",
        "selected_department": "finance",
        "selected_topic": "tuition",
        "message": "რა ღირს სწავლა?",
        "expected_departments": {"finance"},
        "sensitive": True,
    },
    {
        "name": "ka_admissions_deadline",
        "source_domain": "alte.edu.ge",
        "language": "ka",
        "selected_department": "admissions",
        "selected_topic": "deadlines",
        "message": "როდის არის მიღების ბოლო ვადა?",
        "expected_departments": {"admissions"},
        "sensitive": True,
    },
    {
        "name": "ka_finance_ambiguous_details",
        "source_domain": "alte.edu.ge",
        "language": "ka",
        "selected_department": "finance",
        "selected_topic": "tuition",
        "message": "მაინტერესებს დეტალები",
        "expected_departments": {"finance"},
        "sensitive": True,
    },
    {
        "name": "ka_medicine_ambiguous_details",
        "source_domain": "alte.edu.ge",
        "language": "ka",
        "selected_department": "medicine",
        "selected_topic": "medicine",
        "message": "დეტალები მაინტერესებს",
        "expected_departments": {"medicine"},
        "sensitive": True,
    },
    {
        "name": "ka_it_support_portal",
        "source_domain": "alte.edu.ge",
        "language": "ka",
        "selected_department": "it_support",
        "selected_topic": "it_support",
        "message": "პორტალში ვერ შევდივარ",
        "expected_departments": {"it_support"},
        "sensitive": False,
    },
    {
        "name": "en_international_documents",
        "source_domain": "join.alte.edu.ge",
        "language": "en",
        "selected_department": "international",
        "selected_topic": "international",
        "message": "What documents do international students need?",
        "expected_departments": {"international"},
        "sensitive": True,
    },
    {
        "name": "en_medicine_india",
        "source_domain": "join.alte.edu.ge",
        "language": "en",
        "selected_department": "medicine",
        "selected_topic": "medicine",
        "message": "I want to apply for medicine from India",
        "expected_departments": {"medicine", "international"},
        "sensitive": True,
    },
    {
        "name": "en_finance_medicine_tuition",
        "source_domain": "join.alte.edu.ge",
        "language": "en",
        "selected_department": "finance",
        "selected_topic": "tuition",
        "message": "How much is medicine tuition?",
        "expected_departments": {"finance", "medicine"},
        "sensitive": True,
    },
    {
        "name": "en_international_visa_relocation",
        "source_domain": "join.alte.edu.ge",
        "language": "en",
        "selected_department": "international",
        "selected_topic": "visa_relocation",
        "message": "Can you help with visa and relocation?",
        "expected_departments": {"international"},
        "sensitive": True,
    },
]


@dataclass
class CaseResult:
    name: str
    passed: bool
    failures: list[str]
    warnings: list[str]
    preview: dict[str, Any]


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
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session.get("session_id"),
            "message": case["message"],
            "source_domain": case["source_domain"],
            "language": case["language"],
            "selected_department": case["selected_department"],
            "selected_topic": case["selected_topic"],
            "widget_variant": "safe_pro_sidebar",
            "page_url": f"https://{case['source_domain']}/test-site",
        },
    )
    response.raise_for_status()
    return response.json()


def normalized_department(payload: dict[str, Any]) -> str:
    values = [
        payload.get("department_key"),
        payload.get("route_department"),
        payload.get("department"),
        payload.get("handover_department"),
    ]
    text = " ".join(str(value).lower() for value in values if value)
    if "international" in text:
        return "international"
    if "medicine" in text or "medical" in text or "md" in text:
        return "medicine"
    if "finance" in text or "tuition" in text or "payment" in text:
        return "finance"
    if "it" in text or "support" in text or "portal" in text:
        return "it_support"
    if "admission" in text:
        return "admissions"
    if "general" in text or "operator" in text:
        return "general"
    return ""


def preview(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "intent": payload.get("intent"),
        "confidence": payload.get("confidence"),
        "should_handover": payload.get("should_handover"),
        "should_create_lead": payload.get("should_create_lead"),
        "route_department": payload.get("route_department"),
        "department_key": payload.get("department_key"),
        "created_customer_id": payload.get("created_customer_id"),
        "created_lead_id": payload.get("created_lead_id"),
        "created_task_id": payload.get("created_task_id"),
        "answer_source_status": payload.get("answer_source_status"),
        "used_sources_count": len(payload.get("used_sources") or []),
    }


def validate_case(case: dict[str, Any], payload: dict[str, Any]) -> CaseResult:
    failures: list[str] = []
    warnings: list[str] = []

    if not str(payload.get("reply") or "").strip():
        failures.append("empty reply")

    created_ids = [
        payload.get("created_customer_id"),
        payload.get("created_lead_id"),
        payload.get("created_task_id"),
    ]
    if any(created_ids):
        failures.append("created CRM record without contact details")

    if payload.get("should_create_lead") is True:
        warnings.append("should_create_lead=true without contact details, but no CRM record was created")

    routed = normalized_department(payload)
    expected = case["expected_departments"]
    if routed and routed not in expected:
        failures.append(f"unexpected department route: {routed}; expected one of {sorted(expected)}")

    if case["sensitive"] and payload.get("should_handover") is not True and not routed:
        failures.append("sensitive case did not handover or route to a department")

    return CaseResult(name=case["name"], passed=not failures, failures=failures, warnings=warnings, preview=preview(payload))


def run_smoke() -> dict[str, Any]:
    results: list[CaseResult] = []
    with httpx.Client(base_url=PRODUCTION_BACKEND_URL, timeout=30.0) as client:
        for case in TEST_CASES:
            session = start_session(client, case)
            payload = send_message(client, session, case)
            results.append(validate_case(case, payload))

    failures = [
        {"name": result.name, "failures": result.failures, "preview": result.preview}
        for result in results
        if not result.passed
    ]
    warnings = [
        {"name": result.name, "warnings": result.warnings, "preview": result.preview}
        for result in results
        if result.warnings
    ]
    return {
        "total_tests": len(results),
        "passed": len(results) - len(failures),
        "failed": len(failures),
        "failures": failures,
        "warnings": warnings,
        "no_contact_details_sent": not CONTACT_DETAILS_SENT,
        "contact_flow_test_run": CONTACT_FLOW_TEST_RUN,
        "intentional_lead_task_customer_creation": INTENTIONAL_LEAD_TASK_CUSTOMER_CREATION,
        "source_domains": ["alte.edu.ge", "join.alte.edu.ge"],
    }


def main() -> None:
    result = run_smoke()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
