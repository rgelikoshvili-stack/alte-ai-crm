from __future__ import annotations

import json
import re
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


BASE_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
NETLIFY_ORIGIN = "https://nimble-croissant-2f66e8.netlify.app"
NETLIFY_URL = f"{NETLIFY_ORIGIN}/join.html"
OPERATOR_URL = "http://127.0.0.1:5173"

BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
REPORT_JSON = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AC_INTEGRATED_CHAT_ROUTING_OPERATOR_QA_RESULT.json"

DIRECT_CONTACT_PATTERNS = [
    re.compile(r"(type|enter|send|provide|share|write).{0,50}(phone|email|name|whatsapp)", re.I),
    re.compile(r"(phone|email|name|whatsapp).{0,50}(type|enter|send|provide|share|write)", re.I),
    re.compile(r"(ტელეფონ|ელფოსტ|ელ\.ფოსტ|მეილ|სახელ|whatsapp).{0,50}(მომწერ|შეიყვან|გამოგზავნ|მიუთით|დაწერ)", re.I),
    re.compile(r"(მომწერ|შეიყვან|გამოგზავნ|მიუთით|დაწერ).{0,50}(ტელეფონ|ელფოსტ|ელ\.ფოსტ|მეილ|სახელ|whatsapp)", re.I),
]


@dataclass(frozen=True)
class QaCase:
    case_id: str
    message: str
    group: str
    expected_status: str | None = None
    must_include: list[str] = field(default_factory=list)
    must_include_any: list[list[str]] = field(default_factory=list)
    must_exclude: list[str] = field(default_factory=list)
    expected_route_any: list[str] = field(default_factory=list)
    forbidden_route_any: list[str] = field(default_factory=list)
    expect_handover: bool | None = None
    require_sources: bool = False


OFFICIAL_KB_CASES = [
    QaCase(
        "kb_bachelor_ects",
        "რამდენი ECTS კრედიტია საჭირო საბაკალავრო პროგრამის დასასრულებლად?",
        "official_kb",
        expected_status="answered_from_approved_source",
        must_include=["240"],
        must_exclude=["180"],
        require_sources=True,
    ),
    QaCase(
        "kb_master_ects",
        "რამდენი კრედიტია სამაგისტრო პროგრამა ალტე უნივერსიტეტში?",
        "official_kb",
        expected_status="answered_from_approved_source",
        must_include=["120"],
        require_sources=True,
    ),
    QaCase(
        "kb_teaching_language",
        "რა ენაზე მიმდინარეობს სწავლება ალტე უნივერსიტეტში?",
        "official_kb",
        expected_status="answered_from_approved_source",
        must_include_any=[["ქართულ"], ["ინგლისურ", "English"]],
        must_exclude=["planned", "დაგეგმილ"],
        require_sources=True,
    ),
    QaCase(
        "kb_status_suspension",
        "რამდენი წლით შეიძლება სტუდენტის სტატუსის შეჩერება?",
        "official_kb",
        expected_status="answered_from_approved_source",
        must_include=["5"],
        require_sources=True,
    ),
    QaCase(
        "kb_cs_spring_registration",
        "როდის არის Computer Science-ის სტუდენტებისთვის გაზაფხულის სემესტრის რეგისტრაცია?",
        "official_kb",
        expected_status="answered_from_approved_source",
        must_include=["9", "14", "30"],
        must_include_any=[["მარტ", "March"]],
        require_sources=True,
    ),
    QaCase(
        "kb_master_documents",
        "რა საბუთები მჭირდება მაგისტრატურაზე ჩასარიცხად?",
        "official_kb",
        expected_status="answered_from_approved_source",
        must_include_any=[
            ["პირადობის", "ID"],
            ["CV", "რეზიუმ"],
            ["3x4", "3 x 4", "3*4"],
            ["სამხედრო", "military"],
            ["ნოტარ", "notar"],
            ["დიპლომის დანართ", "supplement"],
        ],
        require_sources=True,
    ),
]

