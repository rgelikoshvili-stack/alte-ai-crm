from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
REVIEW_CSV = PROJECT_ROOT / "docs" / "reviewer_package" / "alte_kb_human_review_decisions.csv"
ALLOWED_DECISIONS = {"", "APPROVE", "REWRITE", "ARCHIVE", "HANDOVER_ONLY", "NEEDS_OFFICIAL_SOURCE"}
SECRET_PATTERNS = [
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
    re.compile(r"DB_PASSWORD\s*=", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]


@dataclass
class ValidationResult:
    total_rows: int
    empty_decisions: int
    approve_count: int
    rewrite_count: int
    archive_count: int
    handover_only_count: int
    needs_official_source_count: int
    invalid_decisions: list[str]
    approve_without_reviewer: int
    approve_without_review_date: int
    high_approved_without_notes: int
    recommended_action_copied_to_decision: int
    forbidden_secret_findings: list[str]

    @property
    def status(self) -> str:
        if self.has_errors:
            return "INVALID_REVIEWER_DECISIONS"
        if self.empty_decisions == self.total_rows:
            return "PENDING_HUMAN_DECISIONS"
        return "VALID_REVIEWER_DECISIONS"

    @property
    def has_errors(self) -> bool:
        return bool(
            self.invalid_decisions
            or self.approve_without_reviewer
            or self.approve_without_review_date
            or self.high_approved_without_notes
            or self.recommended_action_copied_to_decision
            or self.forbidden_secret_findings
        )


def read_rows() -> tuple[list[str], list[dict[str, str]]]:
    if not REVIEW_CSV.exists():
        raise FileNotFoundError(f"Reviewer package CSV not found: {REVIEW_CSV}")
    with REVIEW_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def validate() -> ValidationResult:
    headers, rows = read_rows()
    if "decision" not in headers:
        return ValidationResult(0, 0, 0, 0, 0, 0, 0, ["MISSING_DECISION_COLUMN"], 0, 0, 0, 0, [])

    decisions = [(row.get("decision") or "").strip() for row in rows]
    invalid = sorted({decision for decision in decisions if decision not in ALLOWED_DECISIONS})
    findings: list[str] = []
    text = REVIEW_CSV.read_text(encoding="utf-8-sig")
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            findings.append(pattern.pattern)

    return ValidationResult(
        total_rows=len(rows),
        empty_decisions=sum(1 for decision in decisions if not decision),
        approve_count=decisions.count("APPROVE"),
        rewrite_count=decisions.count("REWRITE"),
        archive_count=decisions.count("ARCHIVE"),
        handover_only_count=decisions.count("HANDOVER_ONLY"),
        needs_official_source_count=decisions.count("NEEDS_OFFICIAL_SOURCE"),
        invalid_decisions=invalid,
        approve_without_reviewer=sum(1 for row in rows if row.get("decision") == "APPROVE" and not (row.get("reviewer") or "").strip()),
        approve_without_review_date=sum(1 for row in rows if row.get("decision") == "APPROVE" and not (row.get("review_date") or "").strip()),
        high_approved_without_notes=sum(
            1
            for row in rows
            if row.get("decision") == "APPROVE"
            and (row.get("sensitivity") or "").upper() == "HIGH"
            and not (row.get("reviewer_notes") or "").strip()
        ),
        recommended_action_copied_to_decision=sum(
            1
            for row in rows
            if (row.get("decision") or "").strip()
            and (row.get("decision") or "").strip() == (row.get("recommended_review_action") or "").strip()
        ),
        forbidden_secret_findings=findings,
    )


def main() -> None:
    result = validate()
    print(f"status: {result.status}")
    print(f"total_rows: {result.total_rows}")
    print(f"empty_decisions: {result.empty_decisions}")
    print(f"approve_count: {result.approve_count}")
    print(f"rewrite_count: {result.rewrite_count}")
    print(f"archive_count: {result.archive_count}")
    print(f"handover_only_count: {result.handover_only_count}")
    print(f"needs_official_source_count: {result.needs_official_source_count}")
    print(f"invalid_decisions: {len(result.invalid_decisions)}")
    print(f"high_approved_without_notes: {result.high_approved_without_notes}")
    if result.has_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
