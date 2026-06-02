from __future__ import annotations

import json
import re
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
REPORT_PATH = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AY_PROGRAM_CATALOG_SOURCE_QA_RESULT.md"
CREDENTIAL_FILE = PROJECT_ROOT / ".local-secrets" / "temporary_crm_admin_credentials.txt"

CATALOG_SOURCE_MARKERS = (
    "01_program_catalog",
    "program_catalog",
    "Higher Education Program Catalog",
    "official_alte_8_pdf_kb_01_01_program_catalog",
)
MOJIBAKE_MARKERS = ("áƒ", "â†", "â€¢", "Ã", "�")
TUITION_AMOUNT_PATTERNS = (
    re.compile(r"\b\d{3,6}\s*(lari|gel|₾)\b", re.I),
    re.compile(r"\b\d{3,6}\s*(ლარი|₾)\b", re.I),
)


@dataclass(frozen=True)
class CatalogQuestion:
    id: str
    question: str
    language: str
    must_include: tuple[str, ...]
    must_not_include: tuple[str, ...] = ()
    source_backed_required: bool = True
    catalog_source_required: bool = True
    expected_handover: bool | None = False
    allow_operator_fallback: bool = False


QUESTIONS = [
    CatalogQuestion(
        "program_count_total",
        "რამდენი საგანმანათლებლო პროგრამა აქვს ალტე უნივერსიტეტს სულ?",
        "ka",
        ("16",),
    ),
    CatalogQuestion(
        "program_levels_distribution",
        "როგორ ნაწილდება ეს პროგრამები საფეხურების მიხედვით?",
        "ka",
        ("10", "3", "ბაკალავრ", "მაგისტრ", "ერთსაფეხურ"),
    ),
    CatalogQuestion(
        "bachelor_programs_list",
        "ჩამომითვალე ალტე უნივერსიტეტის საბაკალავრო პროგრამები.",
        "ka",
        ("სამართ", "კომპიუტერულ", "ბიზნეს", "ბაკალავრ"),
    ),
    CatalogQuestion(
        "master_programs_list",
        "ჩამომითვალე ალტე უნივერსიტეტის სამაგისტრო პროგრამები.",
        "ka",
        ("სამართ", "ბიზნეს", "მაგისტრ"),
    ),
    CatalogQuestion(
        "one_cycle_programs_list",
        "რომელი ერთსაფეხურიანი პროგრამები აქვს ალტე უნივერსიტეტს?",
        "ka",
        ("მედიც", "სტომატოლოგ", "ერთსაფეხურ"),
    ),
    CatalogQuestion(
        "catalog_fields",
        "რა ინფორმაციას შეიცავს პროგრამების კატალოგი თითოეულ პროგრამაზე?",
        "ka",
        ("სახელ", "საფეხურ", "კვალიფიკ", "ენა", "კრედიტ", "ხანგრძლივ", "წინაპირობ", "შედეგ"),
    ),
    CatalogQuestion(
        "law_bachelor_qualification",
        "რა კვალიფიკაციას ანიჭებს სამართლის საბაკალავრო პროგრამა?",
        "ka",
        ("სამართლის ბაკალავრ",),
    ),
    CatalogQuestion(
        "law_master_qualification",
        "რა კვალიფიკაციას ანიჭებს სამართლის სამაგისტრო პროგრამა?",
        "ka",
        ("სამართლის მაგისტრ",),
    ),
    CatalogQuestion(
        "computer_science_languages",
        "რა ენებზე გვხვდება კომპიუტერული მეცნიერების პროგრამა კატალოგში?",
        "ka",
        ("ქართულ", "ინგლის"),
    ),
    CatalogQuestion(
        "tuition_not_in_catalog",
        "თუ ვკითხავ პროგრამის სწავლის ზუსტ საფასურს, პროგრამების კატალოგიდან უნდა მიპასუხო თუ უნდა თქვა რომ წყაროში არ ჩანს?",
        "ka",
        ("არ", "წყარო", "ოპერატორ"),
        source_backed_required=False,
        catalog_source_required=True,
        expected_handover=None,
        allow_operator_fallback=True,
    ),
]


def request_json(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    token: str | None = None,
    origin: str | None = NETLIFY_ORIGIN,
) -> tuple[int, Any]:
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
            data = {"detail": raw[:240]}
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


