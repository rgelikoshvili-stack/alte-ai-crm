from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


BASE_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
NETLIFY_ORIGIN = "https://nimble-croissant-2f66e8.netlify.app"
NETLIFY_URL = f"{NETLIFY_ORIGIN}/join.html"

BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
REPORT_JSON = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AD_ROUTING_FIX_SMOKE_RESULT.json"

DIRECT_CONTACT_PATTERNS = [
    re.compile(r"(type|enter|send|provide|share|write).{0,50}(phone|email|name|whatsapp)", re.I),
    re.compile(r"(phone|email|name|whatsapp).{0,50}(type|enter|send|provide|share|write)", re.I),
    re.compile(r"(ტელეფონ|ელფოსტ|ელ\.ფოსტ|მეილ|სახელ|whatsapp).{0,50}(მომწერ|შეიყვან|გამოგზავნ|მიუთით|დაწერ)", re.I),
    re.compile(r"(მომწერ|შეიყვან|გამოგზავნ|მიუთით|დაწერ).{0,50}(ტელეფონ|ელფოსტ|ელ\.ფოსტ|მეილ|სახელ|whatsapp)", re.I),
]


@dataclass(frozen=True)
class SmokeCase:
    case_id: str
    message: str
    expected_route_any: list[str] = field(default_factory=list)
    forbidden_route_any: list[str] = field(default_factory=list)
    expected_status: str | None = None
    must_include: list[str] = field(default_factory=list)
    must_exclude: list[str] = field(default_factory=list)
    expect_handover: bool | None = None
    require_sources: bool = False
    language: str = "ka"


CASES = [
    SmokeCase(
        "admissions_auto_route_fixed",
        "როგორ ჩავირიცხო ბაკალავრიატზე?",
        expected_route_any=["admissions", "registration"],
        forbidden_route_any=["programs", "international"],
    ),
    SmokeCase(
        "library_auto_route_fixed",
        "ბიბლიოთეკის რესურსები როგორ გამოვიყენო?",
        expected_route_any=["library"],
        forbidden_route_any=["international"],
    ),
    SmokeCase(
        "finance_handover_route_fixed",
        "მინდა ფინანსურ დეპარტამენტთან დაკავშირება სწავლის საფასურზე",
        expected_route_any=["finance"],
        forbidden_route_any=["international"],
        expect_handover=True,
    ),
    SmokeCase(
        "international_medicine_control",
        "I am an international student and want to apply to Medicine.",
        expected_route_any=["international", "medicine"],
        language="en",
    ),
    SmokeCase(
        "official_bachelor_ects_240_control",
        "რამდენი ECTS კრედიტია საჭირო საბაკალავრო პროგრამის დასასრულებლად?",
        expected_status="answered_from_approved_source",
        must_include=["240"],
        must_exclude=["180"],
        require_sources=True,
    ),
    SmokeCase(
        "unsupported_2031_scholarship_control",
        "2031 წლის კოსმოსური კამპუსის სტიპენდია როგორ მივიღო?",
        expected_status="no_approved_source_found",
        must_exclude=["eligible", "deadline", "70%", "50%"],
    ),
]


def _request(method: str, url: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, str], Any]:
    headers = {"Origin": NETLIFY_ORIGIN}
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, dict(resp.headers), json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"detail": raw[:200]}
        return exc.code, dict(exc.headers), data


def _start_session() -> dict[str, Any]:
    status, _, data = _request(
        "POST",
        f"{BASE_URL}/chat/session/start",
        {
            "channel": "website_chat",
            "source_domain": "join.alte.edu.ge",
            "language": "ka",
            "widget_variant": "pro_v2_safe",
            "metadata": {"page_url": NETLIFY_URL, "phase": "9ad_routing_fix_no_contact_smoke"},
        },
    )
    if status != 200:
        raise RuntimeError(f"session_start_failed:{status}")
    return data


def _send(case: SmokeCase) -> tuple[dict[str, Any], str | None]:
    session = _start_session()
    status, headers, data = _request(
        "POST",
        f"{BASE_URL}/chat/message",
        {
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": case.message,
            "source_domain": "join.alte.edu.ge",
            "language": case.language,
            "page_url": NETLIFY_URL,
            "widget_variant": "pro_v2_safe",
        },
    )
    if status != 200:
        return {"error": f"http_{status}", "payload": data}, headers.get("access-control-allow-origin")
    return data, headers.get("access-control-allow-origin")


def _route_text(payload: dict[str, Any]) -> str:
    return " ".join(
        str(payload.get(key) or "")
        for key in ["route_department", "department_key", "routing_reason", "intent"]
    ).lower()


def _has_direct_contact_request(reply: str) -> bool:
    return any(pattern.search(reply) for pattern in DIRECT_CONTACT_PATTERNS)


def _evaluate(case: SmokeCase, payload: dict[str, Any], allow_origin: str | None) -> dict[str, Any]:
    reply = str(payload.get("reply") or "")
    sources = payload.get("used_sources") or []
    checks = {
        "http_ok": "error" not in payload,
        "cors_exact_origin": allow_origin == NETLIFY_ORIGIN,
        "route": not case.expected_route_any or any(token in _route_text(payload) for token in case.expected_route_any),
        "forbidden_route": not any(token in _route_text(payload) for token in case.forbidden_route_any),
        "source_status": case.expected_status is None or payload.get("answer_source_status") == case.expected_status,
        "sources": not case.require_sources or len(sources) > 0,
        "must_include": all(token in reply for token in case.must_include),
        "must_exclude": not any(token in reply for token in case.must_exclude),
        "handover": case.expect_handover is None or payload.get("should_handover") is case.expect_handover,
        "no_direct_contact_request": not _has_direct_contact_request(reply),
        "no_created_lead": payload.get("created_lead_id") is None,
        "no_created_task": payload.get("created_task_id") is None,
        "no_create_lead_flag": payload.get("should_create_lead") is not True,
    }
    return {
        "case_id": case.case_id,
        "passed": all(checks.values()),
        "checks": checks,
        "answer_source_status": payload.get("answer_source_status"),
        "route_department": payload.get("route_department"),
        "department_key": payload.get("department_key"),
        "routing_reason": payload.get("routing_reason"),
        "intent": payload.get("intent"),
        "should_handover": payload.get("should_handover"),
        "created_lead": payload.get("created_lead_id") is not None,
        "created_task": payload.get("created_task_id") is not None,
        "reply_excerpt": reply[:280],
    }


def run_smoke() -> dict[str, Any]:
    results = []
    for case in CASES:
        payload, allow_origin = _send(case)
        results.append(_evaluate(case, payload, allow_origin))
        time.sleep(0.25)
    summary = {
        "total": len(results),
        "passed": sum(1 for row in results if row["passed"]),
        "failed": sum(1 for row in results if not row["passed"]),
        "any_created_lead_or_task": any(row["created_lead"] or row["created_task"] for row in results),
        "any_direct_contact_request": any(not row["checks"]["no_direct_contact_request"] for row in results),
    }
    report = {
        "status": "PASSED" if summary["failed"] == 0 else "FAILED",
        "backend_url": BASE_URL,
        "origin": NETLIFY_ORIGIN,
        "summary": summary,
        "results": results,
        "contact_details_sent": False,
        "production_db_writes_intentional": False,
        "public_launch": "NO-GO",
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> None:
    report = run_smoke()
    print(
        json.dumps(
            {
                "status": report["status"],
                "summary": report["summary"],
                "report_json": str(REPORT_JSON.relative_to(PROJECT_ROOT)),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    if report["status"] != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
