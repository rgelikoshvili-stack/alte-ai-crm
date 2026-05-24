from __future__ import annotations

import asyncio
from dataclasses import dataclass

from sqlalchemy import func, select

from app.core.database import AsyncSessionLocal
from app.models import KnowledgeSnippet


SENSITIVE_SOURCE_KEYS = {
    "alte_test_finance_v1",
    "alte_test_deadlines_v1",
    "alte_test_admissions_documents_v1",
    "alte_test_international_admissions_v1",
    "alte_test_medicine_md_v1",
}


@dataclass
class ContentReviewApplyCheck:
    name: str
    passed: bool
    detail: str = ""


async def count_sensitive_fully_approved() -> int:
    async with AsyncSessionLocal() as db:
        result = await db.scalar(
            select(func.count(KnowledgeSnippet.id)).where(
                KnowledgeSnippet.source_key.in_(SENSITIVE_SOURCE_KEYS),
                KnowledgeSnippet.status == "approved",
                KnowledgeSnippet.review_required.is_(False),
            )
        )
        return int(result or 0)


async def count_sensitive_pending_review() -> int:
    async with AsyncSessionLocal() as db:
        result = await db.scalar(
            select(func.count(KnowledgeSnippet.id)).where(
                KnowledgeSnippet.source_key.in_(SENSITIVE_SOURCE_KEYS),
                KnowledgeSnippet.review_required.is_(True),
            )
        )
        return int(result or 0)


async def run_checks() -> list[ContentReviewApplyCheck]:
    sensitive_approved = await count_sensitive_fully_approved()
    sensitive_pending = await count_sensitive_pending_review()
    return [
        ContentReviewApplyCheck(
            "Sensitive categories are not fully approved without explicit review",
            sensitive_approved == 0,
            f"sensitive_fully_approved={sensitive_approved}",
        ),
        ContentReviewApplyCheck(
            "Sensitive seeded content remains pending/review-required",
            sensitive_pending > 0,
            f"sensitive_pending_review={sensitive_pending}",
        ),
    ]


async def _amain() -> int:
    checks = await run_checks()
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"{status} {check.name}: {check.detail}")
    return 1 if any(not check.passed for check in checks) else 0


def main() -> None:
    raise SystemExit(asyncio.run(_amain()))


if __name__ == "__main__":
    main()
