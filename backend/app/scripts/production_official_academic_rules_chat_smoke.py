from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

import httpx


BASE_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
CONTACT_PATTERNS = [
    re.compile(r"phone", re.IGNORECASE),
    re.compile(r"email", re.IGNORECASE),
    re.compile(r"contact details", re.IGNORECASE),
    re.compile(r"ტელეფონ"),
    re.compile(r"ელ\.?ფოსტ"),
]


@dataclass
class Case:
    id: str
    message: str
    language: str
    must_include: list[str]
    must_exclude: list[str]


CASES = [
    Case(
        id="bachelor_ects",
        message="რამდენი ECTS კრედიტია საჭირო საბაკალავრო პროგრამის დასასრულებლად?",
        language="ka",
        must_include=["240"],
        must_exclude=["180", "3-წლიანი", "3 წელი"],
    ),
    Case(
        id="master_ects",
        message="რამდენი კრედიტია სამაგისტრო პროგრამა ალტე უნივერსიტეტში?",
        language="ka",
        must_include=["120"],
        must_exclude=[],
    ),
    Case(
        id="teaching_language",
        message="რა ენაზე მიმდინარეობს სწავლება ალტე უნივერსიტეტში?",
        language="ka",
        must_include=["ქართული", "ინგლისურ"],
        must_exclude=["დაგეგმ"],
    ),
    Case(
        id="status_suspension",
        message="რამდენი წლით შეიძლება სტუდენტის სტატუსის შეჩერება?",
        language="ka",
        must_include=["5"],
        must_exclude=[],
    ),
]


def start_session(client: httpx.Client, language: str) -> dict[str, Any]:
    response = client.post(
        "/chat/session/start",
        json={"channel": "website_chat", "source_domain": "alte.edu.ge", "language": language},
    )
    response.raise_for_status()
    return response.json()


def send_message(client: httpx.Client, session: dict[str, Any], case: Case) -> dict[str, Any]:
    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session.get("conversation_id"),
            "session_id": session.get("session_id"),
            "message": case.message,
            "source_domain": "alte.edu.ge",
            "language": case.language,
        },
    )
    response.raise_for_status()
    return response.json()


def contains_contact_request(reply: str) -> bool:
    return any(pattern.search(reply) for pattern in CONTACT_PATTERNS)


def sanitized_result(case: Case, payload: dict[str, Any]) -> dict[str, Any]:
    reply = str(payload.get("reply") or "")
    used_sources = payload.get("used_sources") or []
    return {
        "id": case.id,
        "http_ok": True,
        "answer_source_status": payload.get("answer_source_status"),
        "used_sources_count": len(used_sources),
        "has_required_values": all(value in reply for value in case.must_include),
        "has_forbidden_values": any(value in reply for value in case.must_exclude),
        "requests_contact": contains_contact_request(reply),
        "should_create_lead": payload.get("should_create_lead"),
        "created_lead": payload.get("created_lead_id") is not None,
        "created_task": payload.get("created_task_id") is not None,
        "reply_len": len(reply),
    }


def run_smoke(base_url: str = BASE_URL) -> dict[str, Any]:
    results = []
    with httpx.Client(base_url=base_url, timeout=180.0) as client:
        health = client.get("/health")
        health.raise_for_status()
        for case in CASES:
            session = start_session(client, case.language)
            payload = send_message(client, session, case)
            row = sanitized_result(case, payload)
            row["passed"] = (
                row["answer_source_status"] == "answered_from_approved_source"
                and row["used_sources_count"] > 0
                and row["has_required_values"]
                and not row["has_forbidden_values"]
                and not row["requests_contact"]
                and row["should_create_lead"] is not True
                and not row["created_lead"]
                and not row["created_task"]
            )
            results.append(row)
    passed = sum(1 for row in results if row["passed"])
    return {
        "base_url": base_url,
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
    }


def main() -> None:
    result = run_smoke()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if result["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
