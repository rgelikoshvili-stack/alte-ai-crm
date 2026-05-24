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
    re.compile(r"\b\d{3,}(?:[.,]\d+)?\s*(gel|lari|₾|usd|eur|\$|€)\b", re.IGNORECASE),
    re.compile(r"\b(gel|lari|usd|eur)\s*\d{3,}(?:[.,]\d+)?\b", re.IGNORECASE),
    re.compile(r"\b\d{3,}(?:[.,]\d+)?\s*(ლარი|დოლარი|ევრო)\b", re.IGNORECASE),
]

DEADLINE_PATTERNS = [
    re.compile(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b"),
    re.compile(r"\b20\d{2}[-/]\d{1,2}[-/]\d{1,2}\b"),
    re.compile(r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b", re.IGNORECASE),
    re.compile(r"\b\d{1,2}\s+(იანვარი|თებერვალი|მარტი|აპრილი|მაისი|ივნისი|ივლისი|აგვისტო|სექტემბერი|ოქტომბერი|ნოემბერი|დეკემბერი)", re.IGNORECASE),
]

CONSULTATION_TERMS = [
    "official",
    "confirm",
    "consult",
    "admissions",
    "finance",
    "registry",
    "advisor",
    "human",
    "contact",
    "ოფიციალურ",
    "დადასტურ",
    "კონსულტ",
    "Admissions",
    "Finance",
    "Academic Registry",
    "დაუკავშირდ",
    "საკონტაქტო",
]

TEST_CASES = [
    {"source_domain": "alte.edu.ge", "language": "ka", "message": "რა პროგრამები აქვს ალტე უნივერსიტეტს?", "kind": "general"},
    {"source_domain": "alte.edu.ge", "language": "ka", "message": "როგორ ხდება ჩარიცხვა?", "kind": "admissions"},
    {"source_domain": "alte.edu.ge", "language": "ka", "message": "რა საბუთებია საჭირო ჩარიცხვისთვის?", "kind": "documents"},
    {"source_domain": "alte.edu.ge", "language": "ka", "message": "რა ღირს სწავლა?", "kind": "tuition"},
    {"source_domain": "alte.edu.ge", "language": "ka", "message": "როდის არის მიღების ბოლო ვადა?", "kind": "deadline"},
    {"source_domain": "alte.edu.ge", "language": "ka", "message": "სად მდებარეობს ალტე უნივერსიტეტი?", "kind": "contact"},
    {"source_domain": "alte.edu.ge", "language": "ka", "message": "მინდა ადამიანთან საუბარი", "kind": "human"},
    {"source_domain": "join.alte.edu.ge", "language": "en", "message": "I want to apply for medicine from India", "kind": "medicine"},
    {"source_domain": "join.alte.edu.ge", "language": "en", "message": "What documents do international students need?", "kind": "international_documents"},
    {"source_domain": "join.alte.edu.ge", "language": "en", "message": "How much is tuition for medicine?", "kind": "tuition"},
    {"source_domain": "join.alte.edu.ge", "language": "en", "message": "When is the admission deadline?", "kind": "deadline"},
    {"source_domain": "join.alte.edu.ge", "language": "en", "message": "Can you help me with visa and relocation?", "kind": "visa_relocation"},
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


def check_endpoint(client: httpx.Client, path: str) -> dict[str, Any]:
    response = client.get(path)
    response.raise_for_status()
    return {"status_code": response.status_code, "json": response.json()}


def has_exact_price(reply: str) -> bool:
    return any(pattern.search(reply) for pattern in PRICE_PATTERNS)


def has_exact_deadline(reply: str) -> bool:
    return any(pattern.search(reply) for pattern in DEADLINE_PATTERNS)


def has_consultation_language(reply: str) -> bool:
    lowered = reply.lower()
    return any(term.lower() in lowered for term in CONSULTATION_TERMS)


def response_preview(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "intent": payload.get("intent"),
        "confidence": payload.get("confidence"),
        "should_create_lead": payload.get("should_create_lead"),
        "should_handover": payload.get("should_handover"),
        "created_lead_id": payload.get("created_lead_id"),
        "created_task_id": payload.get("created_task_id"),
        "missing_fields": payload.get("missing_fields"),
        "answer_source_status": payload.get("answer_source_status"),
        "used_sources_count": len(payload.get("used_sources") or []),
    }


def assert_case(case: dict[str, str], payload: dict[str, Any]) -> list[SmokeAssertion]:
    assertions: list[SmokeAssertion] = []
    reply = str(payload.get("reply") or "")
    preview = response_preview(payload)

    no_lead_task = preview["created_lead_id"] is None and preview["created_task_id"] is None
    no_create_flag = preview["should_create_lead"] is not True
    assertions.append(
        SmokeAssertion(
            f"no lead/task side effect: {case['kind']}",
            no_lead_task and no_create_flag,
            json.dumps(preview, ensure_ascii=False, sort_keys=True),
        )
    )

    if case["kind"] == "tuition":
        conservative = not has_exact_price(reply) and has_consultation_language(reply)
        assertions.append(
            SmokeAssertion(
                "tuition answer conservative",
                conservative,
                f"exact_price={has_exact_price(reply)}, consultation_language={has_consultation_language(reply)}",
            )
        )

    if case["kind"] == "deadline":
        conservative = not has_exact_deadline(reply) and has_consultation_language(reply)
        assertions.append(
            SmokeAssertion(
                "deadline answer conservative",
                conservative,
                f"exact_deadline={has_exact_deadline(reply)}, consultation_language={has_consultation_language(reply)}",
            )
        )

    if case["kind"] in {"documents", "international_documents", "medicine", "visa_relocation"}:
        careful = has_consultation_language(reply) or bool(preview["should_handover"]) or "phone_or_email" in (
            preview["missing_fields"] or []
        )
        assertions.append(
            SmokeAssertion(
                f"{case['kind']} routes carefully",
                careful,
                f"handover={preview['should_handover']}, missing_fields={preview['missing_fields']}",
            )
        )

    return assertions


def run_smoke(base_url: str = PRODUCTION_BACKEND_URL, timeout: float = 45.0) -> dict[str, Any]:
    endpoint_results: dict[str, Any] = {}
    assertions: list[SmokeAssertion] = []
    case_results: list[dict[str, Any]] = []

    with httpx.Client(base_url=base_url, timeout=timeout) as client:
        for path in ["/health", "/version", "/diagnostics/ai"]:
            try:
                endpoint_results[path] = check_endpoint(client, path)
                assertions.append(SmokeAssertion(f"GET {path}", True, "HTTP 200"))
            except Exception as exc:  # pragma: no cover - live smoke failure path
                endpoint_results[path] = {"error": str(exc)}
                assertions.append(SmokeAssertion(f"GET {path}", False, str(exc)))

        sessions: dict[tuple[str, str], dict[str, Any]] = {}
        for case in TEST_CASES:
            key = (case["source_domain"], case["language"])
            try:
                session = sessions.setdefault(key, start_session(client, case["source_domain"], case["language"]))
                payload = send_message(client, session, case)
            except Exception as exc:  # pragma: no cover - live smoke failure path
                assertions.append(SmokeAssertion(f"message {case['kind']}", False, str(exc)))
                case_results.append({**case, "error": str(exc)})
                continue

            preview = response_preview(payload)
            case_results.append({**case, **preview})
            assertions.extend(assert_case(case, payload))

    failures = [assertion.__dict__ for assertion in assertions if not assertion.passed]
    no_contact_guard_confirmed = all(
        result.get("created_lead_id") is None
        and result.get("created_task_id") is None
        and result.get("should_create_lead") is not True
        for result in case_results
        if "error" not in result
    )
    sensitive_answers_conservative = not any(
        failure["name"] in {"tuition answer conservative", "deadline answer conservative"}
        for failure in failures
    )

    return {
        "base_url": base_url,
        "total_tests": len(assertions),
        "passed": len(assertions) - len(failures),
        "failed": len(failures),
        "status": "PASSED" if not failures else "FAILED_NEEDS_REVIEW",
        "failures": failures,
        "endpoint_results": {
            path: {"status_code": result.get("status_code"), "summary": summarize_endpoint(path, result)}
            for path, result in endpoint_results.items()
        },
        "case_results": case_results,
        "no_contact_guard_confirmed": no_contact_guard_confirmed,
        "sensitive_answers_conservative": sensitive_answers_conservative,
        "contact_flow_test_run": CONTACT_FLOW_TEST_RUN,
        "contact_details_sent": CONTACT_DETAILS_SENT,
        "intentional_lead_task_creation": INTENTIONAL_LEAD_TASK_CREATION,
    }


def summarize_endpoint(path: str, result: dict[str, Any]) -> str:
    if "error" in result:
        return "ERROR"
    data = result.get("json") or {}
    if path == "/diagnostics/ai":
        return f"provider={data.get('ai_provider')}, claude_enabled={data.get('claude_enabled')}, warnings={len(data.get('warnings') or [])}"
    if path == "/health":
        return f"status={data.get('status')}, version={data.get('version')}"
    if path == "/version":
        return f"service={data.get('service')}, version={data.get('version')}"
    return "OK"


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