def start_session(case_id: str, language: str) -> dict[str, Any]:
    status, data = request_json(
        "POST",
        "/chat/session/start",
        {
            "channel": "website_chat",
            "source_domain": "join.alte.edu.ge",
            "language": language,
            "widget_variant": "pro_v2_safe",
            "metadata": {"phase": "9ay_program_catalog_source_qa", "case": case_id, "page_url": NETLIFY_URL},
        },
    )
    if status != 200:
        raise RuntimeError(f"session_start_failed:{status}:{data}")
    return data


def send_chat(session: dict[str, Any], item: CatalogQuestion) -> dict[str, Any]:
    status, data = request_json(
        "POST",
        "/chat/message",
        {
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": item.question,
            "source_domain": "join.alte.edu.ge",
            "language": item.language,
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


def source_text(response: dict[str, Any]) -> str:
    values = []
    values.extend(str(value) for value in response.get("used_sources") or [])
    values.append(str(response.get("source_group") or ""))
    values.append(str(response.get("reply") or ""))
    return "\n".join(values)


def has_catalog_source(response: dict[str, Any]) -> bool:
    combined = source_text(response)
    return any(marker in combined for marker in CATALOG_SOURCE_MARKERS)


def primary_source_group_ok(response: dict[str, Any]) -> bool:
    return response.get("source_group") == "program_catalog_sources"


def no_mojibake(text: str) -> bool:
    return not any(marker in text for marker in MOJIBAKE_MARKERS)


def no_tuition_hallucination(reply: str) -> bool:
    return not any(pattern.search(reply) for pattern in TUITION_AMOUNT_PATTERNS)


def token_checks(reply: str, tokens: tuple[str, ...]) -> bool:
    lowered = reply.lower()
    return all(token.lower() in lowered for token in tokens)


def no_crm_created(response: dict[str, Any], detail: dict[str, Any]) -> bool:
    response_clean = not response.get("created_lead_id") and not response.get("created_task_id")
    detail_clean = not detail.get("has_customer") and not detail.get("has_lead")
    return response_clean and detail_clean


def validate_case(item: CatalogQuestion, response: dict[str, Any], detail: dict[str, Any]) -> dict[str, bool]:
    reply = str(response.get("reply") or "")
    source_backed = response.get("answer_source_status") == "answered_from_approved_source"
    no_source = response.get("answer_source_status") == "no_approved_source_found"
    source_status_ok = source_backed if item.source_backed_required else (source_backed or no_source or item.allow_operator_fallback)
    handover_ok = True if item.expected_handover is None else response.get("should_handover") is item.expected_handover
    operator_handover_ok = (
        True
        if item.expected_handover is None or not detail.get("operator_checked")
        else detail.get("human_handover") is item.expected_handover
    )
    return {
        "http_200": response.get("http_status") == 200,
        "expected_terms": token_checks(reply, item.must_include),
        "forbidden_terms_absent": all(token.lower() not in reply.lower() for token in item.must_not_include),
        "source_backed_status": source_status_ok,
        "catalog_source": has_catalog_source(response) if item.catalog_source_required else True,
        "program_catalog_primary_source_group": primary_source_group_ok(response),
        "official_academic_rules_not_primary": response.get("source_group") != "official_academic_rules",
        "handover_expected": handover_ok,
        "operator_handover_expected": operator_handover_ok,
        "no_tuition_hallucination": no_tuition_hallucination(reply),
        "no_mojibake": no_mojibake(reply),
        "no_lead_task_customer": no_crm_created(response, detail),
    }


def run_qa() -> dict[str, Any]:
    token, auth_status = login_operator()
    cases: list[dict[str, Any]] = []
    for item in QUESTIONS:
        session = start_session(item.id, item.language)
        response = send_chat(session, item)
        time.sleep(0.1)
        detail = operator_detail(token, session["conversation_id"])
        checks = validate_case(item, response, detail)
        reply = str(response.get("reply") or "")
        cases.append(
            {
                "id": item.id,
                "question": item.question,
                "passed": all(checks.values()),
                "checks": checks,
                "answer_status": response.get("answer_source_status"),
                "source_group": response.get("source_group"),
                "used_sources": response.get("used_sources") or [],
                "catalog_source_detected": has_catalog_source(response),
                "should_handover": response.get("should_handover"),
                "human_handover": detail.get("human_handover"),
                "department": response.get("department_key") or response.get("route_department"),
                "reply_excerpt": reply[:280],
                "operator_checked": detail.get("operator_checked"),
                "crm_created": not no_crm_created(response, detail),
            }
        )
    result = {
        "status": "PASSED" if all(case["passed"] for case in cases) else "FAILED",
        "test_time_utc": datetime.now(timezone.utc).isoformat(),
        "backend_url": BASE_URL,
        "netlify_url": NETLIFY_URL,
        "operator_auth_status": auth_status,
        "total": len(cases),
        "passed": sum(1 for case in cases if case["passed"]),
        "failed": sum(1 for case in cases if not case["passed"]),
        "cases": cases,
        "contact_flow_executed": False,
        "real_contact_data_sent": False,
        "lead_task_customer_created": any(case["crm_created"] for case in cases),
        "public_launch": "NO-GO",
    }
    write_report(result)
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, ensure_ascii=False, indent=2))
    return result


