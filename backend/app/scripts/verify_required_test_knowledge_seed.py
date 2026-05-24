from __future__ import annotations

import asyncio
from dataclasses import dataclass

from sqlalchemy import func, select

from app.core.database import AsyncSessionLocal
from app.models import KnowledgeSnippet, KnowledgeSource


REQUIRED_SOURCE_GROUPS = {
    "general_contact": ["alte_test_contact_v1"],
    "admissions_general": ["alte_test_admissions_general_v1", "alte_test_admissions_documents_v1"],
    "finance": ["alte_test_finance_v1"],
    "international_admissions": ["alte_test_international_admissions_v1"],
    "medicine_md": ["alte_test_medicine_md_v1"],
    "deadlines": ["alte_test_deadlines_v1"],
}

SAFETY_REVIEW_REQUIRED_KEYS = {
    "alte_test_contact_v1",
    "alte_test_admissions_general_v1",
    "alte_test_admissions_documents_v1",
    "alte_test_finance_v1",
    "alte_test_international_admissions_v1",
    "alte_test_medicine_md_v1",
    "alte_test_deadlines_v1",
}


@dataclass
class KnowledgeSeedCheck:
    name: str
    passed: bool
    detail: str = ""


async def count_sources_for_keys(keys: list[str]) -> int:
    async with AsyncSessionLocal() as db:
        result = await db.scalar(select(func.count(KnowledgeSource.id)).where(KnowledgeSource.source_key.in_(keys)))
        return int(result or 0)


async def count_snippets_for_keys(keys: list[str]) -> int:
    async with AsyncSessionLocal() as db:
        result = await db.scalar(select(func.count(KnowledgeSnippet.id)).where(KnowledgeSnippet.source_key.in_(keys)))
        return int(result or 0)


async def count_unsafe_review_required_items() -> int:
    async with AsyncSessionLocal() as db:
        result = await db.scalar(
            select(func.count(KnowledgeSnippet.id)).where(
                KnowledgeSnippet.source_key.in_(SAFETY_REVIEW_REQUIRED_KEYS),
                KnowledgeSnippet.review_required.is_(False),
                KnowledgeSnippet.status != "approved",
            )
        )
        return int(result or 0)


async def run_checks() -> list[KnowledgeSeedCheck]:
    checks: list[KnowledgeSeedCheck] = []
    for group, keys in REQUIRED_SOURCE_GROUPS.items():
        source_count = await count_sources_for_keys(keys)
        snippet_count = await count_snippets_for_keys(keys)
        checks.append(
            KnowledgeSeedCheck(
                f"{group} sources/snippets exist",
                source_count > 0 and snippet_count > 0,
                f"sources={source_count}, snippets={snippet_count}",
            )
        )
    unsafe_count = await count_unsafe_review_required_items()
    checks.append(
        KnowledgeSeedCheck(
            "Uncertain content remains review-required or approved",
            unsafe_count == 0,
            f"unsafe_review_required_count={unsafe_count}",
        )
    )
    return checks


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