ROUTING_CASES = [
    QaCase(
        "admissions_auto_route_fixed",
        "როგორ ჩავირიცხო ბაკალავრიატზე?",
        "auto_routing",
        expected_route_any=["admissions", "registration", "student_services"],
        forbidden_route_any=["programs", "international"],
    ),
    QaCase("route_programs", "რა პროგრამები გაქვთ და რომელზე შემიძლია ჩაბარება?", "auto_routing", expected_route_any=["programs", "admissions"]),
    QaCase("route_finance", "სწავლის საფასურის გადახდის გრაფიკი მაინტერესებს", "auto_routing", expected_route_any=["finance", "tuition"]),
    QaCase("route_student_status", "სტუდენტის სტატუსის შეჩერება მინდა", "auto_routing", expected_route_any=["study_process", "student_status", "registrar"]),
    QaCase("route_exams", "დასკვნით გამოცდაზე ვერ მივედი საპატიო მიზეზით, რა ვქნა?", "auto_routing", expected_route_any=["exams", "study_process"]),
    QaCase("route_mobility", "სხვა უნივერსიტეტიდან გადმოსვლა მინდა და კრედიტების აღიარება როგორ ხდება?", "auto_routing", expected_route_any=["mobility", "ects", "study_process"]),
    QaCase("route_international_medicine", "I am an international student and want to apply to Medicine.", "auto_routing", expected_route_any=["international", "medicine", "admissions"]),
    QaCase("route_it_help", "emis.alte.edu.ge-ში ვერ შევდივარ", "auto_routing", expected_route_any=["it", "support", "student_services"]),
    QaCase(
        "library_auto_route_fixed",
        "ბიბლიოთეკის რესურსები როგორ გამოვიყენო?",
        "auto_routing",
        expected_route_any=["library"],
        forbidden_route_any=["international"],
    ),
    QaCase(
        "route_unsupported_2031",
        "2031 წლის კოსმოსური კამპუსის სტიპენდია როგორ მივიღო?",
        "auto_routing",
        expected_status="no_approved_source_found",
        expected_route_any=["admissions", "general", "operator", "finance"],
        require_sources=False,
        must_exclude=["eligible", "deadline", "70%", "50%"],
    ),
]

HANDOVER_CASES = [
    QaCase("handover_operator", "მინდა ოპერატორთან დაკავშირება", "handover", expect_handover=True),
    QaCase(
        "finance_handover_route_fixed",
        "მინდა ფინანსურ დეპარტამენტთან დაკავშირება სწავლის საფასურზე",
        "handover",
        expected_route_any=["finance"],
        forbidden_route_any=["international"],
        expect_handover=True,
    ),
]


def _request(method: str, url: str, payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> tuple[int, dict[str, str], Any]:
    body = None
    req_headers = dict(headers or {})
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        req_headers["Content-Type"] = "application/json; charset=utf-8"
    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read().decode("utf-8")
            try:
                data = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                data = {"body_excerpt": raw[:160]}
            return resp.status, dict(resp.headers), data
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"detail": raw[:200]}
        return exc.code, dict(exc.headers), data
    except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
        return 0, {}, {"error": type(exc).__name__, "detail": str(exc)[:180]}


def _health(path: str) -> int:
    status, _, _ = _request("GET", f"{BASE_URL}{path}")
    return status


def _netlify_status() -> int:
    status, _, _ = _request("GET", NETLIFY_URL)
    return status


def _operator_status() -> int | None:
    try:
        status, _, _ = _request("GET", OPERATOR_URL)
        return status
    except Exception:
        return None


def _start_session() -> dict[str, Any]:
    status, _, data = _request(
        "POST",
        f"{BASE_URL}/chat/session/start",
        {
            "channel": "website_chat",
            "source_domain": "join.alte.edu.ge",
            "language": "ka",
            "widget_variant": "pro_v2_safe",
            "metadata": {"page_url": NETLIFY_URL, "phase": "9ac_integrated_no_contact_qa"},
        },
        {"Origin": NETLIFY_ORIGIN},
    )
    if status != 200:
        raise RuntimeError(f"session_start_failed:{status}")
    return data


def _send(session: dict[str, Any], case: QaCase) -> tuple[dict[str, Any], str | None]:
    status, headers, data = _request(
        "POST",
        f"{BASE_URL}/chat/message",
        {
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": case.message,
            "source_domain": "join.alte.edu.ge",
            "language": "ka" if not case.message.startswith("I am ") else "en",
            "page_url": NETLIFY_URL,
            "widget_variant": "pro_v2_safe",
        },
        {"Origin": NETLIFY_ORIGIN},
    )
    if status != 200:
        return {"error": f"http_{status}", "payload": data}, headers.get("access-control-allow-origin")
    return data, headers.get("access-control-allow-origin")


def _has_direct_contact_request(reply: str) -> bool:
    return any(pattern.search(reply) for pattern in DIRECT_CONTACT_PATTERNS)


