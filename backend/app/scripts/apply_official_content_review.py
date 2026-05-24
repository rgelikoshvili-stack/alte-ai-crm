from __future__ import annotations

import argparse
import asyncio
import csv
import json
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.models import KnowledgeSnippet, KnowledgeSource


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
CSV_PATH = BACKEND_ROOT / "reports" / "knowledge_review_queue.csv"

ALLOWED_DECISIONS = {"APPROVE", "REWRITE", "ARCHIVE", "HANDOVER_ONLY", "NEEDS_OFFICIAL_SOURCE"}
SENSITIVE_CATEGORIES = {
    "finance",
    "tuition",
    "deadlines",
    "required_documents",
    "international_admissions",
    "medicine",
    "medicine_md",
    "visa",
    "relocation",
    "legal",
}


@dataclass
class ReviewRow:
    source_key: str
    title: str
    category: str
    status: str
    review_required: bool
    recommended_action: str
    decision: str | None


def normalize_decision(value: str | None) -> str | None:
    decision = (value or "").strip().upper()
    if not decision:
        return None
    if decision not in ALLOWED_DECISIONS:
        raise ValueError(f"Invalid reviewer decision: {decision}")
    return decision


def reviewer_decision_column_present(csv_path: Path = CSV_PATH) -> bool:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return "decision" in (reader.fieldnames or [])


def load_review_rows(csv_path: Path = CSV_PATH) -> list[ReviewRow]:
    rows: list[ReviewRow] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            decision = normalize_decision(raw.get("decision"))
            rows.append(
                ReviewRow(
                    source_key=raw.get("source_key", ""),
                    title=raw.get("title", ""),
                    category=(raw.get("category") or "").lower(),
                    status=raw.get("status", ""),
                    review_required=(raw.get("review_required") or "").lower() == "true",
                    recommended_action=(raw.get("recommended_action") or "").upper(),
                    decision=decision,
                )
            )
    return rows


def summarize_rows(
    rows: list[ReviewRow], *, decision_column_present: bool | None = None
) -> dict[str, int | str | bool | list[str]]:
    warnings: list[str] = []
    if decision_column_present is None:
        decision_column_present = reviewer_decision_column_present()
    missing_decisions = sum(1 for row in rows if row.decision is None)
    valid_decisions = len(rows) - missing_decisions
    if not decision_column_present:
        warnings.append("Reviewer decision column missing; recommended_action is not treated as a reviewer decision.")
    if missing_decisions:
        warnings.append("Reviewer decisions missing; --apply should not be run automatically.")
    return {
        "total_rows": len(rows),
        "decision_column_present": decision_column_present,
        "valid_decisions": valid_decisions,
        "missing_decisions": missing_decisions,
        "approve_count": sum(1 for row in rows if row.decision == "APPROVE"),
        "rewrite_count": sum(1 for row in rows if row.decision == "REWRITE"),
        "archive_count": sum(1 for row in rows if row.decision == "ARCHIVE"),
        "handover_only_count": sum(
            1 for row in rows if row.decision == "HANDOVER_ONLY" or row.recommended_action == "HANDOVER_ONLY"
        ),
        "needs_official_source_count": sum(
            1
            for row in rows
            if row.decision == "NEEDS_OFFICIAL_SOURCE" or row.recommended_action == "NEEDS_OFFICIAL_SOURCE"
        ),
        "warnings": warnings,
    }


async def apply_decisions(rows: list[ReviewRow], *, apply: bool) -> dict[str, int | str | bool | list[str]]:
    summary = summarize_rows(rows)
    summary["mode"] = "apply" if apply else "dry-run"
    summary["applied_count"] = 0

    if not apply or summary["valid_decisions"] == 0:
        return summary

    settings = get_settings()
    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured. Set it locally without printing it, then rerun.")

    async with AsyncSessionLocal() as db:
        for row in rows:
            if row.decision is None:
                continue
            snippet = await db.scalar(
                select(KnowledgeSnippet).where(
                    KnowledgeSnippet.source_key == row.source_key,
                    KnowledgeSnippet.title == row.title,
                )
            )
            if not snippet:
                continue
            source = await db.get(KnowledgeSource, snippet.source_id)
            if row.decision == "APPROVE":
                if row.category in SENSITIVE_CATEGORIES:
                    summary["warnings"].append(f"Skipped sensitive approve without separate official source check: {row.title}")
                    continue
                snippet.status = "approved"
                snippet.review_required = False
                if source:
                    source.status = "approved"
                    source.review_required = False
            elif row.decision == "ARCHIVE":
                snippet.status = "archived"
                snippet.review_required = True
            elif row.decision in {"REWRITE", "HANDOVER_ONLY", "NEEDS_OFFICIAL_SOURCE"}:
                snippet.review_required = True
                if snippet.status == "approved":
                    snippet.status = "review_required"
                if source and source.status == "approved":
                    source.status = "review_required"
                    source.review_required = True
            summary["applied_count"] = int(summary["applied_count"]) + 1
        await db.commit()
    return summary


async def _amain() -> int:
    parser = argparse.ArgumentParser(description="Apply official content review decisions safely.")
    parser.add_argument("--dry-run", action="store_true", help="Preview decisions without writing changes. Default mode.")
    parser.add_argument("--apply", action="store_true", help="Apply explicit reviewer decisions.")
    args = parser.parse_args()

    if args.dry_run and args.apply:
        print("FAIL choose only one mode: --dry-run or --apply")
        return 1

    rows = load_review_rows()
    summary = await apply_decisions(rows, apply=args.apply)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(_amain()))


if __name__ == "__main__":
    main()
