from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from app.services.chat_service import clean_public_answer_text
from app.services.claude_intent_router_service import fallback_intent_route


FORBIDDEN_PUBLIC_MARKERS = [
    "official_academic_rules_full",
    "source_group",
    "Policy:",
    "Reference:",
    "Official source:",
    "answer only from",
    "handover if",
    "chunk",
    "p022_c050",
]

SOURCE_MAP_PATH = Path(__file__).resolve().parents[1] / "data" / "knowledge" / "global_source_map.json"


@dataclass(frozen=True)
class QAItem:
    file_id: str
    category: str
    question: str
    expected_type: str
    expected_source_group: str | None = None
    expected_department: str | None = None
    validator: Callable[[object], bool] | None = None


@dataclass
class QAResult:
    item: QAItem
    result: str
    root_cause: str
    notes: str


PROGRAM_CATALOG_SAMPLE: list[QAItem] = [
    QAItem(
        file_id="program_catalog",
        category="main",
        question="რამდენი საგანმანათლებლო პროგრამა აქვს ალტე უნივერსიტეტს სულ?",
        expected_type="exact",
        expected_source_group="program_catalog_sources",
        expected_department="programs",
    ),
    QAItem(
        file_id="program_catalog",
        category="clarification",
        question="რამდენი კრედიტია პროგრამა?",
        expected_type="clarification",
    ),
    QAItem(
        file_id="program_catalog",
        category="unsupported",
        question="2031 წლის კოსმოსური კამპუსის პროგრამაზე რა მოთხოვნებია?",
        expected_type="unsupported",
    ),
]

GLOBAL_PRIORITY_SAMPLE: list[QAItem] = [
    QAItem(
        file_id="admissions_rules",
        category="priority",
        question="ეროვნული გამოცდების გარეშე ჩარიცხვა",
        expected_type="exact",
        expected_source_group="admissions_rules",
        expected_department="admissions",
    ),
    QAItem(
        file_id="exam_regulation",
        category="priority",
        question="დასკვნით გამოცდაზე დაშვების წესი როგორია?",
        expected_type="exact",
        expected_source_group="exams_and_assessment",
        expected_department="study_process",
    ),
    QAItem(
        file_id="academic_calendar",
        category="priority",
        question="დასკვნითი გამოცდები როდის არის?",
        expected_type="exact",
        expected_source_group="academic_calendar_2025_2026",
        expected_department="academic_calendar",
    ),
    QAItem(
        file_id="exam_regulation",
        category="clarification",
        question="გამოცდებზე მაინტერესებს",
        expected_type="clarification",
    ),
]


def _answer_is_clean(text: str) -> bool:
    cleaned = clean_public_answer_text(text)
    haystack = cleaned.lower()
    return all(marker.lower() not in haystack for marker in FORBIDDEN_PUBLIC_MARKERS)


def evaluate_item(item: QAItem) -> QAResult:
    route = fallback_intent_route(item.question)
    if not _answer_is_clean(f"სატესტო პასუხი. source_group=debug chunk 2 {item.question}"):
        return QAResult(item, "FAIL", "source_label_noise_issue", "answer sanitizer did not remove internal labels")

    if item.expected_type == "clarification":
        passed = route.needs_clarification and route.source_groups_to_search == [] and not route.operator_needed
        return QAResult(
            item,
            "PASS" if passed else "FAIL",
            "clarification_missing" if not passed else "none",
            f"clarification={route.needs_clarification}; groups={route.source_groups_to_search}",
        )

    if item.expected_type == "unsupported":
        passed = route.unsupported_likely and route.source_groups_to_search == [] and not route.operator_needed
        return QAResult(
            item,
            "PASS" if passed else "FAIL",
            "unsupported_false_positive" if not passed else "none",
            f"unsupported={route.unsupported_likely}; groups={route.source_groups_to_search}",
        )

    expected_group = item.expected_source_group
    expected_department = item.expected_department
    passed = (
        bool(route.source_groups_to_search)
        and route.source_groups_to_search[0] == expected_group
        and (expected_department is None or route.department == expected_department)
        and not route.operator_needed
        and not route.unsupported_likely
    )
    return QAResult(
        item,
        "PASS" if passed else "FAIL",
        "wrong_source" if not passed else "none",
        f"department={route.department}; groups={route.source_groups_to_search}",
    )


def run_qa_set(items: list[QAItem]) -> list[QAResult]:
    return [evaluate_item(item) for item in items]


def blocked_source_entries() -> list[str]:
    data = json.loads(SOURCE_MAP_PATH.read_text(encoding="utf-8"))
    return [
        item["source_id"]
        for item in data.get("sources", [])
        if item.get("routable") is False or item.get("qa_ready") is False
    ]


def summarize(results: list[QAResult]) -> dict[str, object]:
    blocked = blocked_source_entries()
    summary = {
        "total": len(results),
        "PASS": sum(1 for item in results if item.result == "PASS"),
        "PARTIAL": sum(1 for item in results if item.result == "PARTIAL"),
        "FAIL": sum(1 for item in results if item.result == "FAIL"),
        "BLOCKED_CONFIG_GAP": len(blocked),
        "blocked_sources": blocked,
        "root_causes": {},
        "safety": {
            "lead_customer_task_created": False,
            "contact_flow_submitted": False,
            "public_launch": "NO-GO",
        },
    }
    root_causes: dict[str, int] = {}
    for result in results:
        if result.root_cause != "none":
            root_causes[result.root_cause] = root_causes.get(result.root_cause, 0) + 1
    summary["root_causes"] = root_causes
    return summary


def main() -> int:
    results = run_qa_set(PROGRAM_CATALOG_SAMPLE + GLOBAL_PRIORITY_SAMPLE)
    summary = summarize(results)
    for result in results:
        print(f"{result.result}: {result.item.file_id} | {result.item.question} | {result.notes}")
    print(
        "SUMMARY: "
        f"total={summary['total']} PASS={summary['PASS']} PARTIAL={summary['PARTIAL']} "
        f"FAIL={summary['FAIL']} BLOCKED_CONFIG_GAP={summary['BLOCKED_CONFIG_GAP']}"
    )
    if summary["blocked_sources"]:
        print("BLOCKED: " + ", ".join(summary["blocked_sources"]))
    print("SAFETY: no lead/customer/task; no contact flow; public launch NO-GO")
    return 0 if summary["FAIL"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