def _route_text(payload: dict[str, Any]) -> str:
    parts = [
        str(payload.get("route_department") or ""),
        str(payload.get("department_key") or ""),
        str(payload.get("routing_reason") or ""),
        str(payload.get("intent") or ""),
    ]
    return " ".join(parts).lower()


def _evaluate(case: QaCase, payload: dict[str, Any], allow_origin: str | None) -> dict[str, Any]:
    reply = str(payload.get("reply") or "")
    sources = payload.get("used_sources") or []
    route_text = _route_text(payload)
    checks = {
        "http_ok": "error" not in payload,
        "cors_exact_origin": allow_origin == NETLIFY_ORIGIN,
        "source_status": case.expected_status is None or payload.get("answer_source_status") == case.expected_status,
        "sources": not case.require_sources or len(sources) > 0,
        "must_include": all(token in reply for token in case.must_include),
        "must_include_any": all(any(token in reply for token in group) for group in case.must_include_any),
        "must_exclude": not any(token in reply for token in case.must_exclude),
        "route": not case.expected_route_any or any(token in route_text for token in case.expected_route_any),
        "forbidden_route": not any(token in route_text for token in case.forbidden_route_any),
        "handover": case.expect_handover is None or payload.get("should_handover") is case.expect_handover,
        "no_direct_contact_request": not _has_direct_contact_request(reply),
        "no_created_lead": payload.get("created_lead_id") is None,
        "no_created_task": payload.get("created_task_id") is None,
        "no_create_lead_flag": payload.get("should_create_lead") is not True,
    }
    passed = all(checks.values())
    return {
        "case_id": case.case_id,
        "group": case.group,
        "passed": passed,
        "checks": checks,
        "answer_source_status": payload.get("answer_source_status"),
        "used_sources_count": len(sources),
        "route_department": payload.get("route_department"),
        "department_key": payload.get("department_key"),
        "routing_reason": payload.get("routing_reason"),
        "intent": payload.get("intent"),
        "should_handover": payload.get("should_handover"),
        "should_create_lead": payload.get("should_create_lead"),
        "created_lead": payload.get("created_lead_id") is not None,
        "created_task": payload.get("created_task_id") is not None,
        "reply_excerpt": reply[:360],
    }


def run_qa() -> dict[str, Any]:
    cases = OFFICIAL_KB_CASES + ROUTING_CASES + HANDOVER_CASES
    baseline = {
        "backend_health": _health("/health"),
        "backend_version": _health("/version"),
        "backend_diagnostics_ai": _health("/diagnostics/ai"),
        "dashboard_overview_unauthenticated": _health("/dashboard/overview"),
        "netlify_join": _netlify_status(),
        "operator_crm_local": _operator_status(),
    }
    results: list[dict[str, Any]] = []
    for case in cases:
        session = _start_session()
        payload, allow_origin = _send(session, case)
        results.append(_evaluate(case, payload, allow_origin))
        time.sleep(0.25)

    summary = {
        "total": len(results),
        "passed": sum(1 for row in results if row["passed"]),
        "failed": sum(1 for row in results if not row["passed"]),
        "official_kb_passed": sum(1 for row in results if row["group"] == "official_kb" and row["passed"]),
        "official_kb_total": sum(1 for row in results if row["group"] == "official_kb"),
        "auto_routing_passed": sum(1 for row in results if row["group"] == "auto_routing" and row["passed"]),
        "auto_routing_total": sum(1 for row in results if row["group"] == "auto_routing"),
        "handover_passed": sum(1 for row in results if row["group"] == "handover" and row["passed"]),
        "handover_total": sum(1 for row in results if row["group"] == "handover"),
        "any_created_lead_or_task": any(row["created_lead"] or row["created_task"] for row in results),
        "any_direct_contact_request": any(not row["checks"]["no_direct_contact_request"] for row in results),
    }
    report = {
        "status": "PASSED" if summary["failed"] == 0 else "FAILED",
        "backend_url": BASE_URL,
        "netlify_url": NETLIFY_URL,
        "operator_crm_url": OPERATOR_URL,
        "origin": NETLIFY_ORIGIN,
        "baseline": baseline,
        "summary": summary,
        "results": results,
        "production_db_writes_intentional": False,
        "contact_details_sent": False,
        "public_launch": "NO-GO",
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> None:
    report = run_qa()
    print(
        json.dumps(
            {
                "status": report["status"],
                "baseline": report["baseline"],
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
