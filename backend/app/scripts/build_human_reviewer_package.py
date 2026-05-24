from __future__ import annotations

import csv
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
SOURCE_CSV = BACKEND_ROOT / "reports" / "full_alte_local_kb_reviewer_decision_queue.csv"
PACKAGE_DIR = PROJECT_ROOT / "docs" / "reviewer_package"
DECISIONS_CSV = PACKAGE_DIR / "alte_kb_human_review_decisions.csv"
COMPACT_CSV = PACKAGE_DIR / "alte_kb_human_review_compact.csv"

SENSITIVE_P1_CATEGORIES = {
    "finance_tuition",
    "deadlines_calendar",
    "required_documents",
    "medicine_md",
    "international_admissions",
    "visa_relocation",
    "accreditation",
    "legal",
    "legal_sensitive",
}
P2_CATEGORIES = {"admissions_general", "program_overview", "student_services", "bachelor_admissions", "master_admissions"}
FINAL_COLUMNS = [
    "review_priority",
    "source_key",
    "source_url",
    "title",
    "locale",
    "department",
    "category",
    "section",
    "chunk_index",
    "sensitivity",
    "review_required",
    "public_answer_allowed",
    "recommended_review_action",
    "content_preview",
    "decision",
    "reviewer",
    "review_date",
    "reviewer_notes",
]
COMPACT_COLUMNS = [
    "review_priority",
    "department",
    "category",
    "title",
    "source_url",
    "sensitivity",
    "recommended_review_action",
    "content_preview",
    "decision",
    "reviewer_notes",
]


def review_priority(row: dict[str, str]) -> str:
    category = (row.get("category") or "").strip()
    sensitivity = (row.get("sensitivity") or "").strip().upper()
    if sensitivity == "HIGH" or category in SENSITIVE_P1_CATEGORIES:
        return "P1"
    if sensitivity == "MEDIUM" or category in P2_CATEGORIES:
        return "P2"
    return "P3"


def normalized_row(row: dict[str, str]) -> dict[str, str]:
    preview = (row.get("content_preview") or "").replace("\r\n", " ").replace("\n", " ").strip()
    if len(preview) > 300:
        preview = preview[:297].rstrip() + "..."
    return {
        "review_priority": review_priority(row),
        "source_key": row.get("source_key", ""),
        "source_url": row.get("source_url", ""),
        "title": row.get("title", ""),
        "locale": row.get("locale") or row.get("language", ""),
        "department": row.get("department", ""),
        "category": row.get("category", ""),
        "section": row.get("section", ""),
        "chunk_index": row.get("chunk_index", ""),
        "sensitivity": row.get("sensitivity", ""),
        "review_required": row.get("review_required", ""),
        "public_answer_allowed": row.get("public_answer_allowed", ""),
        "recommended_review_action": row.get("recommended_review_action", ""),
        "content_preview": preview,
        "decision": "",
        "reviewer": "",
        "review_date": "",
        "reviewer_notes": "",
    }


def sort_key(row: dict[str, str]) -> tuple[int, int, int, str, str, str]:
    priority_order = {"P1": 0, "P2": 1, "P3": 2}
    high_first = 0 if (row.get("sensitivity") or "").upper() == "HIGH" else 1
    review_first = 0 if (row.get("review_required") or "").lower() == "true" else 1
    category_first = 0 if row.get("category") in SENSITIVE_P1_CATEGORIES else 1
    return (
        priority_order.get(row.get("review_priority", "P3"), 3),
        high_first,
        review_first,
        category_first,
        row.get("department", ""),
        row.get("category", ""),
        row.get("title", ""),
    )


def read_source_rows() -> list[dict[str, str]]:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"Source reviewer queue not found: {SOURCE_CSV}")
    with SOURCE_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    tmp_path.replace(path)


def build_package() -> dict[str, int | str]:
    source_rows = read_source_rows()
    final_rows = sorted((normalized_row(row) for row in source_rows), key=sort_key)
    compact_rows = [{column: row.get(column, "") for column in COMPACT_COLUMNS} for row in final_rows]
    write_csv(DECISIONS_CSV, FINAL_COLUMNS, final_rows)
    write_csv(COMPACT_CSV, COMPACT_COLUMNS, compact_rows)
    return {
        "source_rows": len(source_rows),
        "decision_rows": len(final_rows),
        "compact_rows": len(compact_rows),
        "high_sensitivity": sum(1 for row in final_rows if row.get("sensitivity", "").upper() == "HIGH"),
        "review_required": sum(1 for row in final_rows if row.get("review_required", "").lower() == "true"),
        "decision_column_filled": sum(1 for row in final_rows if row.get("decision")),
        "output_decisions": str(DECISIONS_CSV),
        "output_compact": str(COMPACT_CSV),
    }


def main() -> None:
    summary = build_package()
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