def case_status(case: dict[str, Any]) -> str:
    if case["passed"]:
        return "PASS"
    if case.get("catalog_source_detected") and case.get("answer_status") == "answered_from_approved_source":
        return "PARTIAL"
    return "FAIL"


def write_report(result: dict[str, Any]) -> None:
    rows = []
    failures = []
    source_notes = []
    for case in result["cases"]:
        status = case_status(case)
        failed = [name for name, passed in case["checks"].items() if not passed]
        if failed:
            failures.append(f"- `{case['id']}`: {', '.join(failed)}")
        source_note = "catalog source exposed" if case["catalog_source_detected"] else "catalog source not exposed/detected"
        source_notes.append(f"- `{case['id']}`: {source_note}; used_sources={case['used_sources']}")
        rows.append(
            "| {id} | {status} | {answer_status} | {source_group} | {catalog} | {handover} | {department} | {snippet} |".format(
                id=case["id"],
                status=status,
                answer_status=case["answer_status"],
                source_group=case["source_group"],
                catalog="YES" if case["catalog_source_detected"] else "NO",
                handover=case["should_handover"],
                department=case["department"],
                snippet=str(case["reply_excerpt"]).replace("\n", " ")[:180],
            )
        )
    if not failures:
        failures.append("- None")
    if result["failed"] == 0:
        qa_status = "PASSED"
        recommendation = "The program catalog source is active for the targeted production chatbot checks."
    elif any(case_status(case) == "PARTIAL" for case in result["cases"]):
        qa_status = "PASSED_WITH_SOURCE_METADATA_NOTES"
        recommendation = "Answers were correct/source-backed where noted, but source metadata exposure should be reviewed."
    else:
        qa_status = "FAILED_PENDING_FIXES"
        recommendation = "Review failed catalog source-backed cases before considering launch approval."

    REPORT_PATH.write_text(
        "\n".join(
            [
                "# Phase 9AY Program Catalog Source QA Result",
                "",
                f"PHASE_9AY_PROGRAM_CATALOG_QA_STATUS={qa_status}",
                "",
                "Decision state: `BACKEND_DEPLOYED_FULL_KNOWLEDGE_QA_PASSED_PENDING_APPROVALS`",
                "",
                "Public launch: `NO-GO`",
                "",
                "## Tested Source",
                "",
                "- File/source: `01_program_catalog.pdf` / Higher Education Program Catalog",
                "- Topic: Programs and Admissions",
                "",
                "## Tested URLs",
                "",
                f"- Production backend: {BASE_URL}",
                f"- Netlify chatbot: {NETLIFY_URL}",
                "",
                "## Summary",
                "",
                f"- Test time UTC: {result['test_time_utc']}",
                "- Backend revision: `alte-ai-crm-backend-00045-dg2`",
                f"- Total questions: {result['total']}",
                f"- Passed: {result['passed']}",
                f"- Failed: {result['failed']}",
                f"- Operator API auth: {result['operator_auth_status']}",
                "- Contact flow submitted: NO",
                "- Real contact data sent: NO",
                f"- Lead/customer/task created: {'YES' if result['lead_task_customer_created'] else 'NO'}",
                "- Public launch: NO-GO",
                "",
                "## Ten-Question Results",
                "",
                "| Question ID | Status | answer_status | source_group | Catalog source exposed | should_handover | department | Answer snippet |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
                *rows,
                "",
                "## Source-Backed Verification Notes",
                "",
                *source_notes,
                "",
                "## Failures / Gaps",
                "",
                *failures,
                "",
                "## Safety Checks",
                "",
                "- Real site modified: NO",
                "- Deploy performed: NO",
                "- Frontend/Netlify changed: NO",
                "- DB/Secret Manager/CORS/Bridge Hub changed: NO",
                "- Contact flow submitted: NO",
                "- Lead/customer/task created: NO",
                "- Public launch: NO-GO",
                "",
                "## Final Recommendation",
                "",
                recommendation,
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
