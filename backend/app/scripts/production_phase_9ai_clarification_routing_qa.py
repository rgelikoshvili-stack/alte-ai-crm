from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any
from urllib import request


BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
ORIGIN = "https://nimble-croissant-2f66e8.netlify.app"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPORT_PATH = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AI_CLARIFICATION_ROUTING_QA_RESULT.md"
MOJIBAKE_MARKER = "\u00e1\u0192"


CASES = [
    {
        "name": "bachelor_ects",
        "question": "რამდენი ECTS კრედიტია საჭირო საბაკალავრო პროგრამის დასასრულებლად?",
        "expect": {"answer_status": "answered_from_approved_source", "contains": ["240"], "excludes": ["180"], "clarification": False},
    },
    {
        "name": "master_ects",
        "question": "რამდენი კრედიტია სამაგისტრო პროგრამა?",
        "expect": {"answer_status": "answered_from_approved_source", "contains": ["120"], "clarification": False},
    },
    {
        "name": "student_status_5_years",
        "question": "რამდენი წლით შეიძლება სტუდენტის სტატუსის შეჩერება?",
        "expect": {"answer_status": "answered_from_approved_source", "contains": ["5"], "clarification": False},
    },
    {
        "name": "generic_study_clarification",
        "question": "სწავლა მაინტერესებს",
        "expect": {"clarification": True, "contains": ["მიღება", "პროგრამები", "სწავლის საფასური", "სტუდენტის სტატუსი"]},
    },
    {
        "name": "programs_clarification",
        "question": "პროგრამები მაინტერესებს",
        "expect": {"clarification": True, "contains": ["ბაკალავრიატი", "მაგისტრატურა", "მედიცინა/MD", "საერთაშორისო მიღება"]},
    },
    {
        "name": "finance_clarification",
        "question": "გადახდებზე მაინტერესებს",
        "expect": {"clarification": True, "department_key": "finance", "not_department": "international"},
    },
    {
        "name": "status_clarification",
        "question": "სტატუსზე მაქვს კითხვა",
        "expect": {"clarification": True, "contains": ["შეჩერება", "აღდგენა", "შეწყვეტა", "მობილობა"]},
    },
    {
        "name": "library_route",
        "question": "ბიბლიოთეკის რესურსები როგორ გამოვიყენო?",
        "expect": {"department_key": "library", "not_department": "international"},
    },
    {
        "name": "it_support_route",
        "question": "emis.alte.edu.ge-ში ვერ შევდივარ",
        "expect": {"department_key": "it_support"},
    },
    {
        "name": "finance_handover_route",
        "question": "მინდა ფინანსურ დეპარტამენტთან დაკავშირება",
        "expect": {"department_key": "finance", "not_department": "international"},
    },
    {
        "name": "international_medicine",
        "question": "I am an international student and want to apply to Medicine",
        "language": "en",
        "expect": {"department_key_any": ["international", "medicine"], "not_department": "finance"},
    },
    {
        "name": "unsupported_2031_scholarship",
        "question": "2031 წლის კოსმოსური კამპუსის სტიპენდია როგორ მივიღო?",
        "expect": {"answer_status": "no_approved_source_found", "contains": ["დამტკიცებულ წყაროში"], "excludes": ["კოსმოსური კამპუსის სტიპენდია არის"]},
    },
]


def post_json(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        f"{BACKEND_URL}{path}",
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "Origin": ORIGIN,
        },
    )
    with request.urlopen(req, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    session = post_json(
        "/chat/session/start",
        {"source_domain": ORIGIN, "language": case.get("language", "ka"), "widget_variant": "pro_v2_safe"},
    )
    response = post_json(
        "/chat/message",
        {
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": case["question"],
            "source_domain": ORIGIN,
            "language": case.get("language", "ka"),
            "widget_variant": "pro_v2_safe",
        },
    )
    checks = evaluate(case, response)
    return {
        "name": case["name"],
        "question": case["question"],
        "route": response.get("department_key"),
        "source_group": response.get("source_group"),
        "clarification_needed": response.get("clarification_needed"),
        "answer_status": response.get("answer_source_status"),
        "handover_intent": response.get("should_handover"),
        "created_lead_id": response.get("created_lead_id"),
        "created_task_id": response.get("created_task_id"),
        "passed": all(item["passed"] for item in checks),
        "checks": checks,
    }


def evaluate(case: dict[str, Any], response: dict[str, Any]) -> list[dict[str, Any]]:
    expect = case["expect"]
    reply = response.get("reply") or ""
    checks: list[dict[str, Any]] = []
    if "answer_status" in expect:
        checks.append({"name": "answer_status", "passed": response.get("answer_source_status") == expect["answer_status"]})
    if "clarification" in expect:
        checks.append({"name": "clarification", "passed": bool(response.get("clarification_needed")) is expect["clarification"]})
    if "department_key" in expect:
        checks.append({"name": "department_key", "passed": response.get("department_key") == expect["department_key"]})
    if "department_key_any" in expect:
        checks.append({"name": "department_key_any", "passed": response.get("department_key") in expect["department_key_any"]})
    if "not_department" in expect:
        checks.append({"name": "not_department", "passed": response.get("department_key") != expect["not_department"]})
    for value in expect.get("contains", []):
        haystack = reply + "\n" + "\n".join(response.get("clarification_options") or [])
        checks.append({"name": f"contains:{value}", "passed": value in haystack})
    for value in expect.get("excludes", []):
        checks.append({"name": f"excludes:{value}", "passed": value not in reply})
    checks.append({"name": "no_lead_created", "passed": response.get("created_lead_id") is None})
    checks.append({"name": "no_task_created", "passed": response.get("created_task_id") is None})
    checks.append({"name": "no_mojibake", "passed": MOJIBAKE_MARKER not in reply})
    return checks


def write_report(results: list[dict[str, Any]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for item in results if item["passed"])
    lines = [
        "# Phase 9AI Clarification Routing QA Result",
        "",
        f"Backend URL: {BACKEND_URL}",
        f"Origin: {ORIGIN}",
        f"Total: {len(results)}",
        f"Passed: {passed}",
        f"Failed: {len(results) - passed}",
        "No real contact details sent: YES",
        "Lead/task/customer created intentionally: NO",
        "",
        "| Case | Route | Source group | Clarification | Answer status | Result |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in results:
        lines.append(
            f"| {item['name']} | {item.get('route')} | {item.get('source_group')} | "
            f"{item.get('clarification_needed')} | {item.get('answer_status')} | {'PASS' if item['passed'] else 'FAIL'} |"
        )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    results = []
    for case in CASES:
        results.append(run_case(case))
        time.sleep(0.1)
    write_report(results)
    payload = {
        "status": "PASSED" if all(item["passed"] for item in results) else "FAILED",
        "total": len(results),
        "passed": sum(1 for item in results if item["passed"]),
        "failed": sum(1 for item in results if not item["passed"]),
        "report": str(REPORT_PATH),
        "results": results,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(main())
