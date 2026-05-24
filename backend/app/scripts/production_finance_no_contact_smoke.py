from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

import httpx


PRODUCTION_BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"

CONTACT_FLOW_TEST_RUN = False
CONTACT_DETAILS_SENT = False
INTENTIONAL_LEAD_TASK_CREATION = False

PRICE_PATTERNS = [
    re.compile(r"\b\d{3,}(?:[.,]\d+)?\s*(gel|lari|usd|eur|\$|€|₾)\b", re.IGNORECASE),
    re.compile(r"\b(gel|lari|usd|eur)\s*\d{3,}(?:[.,]\d+)?\b", re.IGNORECASE),
    re.compile(r"\b\d{3,}(?:[.,]\d+)?\s*(ლარი|დოლარი|ევრო)\b", re.IGNORECASE),
]

DEADLINE_PATTERNS = [
    re.compile(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b"),
    re.compile(r"\b20\d{2}[-/]\d{1,2}[-/]\d{1,2}\b"),
    re.compile(
        r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b\d{1,2}\s+(იანვარი|თებერვალი|მარტი|აპრილი|მაისი|ივნისი|ივლისი|აგვისტო|სექტემბერი|ოქტომბერი|ნოემბერი|დეკემბერი)",
        re.IGNORECASE,
    ),
]

CONSERVATIVE_TERMS = [
    "official",
    "confirm",
    "consult",
    "admissions",
    "finance",
    "advisor",
    "human",
    "contact",
    "ოფიციალურ",
    "დადასტურ",
    "კონსულტ",
    "დაუკავშირდ",
    "საკონტაქტო",
    "მრჩეველ",
]

TEST_CASES = [
    {"source_domain": "alte.edu.ge", "language": "ka", "message": "რა ღირს სწავლა?", "kind": "tuition"},
    {"source_domain": "alte.edu.ge", "language": "ka", "message": "რა არის სწავლის საფასური?", "kind": "tuition"},
    {"source_domain": "alte.edu.ge", "language": "ka", "message": "სტიპენდია ან გრანტი არის?", "kind": "scholarship"},
    {"source_domain": "alte.edu.ge", "language": "ka", "message": "როდის არის ჩარიცხვის ბოლო ვადა?", "kind": "deadline"},
    {"source_domain": "join.alte.edu.ge", "language": "en", "message": "How much is tuition?", "kind": "tuition"},
    {"source_domain": "join.alte.edu.ge", "language": "en", "message": "How much is medicine tuition?", "kind": "tuition"},
    {"source_domain": "join.alte.edu.ge", "language": "en", "message": "Are scholarships available?", "kind": "scholarship"},
    {"source_domain": "join.alte.edu.ge", "language": "en", "message": "When is the admission deadline?", "kind": "deadline"},
]


@dataclass
class SmokeAssertion:
    name: str
    passed: bool
    detail: str = ""


def start_session(client: httpx.Client, source_domain: str, language: str) -> dict[str, Any]:
    response = client.post(
        "/chat/session/start",
        json={"channel": "website_chat", "source_domain": source_domain, "language": language},
    )
    response.raise_for_status()
    return response.json()


def send_message(client: httpx.Client, session: dict[str, Any], case: dict[str, str]) -> dict[str, Any]:
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": case["message"],
            "source_domain": case["source_domain"],
            "language": case["language"],
        },
    )
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
        "missing_fields": payload.get("missing_fields"),
        "answer_source_status": payload.get("answer_source_status"),
        "used_sources_count": len(payload.get("used_sources") or []),
    }


def has_exact_price(reply: str) -> bool:
    return any(pattern.search(reply) for pattern in PRICE_PATTERNS)


def has_exact_deadline(reply: str) -> bool:
    return any(pattern.search(reply) for pattern in DEADLINE_PATTERNS)


def has_conservative_language(reply: str) -> bool:
    lowered = reply.lower()
    return any(term.lower() in lowered for term in CONSERVATIVE_TERMS)


def assert_case(case: dict[str, str], payload: dict[str, Any]) -> list[SmokeAssertion]:
    preview = response_preview(payload)
    reply = str(payload.get("reply") or "")
    assertions = [
        SmokeAssertion(
            f"{case['kind']} should_create_lead false: {case['message']}",
            preview["should_create_lead"] is not True,
            json.dumps(preview, ensure_ascii=False, sort_keys=True),
        ),
        SmokeAssertion(
            f"{case['kind']} no customer/lead/task IDs: {case['message']}",
            preview["created_customer_id"] is None
            and preview["created_lead_id"] is None
            and preview["created_task_id"] is None,
            json.dumps(preview, ensure_ascii=False, sort_keys=True),
        ),
    ]

    if case["kind"] in {"tuition", "scholarship"}:
        assertions.append(
            SmokeAssertion(
                f"{case['kind']} answer conservative: {case['message']}",
                not has_exact_price(reply) or has_conservative_language(reply),
                f"exact_price={has_exact_price(reply)}, conservative_language={has_conservative_language(reply)}",
            )
        )

    if case["kind"] == "deadline":
        assertions.append(
            SmokeAssertion(
                f"deadline answer conservative: {case['message']}",
                not has_exact_deadline(reply) or has_conservative_language(reply),
                f"exact_deadline={has_exact_deadline(reply)}, conservative_language={has_conservative_language(reply)}",
            )
        )

    return assertions


def run_smoke(base_url: str = PRODUCTION_BACKEND_URL, timeout: float = 45.0) -> dict[str, Any]:
    assertions: list[SmokeAssertion] = []
    case_results: list[dict[str, Any]] = []

    transport = httpx.HTTPTransport(local_address="0.0.0.0")
    with httpx.Client(base_url=base_url, timeout=timeout, transport=transport) as client:
        sessions: dict[tuple[str, str], dict[str, Any]] = {}
        for case in TEST_CASES:
            key = (case["source_domain"], case["language"])
            try:
                session = sessions.setdefault(key, start_session(client, case["source_domain"], case["language"]))
                payload = send_message(client, session, case)
            except Exception as exc:  # pragma: no cover - live smoke failure path
                assertions.append(SmokeAssertion(f"message {case['message']}", False, str(exc)))
                case_results.append({**case, "error": str(exc)})
                continue

            preview = response_preview(payload)
            case_results.append({**case, **preview})
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
    sensitive_answers_conservative = not any(
        "answer conservative" in failure["name"] for failure in failures
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
        "sensitive_answers_conservative": sensitive_answers_conservative,
        "contact_flow_test_run": CONTACT_FLOW_TEST_RUN,
        "contact_details_sent": CONTACT_DETAILS_SENT,
        "intentional_lead_task_creation": INTENTIONAL_LEAD_TASK_CREATION,
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
                "sensitive_answers_conservative": result["sensitive_answers_conservative"],
                "contact_flow_test_run": result["contact_flow_test_run"],
                "contact_details_sent": result["contact_details_sent"],
                "intentional_lead_task_creation": result["intentional_lead_task_creation"],
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
