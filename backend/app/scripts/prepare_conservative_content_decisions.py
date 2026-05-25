from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

SOURCE_CANDIDATES = [
    PROJECT_ROOT / "docs" / "reviewer_package" / "alte_kb_human_review_decisions.csv",
    BACKEND_ROOT / "reports" / "full_alte_local_kb_reviewer_decision_queue.csv",
    BACKEND_ROOT / "reports" / "full_alte_kb_reviewer_decision_queue.csv",
    BACKEND_ROOT / "reports" / "knowledge_review_queue_for_review_with_evidence.csv",
    BACKEND_ROOT / "reports" / "knowledge_review_queue_for_review.csv",
]
OUTPUT_PATH = PROJECT_ROOT / "docs" / "reviewer_package" / "alte_kb_conservative_decisions_for_approval.csv"

SYSTEM_REVIEWER = "SYSTEM_CONSERVATIVE_DRAFT"
APPROVAL_BASIS = "Conservative default, pending official reviewer approval"

SENSITIVE_CATEGORIES = {
    "finance_tuition",
    "deadlines_calendar",
    "required_documents",
    "medicine_md",
    "dentistry",
    "international_admissions",
    "visa_relocation",
    "legal",
    "scholarship",
    "grant",
    "payment",
}
LOW_RISK_CATEGORIES = {"general_contact", "about", "faq", "student_services"}
OFFICIAL_DOMAINS = ("alte.edu.ge", "join.alte.edu.ge")

SENSITIVE_TERMS = [
    "tuition",
    "fee",
    "fees",
    "price",
    "scholarship",
    "grant",
    "payment",
    "deadline",
    "intake",
    "required document",
    "documents",
    "medicine",
    "md",
    "dentistry",
    "international",
    "visa",
    "relocation",
    "legal",
    "საფას",
    "ფასი",
    "გრანტ",
    "სტიპენდ",
    "გადახდ",
    "ვადა",
    "საბუთ",
    "დოკუმენტ",
    "მედიც",
    "სტომატოლოგ",
    "საერთაშორისო",
    "ვიზა",
    "რელოკ",
]


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"true", "1", "yes", "y"}


def _clean(value: str | None) -> str:
    return str(value or "").strip()


def select_source_file() -> Path:
    for candidate in SOURCE_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("No reviewer decision CSV found")


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def is_official_source(row: dict[str, str]) -> bool:
    source_url = _clean(row.get("source_url")).lower()
    return any(domain in source_url for domain in OFFICIAL_DOMAINS)


def text_has_sensitive_claim(row: dict[str, str]) -> bool:
    text = " ".join(
        [
            _clean(row.get("category")),
            _clean(row.get("department")),
            _clean(row.get("title")),
            _clean(row.get("section")),
            _clean(row.get("content_preview")),
        ]
    ).lower()
    return any(term in text for term in SENSITIVE_TERMS)


def conservative_decision(row: dict[str, str]) -> tuple[str, bool, str]:
    category = _clean(row.get("category")).lower()
    sensitivity = _clean(row.get("sensitivity")).upper()
    review_required = _truthy(row.get("review_required"))
    official_source = is_official_source(row)
    sensitive_claim = text_has_sensitive_claim(row)

    if sensitivity == "HIGH" or category in SENSITIVE_CATEGORIES or sensitive_claim:
        if category in {"visa_relocation", "legal"} or "visa" in category or "legal" in category:
            return "HANDOVER_ONLY", False, "Sensitive official/legal content requires human handover or explicit official approval."
        return "NEEDS_OFFICIAL_SOURCE", False, "Sensitive official content requires human/official approval."

    if sensitivity == "MEDIUM":
        if official_source and not review_required and not sensitive_claim and category in LOW_RISK_CATEGORIES:
            return "APPROVE", True, "Low-risk official-source-backed non-sensitive content approved as conservative draft."
        return "NEEDS_OFFICIAL_SOURCE", False, "Medium-risk content remains pending official reviewer approval."

    if sensitivity == "LOW":
        if official_source and not review_required and not sensitive_claim:
            return "APPROVE", True, "Low-risk official-source-backed non-sensitive content approved as conservative draft."
        return "NEEDS_OFFICIAL_SOURCE", False, "Low-risk content lacks enough safe official-source evidence for automatic public launch."

    return "NEEDS_OFFICIAL_SOURCE", False, "Unclear sensitivity; conservative default pending official reviewer approval."


def ensure_columns(headers: list[str]) -> list[str]:
    output_headers = list(headers)
    for column in ["decision", "reviewer", "review_date", "reviewer_notes", "approval_basis", "public_launch_allowed"]:
        if column not in output_headers:
            output_headers.append(column)
    return output_headers


def build_decisions(source_path: Path | None = None, output_path: Path = OUTPUT_PATH) -> dict[str, object]:
    source = source_path or select_source_file()
    headers, rows = read_rows(source)
    output_headers = ensure_columns(headers)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    decision_counts: Counter[str] = Counter()
    high_sensitivity_count = 0
    sensitive_blocked_count = 0
    public_launch_allowed_count = 0

    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_headers)
        writer.writeheader()
        for row in rows:
            sensitivity = _clean(row.get("sensitivity")).upper()
            decision, public_allowed, notes = conservative_decision(row)

            if sensitivity == "HIGH":
                high_sensitivity_count += 1
            if sensitivity == "HIGH" or decision in {"HANDOVER_ONLY", "NEEDS_OFFICIAL_SOURCE"}:
                sensitive_blocked_count += 1
            if public_allowed:
                public_launch_allowed_count += 1

            row["decision"] = decision
            row["reviewer"] = SYSTEM_REVIEWER
            row["review_date"] = ""
            row["reviewer_notes"] = notes
            row["approval_basis"] = APPROVAL_BASIS
            row["public_launch_allowed"] = "true" if public_allowed else "false"
            decision_counts[decision] += 1
            writer.writerow({header: row.get(header, "") for header in output_headers})

    summary = {
        "source_path": str(source.relative_to(PROJECT_ROOT)),
        "output_path": str(output_path.relative_to(PROJECT_ROOT)),
        "total_rows": len(rows),
        "approve_count": decision_counts["APPROVE"],
        "rewrite_count": decision_counts["REWRITE"],
        "archive_count": decision_counts["ARCHIVE"],
        "handover_only_count": decision_counts["HANDOVER_ONLY"],
        "needs_official_source_count": decision_counts["NEEDS_OFFICIAL_SOURCE"],
        "public_launch_allowed_count": public_launch_allowed_count,
        "high_sensitivity_count": high_sensitivity_count,
        "sensitive_blocked_count": sensitive_blocked_count,
    }
    return summary


def main() -> None:
    summary = build_decisions()
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
