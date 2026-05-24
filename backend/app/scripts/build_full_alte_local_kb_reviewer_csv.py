from __future__ import annotations

import csv
import json
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
NORMALIZED_JSONL = BACKEND_ROOT / "app" / "knowledge_seed" / "full_alte_local_kb" / "full_alte_local_kb_normalized.jsonl"
OUTPUT_CSV = BACKEND_ROOT / "reports" / "full_alte_local_kb_reviewer_decision_queue.csv"

FIELDNAMES = [
    "source_key",
    "source_url",
    "source_file",
    "title",
    "language",
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


def load_records(path: Path = NORMALIZED_JSONL) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Missing normalized KB file: {path}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build_rows(records: list[dict]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in records:
        rows.append(
            {
                "source_key": item.get("source_key", ""),
                "source_url": item.get("source_url", ""),
                "source_file": item.get("source_file", ""),
                "title": item.get("title", ""),
                "language": item.get("language", ""),
                "department": item.get("department", ""),
                "category": item.get("category", ""),
                "section": item.get("section", ""),
                "chunk_index": str(item.get("chunk_index", "")),
                "sensitivity": item.get("sensitivity", ""),
                "review_required": str(bool(item.get("review_required"))).lower(),
                "public_answer_allowed": str(bool(item.get("public_answer_allowed"))).lower(),
                "recommended_review_action": item.get("recommended_review_action", ""),
                "content_preview": preview(item.get("content", "")),
                "decision": "",
                "reviewer": "",
                "review_date": "",
                "reviewer_notes": "",
            }
        )
    return rows


def preview(value: str) -> str:
    compact = " ".join(value.split())
    return compact[:220]


def write_csv(rows: list[dict[str, str]], path: Path = OUTPUT_CSV) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = build_rows(load_records())
    write_csv(rows)
    high = sum(1 for row in rows if row["sensitivity"] == "high")
    print(
        json.dumps(
            {
                "output_path": str(OUTPUT_CSV.relative_to(PROJECT_ROOT)),
                "rows_written": len(rows),
                "high_sensitivity_rows": high,
                "decision_column_left_empty": all(not row["decision"] for row in rows),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
