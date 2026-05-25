from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

from app.scripts.prepare_conservative_content_decisions import OUTPUT_PATH, SYSTEM_REVIEWER, text_has_sensitive_claim


ALLOWED_DECISIONS = {"APPROVE", "REWRITE", "ARCHIVE", "HANDOVER_ONLY", "NEEDS_OFFICIAL_SOURCE"}
SENSITIVE_PUBLIC_FORBIDDEN_CATEGORIES = {
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
FORBIDDEN_PATTERNS = [
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
    re.compile(r"DB_PASSWORD\s*=", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"true", "1", "yes", "y"}


def _clean(value: str | None) -> str:
    return str(value or "").strip()


def validate(path: Path = OUTPUT_PATH) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(path)

    text = path.read_text(encoding="utf-8-sig")
    secret_findings = [pattern.pattern for pattern in FORBIDDEN_PATTERNS if pattern.search(text)]

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        rows = list(reader)

    if "decision" not in headers:
        raise ValueError("decision column is required")

    counts: Counter[str] = Counter()
    invalid_decisions: list[str] = []
    high_approved_by_system: list[str] = []
    sensitive_public_allowed_by_system: list[str] = []
    copied_recommendations = 0

    for index, row in enumerate(rows, start=2):
        decision = _clean(row.get("decision"))
        recommended = _clean(row.get("recommended_review_action") or row.get("evidence_recommended_review_action"))
        reviewer = _clean(row.get("reviewer"))
        sensitivity = _clean(row.get("sensitivity")).upper()
        category = _clean(row.get("category")).lower()
        public_allowed = _truthy(row.get("public_launch_allowed"))

        if decision not in ALLOWED_DECISIONS:
            invalid_decisions.append(f"row {index}: {decision}")
        counts[decision] += 1

        if decision and recommended and decision == recommended:
            copied_recommendations += 1

        if sensitivity == "HIGH" and decision == "APPROVE" and reviewer == SYSTEM_REVIEWER:
            high_approved_by_system.append(f"row {index}")

        sensitive_public = (
            sensitivity == "HIGH"
            or category in SENSITIVE_PUBLIC_FORBIDDEN_CATEGORIES
            or text_has_sensitive_claim(row)
        )
        if sensitive_public and public_allowed and reviewer == SYSTEM_REVIEWER:
            sensitive_public_allowed_by_system.append(f"row {index}")

    summary = {
        "path": str(path),
        "total_rows": len(rows),
        "approve_count": counts["APPROVE"],
        "rewrite_count": counts["REWRITE"],
        "archive_count": counts["ARCHIVE"],
        "handover_only_count": counts["HANDOVER_ONLY"],
        "needs_official_source_count": counts["NEEDS_OFFICIAL_SOURCE"],
        "invalid_decisions": len(invalid_decisions),
        "high_approved_by_system": len(high_approved_by_system),
        "sensitive_public_allowed_by_system": len(sensitive_public_allowed_by_system),
        "recommended_review_action_copied_count": copied_recommendations,
        "secret_findings": len(secret_findings),
        "status": "VALID",
    }

    failures = invalid_decisions or high_approved_by_system or sensitive_public_allowed_by_system or secret_findings
    if failures:
        summary["status"] = "INVALID"
        summary["failure_examples"] = {
            "invalid_decisions": invalid_decisions[:5],
            "high_approved_by_system": high_approved_by_system[:5],
            "sensitive_public_allowed_by_system": sensitive_public_allowed_by_system[:5],
            "secret_findings": secret_findings[:5],
        }
    return summary


def main() -> None:
    summary = validate()
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if summary["status"] != "VALID":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
