from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
QA_PATH = ROOT / "backend" / "app" / "data" / "evaluation" / "alte_official_academic_rules_30_qa.json"
STRUCTURED_KB = ROOT / "backend" / "app" / "data" / "knowledge" / "official_academic_rules_2025_2026.json"
FULL_CHUNKS = ROOT / "backend" / "app" / "data" / "knowledge" / "official_academic_rules_full_chunks.json"
CALENDAR_JSON = ROOT / "backend" / "app" / "data" / "knowledge" / "academic_calendar_2025_2026_structured.json"
REPORT_PATH = ROOT / "docs" / "evaluation" / "ALTE_OFFICIAL_ACADEMIC_RULES_30_QA_EVALUATION_RESULT.md"

ALLOWED_STATUSES = {"ANSWERABLE", "PARTIALLY_ANSWERABLE", "NEEDS_ADDITIONAL_OFFICIAL_SOURCE"}
FORBIDDEN = [
    "share your phone",
    "share your email",
    "phone number",
    "contact details",
    "created lead",
    "created task",
    "created customer",
]


@dataclass
class EvalResult:
    qid: str
    expected_status: str
    result: str
    expected_source: str
    actual_source: str
    missing_facts: str
    unsupported_claims: str
    passed: bool


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def corpus_text() -> str:
    parts = [
        STRUCTURED_KB.read_text(encoding="utf-8"),
        FULL_CHUNKS.read_text(encoding="utf-8"),
        CALENDAR_JSON.read_text(encoding="utf-8"),
    ]
    return "\n".join(parts)


def detect_source(item: dict, haystack: str) -> str:
    found = [doc for doc in item["expected_source_documents"] if doc in haystack]
    return "; ".join(found) if found else "not found"


def evaluate_item(item: dict, haystack: str) -> EvalResult:
    qid = item["id"]
    status = item["expected_status"]
    if status not in ALLOWED_STATUSES:
        return EvalResult(qid, status, "FAIL", "", "", "invalid expected_status", "", False)

    lower = haystack.lower()
    missing = [value for value in item["required_exact_values"] if value.lower() not in lower]
    forbidden = [phrase for phrase in FORBIDDEN if phrase in lower]
    policy_ok = (
        '"official": true' in lower
        and '"requires_exact_source": true' in lower
        and "conservative_official_source_only" in lower
    )
    source = detect_source(item, haystack)

    if source == "not found":
        return EvalResult(
            qid,
            status,
            "FAIL",
            "; ".join(item["expected_source_documents"]),
            source,
            "expected source document missing",
            "",
            False,
        )
    if missing:
        return EvalResult(
            qid,
            status,
            "FAIL",
            "; ".join(item["expected_source_documents"]),
            source,
            ", ".join(missing),
            "",
            False,
        )
    if forbidden:
        return EvalResult(
            qid,
            status,
            "FAIL",
            "; ".join(item["expected_source_documents"]),
            source,
            "",
            ", ".join(forbidden),
            False,
        )
    if not policy_ok:
        return EvalResult(
            qid,
            status,
            "FAIL",
            "; ".join(item["expected_source_documents"]),
            source,
            "official conservative policy markers missing",
            "",
            False,
        )
    return EvalResult(qid, status, "PASS", "; ".join(item["expected_source_documents"]), source, "none", "none", True)


def write_report(results: list[EvalResult]) -> None:
    passed = sum(1 for result in results if result.passed)
    lines = [
        "# ALTE Official Academic Rules 30 QA Evaluation Result",
        "",
        f"PHASE_9T_OFFICIAL_ACADEMIC_RULES_30_QA_EVALUATION_STATUS={'PASS' if passed == len(results) else 'FAIL'}",
        "",
        f"Final score: {passed}/{len(results)}",
        "",
        "| Question ID | Expected status | Result | Expected source | Actual source | Missing facts | Unsupported claims |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(
            f"| {result.qid} | {result.expected_status} | {result.result} | "
            f"{result.expected_source.replace('|', '/')} | {result.actual_source.replace('|', '/')} | "
            f"{result.missing_facts.replace('|', '/')} | {result.unsupported_claims.replace('|', '/')} |"
        )
    lines.extend(
        [
            "",
            "## Safety",
            "",
            "- Production DB modified by this evaluator: NO",
            "- Migration run: NO",
            "- Seed run: NO",
            "- Contact details requested: NO",
            "- Lead/task/customer intentionally created: NO",
            "- Public launch: NO-GO",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    qa = load_json(QA_PATH)
    if len(qa) != 30:
        raise AssertionError(f"Expected 30 QA items, found {len(qa)}")
    haystack = corpus_text()
    results = [evaluate_item(item, haystack) for item in qa]
    write_report(results)
    for result in results:
        print(f"{result.qid}={result.result}")
    passed = sum(1 for result in results if result.passed)
    print(f"OFFICIAL_ACADEMIC_RULES_30_QA_PASS_COUNT={passed}/30")
    print("OFFICIAL_ACADEMIC_RULES_30_QA_STATUS=" + ("PASS" if passed == 30 else "FAIL"))
    return 0 if passed == 30 else 1


if __name__ == "__main__":
    raise SystemExit(main())
