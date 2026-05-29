from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
QA_PATH = ROOT / "backend" / "app" / "data" / "evaluation" / "alte_official_academic_rules_20_qa.json"
KNOWLEDGE_PATH = ROOT / "backend" / "app" / "data" / "knowledge" / "official_academic_rules_ka_en.json"
REPORT_PATH = ROOT / "docs" / "evaluation" / "ALTE_OFFICIAL_ACADEMIC_RULES_20_QA_EVALUATION_RESULT.md"

REQUIRED_SNIPPETS = {
    "Q01": ["17-22 November", "24-29 November", "1-6 December", "5-10 January"],
    "Q02": ["240 ECTS", "360 ECTS", "300 ECTS"],
    "Q03": ["5 years"],
    "Q04": ["GPA = (X - 50) * 0.06 + 1", "FX and F count as 0"],
    "Q05": ["41-50 points", "additional exam once"],
    "Q06": ["9-14 March"],
    "Q07": ["not earlier than 5 days"],
    "Q08": ["no financial debt", "mandatory/intermediate"],
    "Q09": ["ID card copy", "CV", "3x4", "notarized diploma copy", "diploma supplement copy"],
    "Q10": ["without national exams", "foreign citizens"],
    "Q11": ["A2", "B1", "B2", "C1"],
    "Q12": ["comparing prior completed courses", "transcript", "syllabus"],
    "Q13": ["common master exam", "internal university exam", "logical thinking"],
    "Q14": ["half of the annual tuition fee"],
    "Q15": ["NCEQE", "Ministry decision"],
    "Q16": ["Partial", "additional official source"],
    "Q17": ["Additional official source"],
    "Q18": ["Georgian", "English"],
    "Q19": ["Quality Management and Compliance Department", "Board of Directors"],
    "Q20": ["Additional official source"],
}

ALLOWED_STATUSES = {"ANSWERABLE", "PARTIALLY_ANSWERABLE", "NEEDS_ADDITIONAL_OFFICIAL_SOURCE"}
FORBIDDEN_CONTACT_REQUESTS = [
    "share your phone",
    "share your email",
    "send your phone",
    "send your email",
    "contact details",
    "phone number",
]


@dataclass
class EvalResult:
    qid: str
    expected_status: str
    result: str
    source_used: str
    missing_issue: str
    passed: bool
    notes: str


def load_json(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise AssertionError(f"{path.name} must contain a list")
    return data


def matching_knowledge(qid: str, knowledge_rows: list[dict]) -> list[dict]:
    return [row for row in knowledge_rows if qid in row.get("qa_ids", [])]


def evaluate_item(item: dict, knowledge_rows: list[dict]) -> EvalResult:
    qid = item["id"]
    status = item["expected_status"]
    if status not in ALLOWED_STATUSES:
        return EvalResult(qid, status, "FAIL", "", "unexpected status", False, "Invalid expected_status")

    rows = matching_knowledge(qid, knowledge_rows)
    if not rows:
        return EvalResult(qid, status, "FAIL", "", "knowledge item missing", False, "No local knowledge artifact row")

    combined = " ".join(str(row.get("text", "")) for row in rows)
    combined_lower = combined.lower()
    missing = [snippet for snippet in REQUIRED_SNIPPETS.get(qid, []) if snippet.lower() not in combined_lower]
    forbidden = [phrase for phrase in FORBIDDEN_CONTACT_REQUESTS if phrase.lower() in combined.lower()]
    official = all(row.get("official") is True and row.get("requires_exact_source") is True for row in rows)
    no_crm_creation = not any(word in combined.lower() for word in ["created lead", "created task", "created customer"])

    source_used = "; ".join(sorted({str(row.get("document_title", "")) for row in rows if row.get("document_title")}))
    if missing:
        return EvalResult(qid, status, "FAIL", source_used, ", ".join(missing), False, "Required exact fact missing")
    if forbidden:
        return EvalResult(qid, status, "FAIL", source_used, ", ".join(forbidden), False, "Contact request phrase found")
    if not official:
        return EvalResult(qid, status, "FAIL", source_used, "official source flag missing", False, "Knowledge item lacks official/source flags")
    if not no_crm_creation:
        return EvalResult(qid, status, "FAIL", source_used, "CRM creation phrase found", False, "Evaluation must not create CRM objects")
    if status == "NEEDS_ADDITIONAL_OFFICIAL_SOURCE" and "Additional official source" not in combined:
        return EvalResult(qid, status, "FAIL", source_used, "missing additional-source refusal", False, "Gap answer must refuse to invent")

    return EvalResult(qid, status, "PASS", source_used, "", True, "Meets official-source QA policy")


def write_report(results: list[EvalResult]) -> None:
    lines = [
        "# ALTE Official Academic Rules 20 QA Evaluation Result",
        "",
        "PHASE_9T_OFFICIAL_ACADEMIC_RULES_20_QA_EVALUATION_STATUS="
        + ("PASS" if all(result.passed for result in results) else "FAIL"),
        "",
        "| Question ID | Expected status | Result | Source used | Missing issue | Pass/fail | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(
            "| {qid} | {expected} | {result} | {source} | {missing} | {passfail} | {notes} |".format(
                qid=result.qid,
                expected=result.expected_status,
                result=result.result,
                source=result.source_used.replace("|", "/") or "n/a",
                missing=result.missing_issue.replace("|", "/") or "none",
                passfail="PASS" if result.passed else "FAIL",
                notes=result.notes.replace("|", "/"),
            )
        )
    lines.extend(
        [
            "",
            "## Safety",
            "",
            "- Production DB modified: NO",
            "- Migration run: NO",
            "- Seed run: NO",
            "- Contact details requested: NO",
            "- Lead/task/customer intentionally created: NO",
            "- Public launch: NO-GO",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    qa_items = load_json(QA_PATH)
    knowledge_rows = load_json(KNOWLEDGE_PATH)
    if len(qa_items) != 20:
        raise AssertionError(f"Expected 20 QA items, found {len(qa_items)}")
    results = [evaluate_item(item, knowledge_rows) for item in qa_items]
    write_report(results)
    for result in results:
        print(f"{result.qid}={result.result}")
    passed = sum(1 for result in results if result.passed)
    print(f"OFFICIAL_ACADEMIC_RULES_20_QA_PASS_COUNT={passed}/20")
    print("OFFICIAL_ACADEMIC_RULES_20_QA_STATUS=" + ("PASS" if passed == 20 else "FAIL"))
    return 0 if passed == 20 else 1


if __name__ == "__main__":
    raise SystemExit(main())
