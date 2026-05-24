from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import func, select

from app.core.database import AsyncSessionLocal
from app.models import KnowledgeSnippet, KnowledgeSource


BACKEND_ROOT = Path(__file__).resolve().parents[2]
NORMALIZED_JSONL = BACKEND_ROOT / "app" / "knowledge_seed" / "full_alte_local_kb" / "full_alte_local_kb_normalized.jsonl"
SUMMARY_JSON = BACKEND_ROOT / "reports" / "full_alte_local_kb_normalization_summary.json"
REVIEWER_CSV = BACKEND_ROOT / "reports" / "full_alte_local_kb_reviewer_decision_queue.csv"
SENSITIVE_CATEGORIES = {
    "finance_tuition",
    "deadlines_calendar",
    "required_documents",
    "international_admissions",
    "medicine_md",
    "dentistry",
    "visa_relocation",
}


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def load_records() -> list[dict]:
    return [json.loads(line) for line in NORMALIZED_JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]


def verify_files() -> list[Check]:
    checks = [
        Check("Normalized JSONL exists", NORMALIZED_JSONL.exists(), str(NORMALIZED_JSONL)),
        Check("Normalization summary exists", SUMMARY_JSON.exists(), str(SUMMARY_JSON)),
        Check("Reviewer CSV exists", REVIEWER_CSV.exists(), str(REVIEWER_CSV)),
    ]
    if not NORMALIZED_JSONL.exists():
        return checks
    records = load_records()
    checks.extend(
        [
            Check("Normalized records >= 600", len(records) >= 600, f"count={len(records)}"),
            Check(
                "High sensitivity exists",
                any(item.get("sensitivity") == "high" for item in records),
                f"count={sum(1 for item in records if item.get('sensitivity') == 'high')}",
            ),
            Check(
                "Review required exists",
                any(item.get("review_required") for item in records),
                f"count={sum(1 for item in records if item.get('review_required'))}",
            ),
            Check(
                "Sensitive categories review_required",
                all(item.get("review_required") for item in records if item.get("category") in SENSITIVE_CATEGORIES),
            ),
            Check(
                "Sensitive categories not public-approved",
                all(not item.get("public_answer_allowed") for item in records if item.get("category") in SENSITIVE_CATEGORIES),
            ),
        ]
    )
    return checks


async def verify_db() -> list[Check]:
    if not os.environ.get("DATABASE_URL"):
        return [Check("DATABASE_URL not set; DB verification skipped", True, "file-only verification")]
    async with AsyncSessionLocal() as db:
        source_count = await db.scalar(
            select(func.count(KnowledgeSource.id)).where(KnowledgeSource.source_type == "full_alte_local_kb")
        )
        snippet_count = await db.scalar(
            select(func.count(KnowledgeSnippet.id)).where(KnowledgeSnippet.source_key.like("full_alte_local_kb_%"))
        )
        unsafe_sensitive = await db.scalar(
            select(func.count(KnowledgeSnippet.id)).where(
                KnowledgeSnippet.source_key.like("full_alte_local_kb_%"),
                KnowledgeSnippet.category.in_(SENSITIVE_CATEGORIES),
                KnowledgeSnippet.review_required.is_(False),
            )
        )
    return [
        Check("DB full local KB sources exist", int(source_count or 0) >= 100, f"count={source_count}"),
        Check("DB full local KB snippets exist", int(snippet_count or 0) >= 600, f"count={snippet_count}"),
        Check("DB sensitive snippets remain review_required", int(unsafe_sensitive or 0) == 0, f"unsafe={unsafe_sensitive}"),
    ]


async def run_checks() -> list[Check]:
    return [*verify_files(), *(await verify_db())]


async def _amain() -> int:
    checks = await run_checks()
    for check in checks:
        print(f"{'PASS' if check.passed else 'FAIL'} {check.name}: {check.detail}")
    return 1 if any(not check.passed for check in checks) else 0


def main() -> None:
    raise SystemExit(asyncio.run(_amain()))


if __name__ == "__main__":
    main()
