from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import func, select

from app.core.database import AsyncSessionLocal
from app.models import KnowledgeSnippet, KnowledgeSource


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
SEED_PATH = BACKEND_ROOT / "app" / "knowledge_seed" / "alte_study_docs" / "alte_study_docs_seed_v1.json"
SUMMARY_PATH = BACKEND_ROOT / "reports" / "alte_study_docs_normalization_summary.json"

REQUIRED_KEYS = {
    "alte_study_programs_overview_v1",
    "alte_study_admissions_rules_v1",
    "alte_study_required_documents_v1",
    "alte_study_finance_policy_v1",
    "alte_study_deadline_policy_v1",
    "alte_study_international_admissions_v1",
    "alte_study_medicine_md_v1",
    "alte_study_contact_v1",
    "alte_study_handover_policy_v1",
}

SENSITIVE_CATEGORIES = {
    "finance_tuition",
    "deadlines_calendar",
    "required_documents",
    "international_admissions",
    "medicine_md",
}


@dataclass
class StudyDocsCheck:
    name: str
    passed: bool
    detail: str = ""


def seed_file_exists() -> StudyDocsCheck:
    return StudyDocsCheck("Study docs seed exists", SEED_PATH.exists(), str(SEED_PATH))


def summary_exists() -> StudyDocsCheck:
    return StudyDocsCheck("Study docs summary exists", SUMMARY_PATH.exists(), str(SUMMARY_PATH))


def seed_records_valid() -> StudyDocsCheck:
    if not SEED_PATH.exists():
        return StudyDocsCheck("Study docs seed records valid", False, "missing seed")
    records = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    keys = {record.get("source_key") for record in records}
    missing = sorted(REQUIRED_KEYS.difference(keys))
    unsafe = [
        record["source_key"]
        for record in records
        if record.get("category") in SENSITIVE_CATEGORIES and not record.get("review_required")
    ]
    return StudyDocsCheck(
        "Study docs seed records valid",
        not missing and not unsafe and len(records) >= 10,
        f"records={len(records)}, missing={missing}, unsafe={unsafe}",
    )


async def database_records_exist() -> StudyDocsCheck:
    async with AsyncSessionLocal() as db:
        source_count = await db.scalar(
            select(func.count(KnowledgeSource.id)).where(KnowledgeSource.source_key.in_(REQUIRED_KEYS))
        )
        snippet_count = await db.scalar(
            select(func.count(KnowledgeSnippet.id)).where(KnowledgeSnippet.source_key.in_(REQUIRED_KEYS))
        )
    return StudyDocsCheck(
        "Study docs DB records exist",
        int(source_count or 0) >= len(REQUIRED_KEYS) and int(snippet_count or 0) >= 10,
        f"sources={int(source_count or 0)}, snippets={int(snippet_count or 0)}",
    )


async def sensitive_records_review_required() -> StudyDocsCheck:
    async with AsyncSessionLocal() as db:
        unsafe = await db.scalar(
            select(func.count(KnowledgeSnippet.id)).where(
                KnowledgeSnippet.source_key.in_(REQUIRED_KEYS),
                KnowledgeSnippet.category.in_(SENSITIVE_CATEGORIES),
                KnowledgeSnippet.review_required.is_(False),
            )
        )
    return StudyDocsCheck(
        "Sensitive study docs remain review-required",
        int(unsafe or 0) == 0,
        f"unsafe={int(unsafe or 0)}",
    )


async def run_checks() -> list[StudyDocsCheck]:
    checks = [seed_file_exists(), summary_exists(), seed_records_valid()]
    checks.append(await database_records_exist())
    checks.append(await sensitive_records_review_required())
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
