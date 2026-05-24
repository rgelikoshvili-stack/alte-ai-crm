from __future__ import annotations

import csv
import json
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = BACKEND_ROOT / "reports"
INPUT_PATH = REPORTS_DIR / "knowledge_review_queue.csv"
OUTPUT_PATH = REPORTS_DIR / "knowledge_review_queue_for_review.csv"

ALLOWED_DECISIONS = ["APPROVE", "REWRITE", "ARCHIVE", "HANDOVER_ONLY", "NEEDS_OFFICIAL_SOURCE"]
REVIEWER_COLUMNS = ["decision", "reviewer", "review_date", "reviewer_notes"]
HELPER_COLUMNS = ["allowed_decisions", "decision_guidance"]

SENSITIVE_GUIDANCE = {
    "finance": "Default to NEEDS_OFFICIAL_SOURCE or HANDOVER_ONLY. Do not approve tuition/fees without official source.",
    "tuition": "Default to NEEDS_OFFICIAL_SOURCE or HANDOVER_ONLY. Do not approve tuition/fees without official source.",
    "deadlines": "Default to NEEDS_OFFICIAL_SOURCE or HANDOVER_ONLY. Do not approve deadlines without official source.",
    "required_documents": "Default to NEEDS_OFFICIAL_SOURCE. Do not approve document requirements without official source.",
    "international_admissions": "Default to NEEDS_OFFICIAL_SOURCE. International admissions requirements need official review.",
    "medicine": "Default to NEEDS_OFFICIAL_SOURCE. Medicine/MD requirements need official review.",
    "medicine_md": "Default to NEEDS_OFFICIAL_SOURCE. Medicine/MD requirements need official review.",
    "visa": "Default to HANDOVER_ONLY. Visa/legal/relocation wording needs official approval.",
    "relocation": "Default to HANDOVER_ONLY. Visa/legal/relocation wording needs official approval.",
    "legal": "Default to HANDOVER_ONLY. Legal-sensitive wording needs official approval.",
}


def decision_guidance_for(row: dict[str, str]) -> str:
    category = (row.get("category") or "").strip().lower()
    source_key = (row.get("source_key") or "").strip().lower()
    title = (row.get("title") or "").strip().lower()
    haystack = f"{category} {source_key} {title}"

    for key, guidance in SENSITIVE_GUIDANCE.items():
        if key in haystack:
            return guidance
    if "contact" in haystack:
        return "APPROVE only if official contact source is confirmed. If unsure, choose NEEDS_OFFICIAL_SOURCE."
    if "admission" in haystack:
        return "APPROVE only if official admissions source is confirmed. If unsure, choose NEEDS_OFFICIAL_SOURCE."
    return "Choose APPROVE only for official reviewed wording. If unsure, choose NEEDS_OFFICIAL_SOURCE."


def output_headers(input_headers: list[str]) -> list[str]:
    headers = [header for header in input_headers if header not in REVIEWER_COLUMNS + HELPER_COLUMNS]
    return headers + REVIEWER_COLUMNS + HELPER_COLUMNS


def prepare_reviewer_csv(input_path: Path = INPUT_PATH, output_path: Path = OUTPUT_PATH) -> dict[str, object]:
    warnings: list[str] = []
    if not input_path.exists():
        raise FileNotFoundError(f"Input review queue not found: {input_path}")

    with input_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        input_headers = reader.fieldnames or []
        rows = list(reader)

    if "recommended_action" not in input_headers:
        warnings.append("recommended_action column missing from source queue.")
    if "decision" in input_headers:
        warnings.append("source queue already has a decision column; output decisions are still reset for reviewer ownership.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    headers = output_headers(input_headers)
    allowed = "|".join(ALLOWED_DECISIONS)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            output_row = {header: row.get(header, "") for header in input_headers if header in headers}
            output_row["decision"] = ""
            output_row["reviewer"] = ""
            output_row["review_date"] = ""
            output_row["reviewer_notes"] = ""
            output_row["allowed_decisions"] = allowed
            output_row["decision_guidance"] = decision_guidance_for(row)
            writer.writerow(output_row)

    return {
        "input_path": str(input_path),
        "output_path": str(output_path),
        "rows_written": len(rows),
        "decision_column_added": True,
        "warnings": warnings,
    }


def main() -> None:
    summary = prepare_reviewer_csv()
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
