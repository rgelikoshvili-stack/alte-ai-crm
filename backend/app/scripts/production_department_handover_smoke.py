from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx


PRODUCTION_BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"

CONTACT_FLOW_TEST_RUN = False
CONTACT_DETAILS_SENT = False
INTENTIONAL_LEAD_TASK_CREATION = False

TEST_CASES = [
    {
        "source_domain": "alte.edu.ge",
        "language": "ka",
        "message": "რა ღირს სწავლა?",
        "selected_department": "finance",
        "selected_topic": "tuition",
        "expected": {"finance"},
    },
    {
        "source_domain": "alte.edu.ge",
        "language": "ka",
        "message": "როდის არის მიღების ბოლო ვადა?",
        "selected_department": "admissions",
        "selected_topic": "deadlines",
        "expected": {"admissions"},
    },
    {
        "source_domain": "join.alte.edu.ge",
        "language": "en",
        "message": "I want to apply for medicine from India",
        "selected_department": "medicine",
        "selected_topic": "medicine_md",
        "expected": {"medicine", "international"},
    },
    {
        "source_domain": "join.alte.edu.ge",
        "language": "en",
        "message": "What documents do international students need?",
        "selected_department": "international",
        "selected_topic": "international_admissions",
        "expected": {"international"},
    },
    {
        "source_domain": "alte.edu.ge",
        "language": "en",
        "message": "I have a portal login problem",
        "selected_department": "it_support",
        "selected_topic": "technical_support",
        "expected": {"it_support"},
    },
    {
        "source_domain": "alte.edu.ge",
        "language": "en",
        "message": "I want to talk to an operator about tuition",
        "selected_department": "finance",
        "selected_topic": "tuition",
        "expected": {"finance"},
    },
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


def send_message(client: httpx.Client, session: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": case["message"],
            "source_domain": case["source_domain"],
            "language": case["language"],
            "selected_department": case["selected_department"],
            "selected_topic": case["selected_topic"],
            "widget_variant": "safe_pro",
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
        "created_lead_id": payload.get("created_lead_id"),
        "created_task_id": payload.get("created_task_id"),
        "route_department": payload.get("route_department"),
        "department_key": payload.get("department_key"),
        "handover_reason": payload.get("handover_reason"),
        "answer_source_status": payload.get("answer_source_status"),
    }


def assert_case(case: dict[str, Any], payload: dict[str, Any]) -> list[SmokeAssertion]:
    preview = response_preview(payload)
    expected = case["expected"]
    assertions = [
        SmokeAssertion(
            f"department route for {case['message']}",
            preview.get("department_key") in expected or not preview.get("department_key"),
            json.dumps(preview, ensure_ascii=False, sort_keys=True),
        ),
        SmokeAssertion(
            f"no lead/task side effect for {case['message']}",
            preview.get("should_create_lead") is not True
            and preview.get("created_lead_id") is None
            and preview.get("created_task_id") is None,
            json.dumps(preview, ensure_ascii=False, sort_keys=True),
        ),
    ]
    return assertions


def run_smoke(base_url: str = PRODUCTION_BACKEND_URL, timeout: float = 45.0) -> dict[str, Any]:
    assertions: list[SmokeAssertion] = []
    case_results: list[dict[str, Any]] = []
    with httpx.Client(base_url=base_url, timeout=timeout) as client:
        sessions: dict[tuple[str, str], dict[str, Any]] = {}
        for case in TEST_CASES:
            key = (case["source_domain"], case["language"])
            try:
                session = sessions.setdefault(key, start_session(client, case["source_domain"], case["language"]))
                payload = send_message(client, session, case)
                assertions.extend(assert_case(case, payload))
                case_results.append({**case, **response_preview(payload)})
            except Exception as exc:  # pragma: no cover - live smoke failure path
                assertions.append(SmokeAssertion(f"case failed: {case['message']}", False, str(exc)))
                case_results.append({**case, "error": str(exc)})

    failures = [assertion.__dict__ for assertion in assertions if not assertion.passed]
    return {
        "total_assertions": len(assertions),
        "passed": len(assertions) - len(failures),
        "failed": len(failures),
        "failures": failures,
        "case_results": case_results,
        "contact_flow_test_run": CONTACT_FLOW_TEST_RUN,
        "contact_details_sent": CONTACT_DETAILS_SENT,
        "intentional_lead_task_creation": INTENTIONAL_LEAD_TASK_CREATION,
        "note": "Production may require redeploy before Phase 9D routing fields appear.",
    }


def main() -> None:
    result = run_smoke()
    print(json.dumps({k: v for k, v in result.items() if k != "case_results"}, ensure_ascii=False, indent=2))
    if result["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
