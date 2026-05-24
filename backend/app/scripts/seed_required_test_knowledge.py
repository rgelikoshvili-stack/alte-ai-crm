from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.models import KnowledgeSnippet, KnowledgeSource


SEED_PATH = Path(__file__).resolve().parents[1] / "knowledge_seed" / "alte_required_test_knowledge_v1.json"


def _is_production_environment() -> bool:
    settings = get_settings()
    return settings.ENVIRONMENT.lower().strip() == "production"


async def seed_required_test_knowledge(
    seed_path: Path = SEED_PATH,
    *,
    allow_production: bool = False,
) -> dict[str, int | list[str]]:
    if _is_production_environment() and not allow_production:
        return {
            "sources_created": 0,
            "snippets_created": 0,
            "skipped_existing": 0,
            "review_required_count": 0,
            "warnings": [
                "Refusing to seed production without --allow-production. Review content first and rerun only after approval."
            ],
        }

    data = json.loads(seed_path.read_text(encoding="utf-8"))
    summary: dict[str, int | list[str]] = {
        "sources_created": 0,
        "snippets_created": 0,
        "skipped_existing": 0,
        "review_required_count": sum(1 for item in data if item.get("review_required")),
        "warnings": [],
    }

    async with AsyncSessionLocal() as db:
        for entry in data:
            source = await get_or_create_source(db, entry, summary)
            content_hash = hash_content(entry)
            existing = await db.scalar(
                select(KnowledgeSnippet).where(
                    KnowledgeSnippet.source_id == source.id,
                    KnowledgeSnippet.content_hash == content_hash,
                )
            )
            if existing:
                summary["skipped_existing"] = int(summary["skipped_existing"]) + 1
                continue

            db.add(
                KnowledgeSnippet(
                    source_id=source.id,
                    source_key=entry.get("source_key"),
                    title=entry["title"],
                    content=entry["content"],
                    category=entry["category"],
                    source_domain=entry.get("source_domain"),
                    sensitivity=entry.get("sensitivity", "low"),
                    review_required=bool(entry.get("review_required", False)),
                    stale_after_days=entry.get("stale_after_days"),
                    content_hash=content_hash,
                    program_name=entry.get("program_name"),
                    keywords=keywords_to_text(entry.get("keywords")),
                    status=entry.get("status", "review_required"),
                    language=entry["language"],
                )
            )
            summary["snippets_created"] = int(summary["snippets_created"]) + 1

        await db.commit()
    return summary


async def get_or_create_source(db, entry: dict[str, Any], summary: dict[str, int | list[str]]) -> KnowledgeSource:
    source = await db.scalar(
        select(KnowledgeSource).where(
            KnowledgeSource.source_key == entry.get("source_key"),
            KnowledgeSource.language == entry["language"],
            KnowledgeSource.category == entry["category"],
        )
    )
    if source:
        changed = False
        if entry.get("status") and source.status != entry["status"]:
            source.status = entry["status"]
            changed = True
        if source.review_required != bool(entry.get("review_required", False)):
            source.review_required = bool(entry.get("review_required", False))
            changed = True
        if changed:
            await db.flush()
        return source

    source = KnowledgeSource(
        source_key=entry.get("source_key"),
        title=f"{entry['source_key']} ({entry['language']}, {entry['category']})",
        source_type="manual",
        status=entry.get("status", "review_required"),
        language=entry["language"],
        source_url=entry.get("source_url"),
        source_domain=entry.get("source_domain"),
        category=entry["category"],
        sensitivity=entry.get("sensitivity", "low"),
        review_required=bool(entry.get("review_required", False)),
        stale_after_days=entry.get("stale_after_days"),
        owner="Alte required test knowledge seed",
        approved_by="manual-test-seed" if entry.get("status") == "approved" else None,
        approved_at=datetime.now(UTC) if entry.get("status") == "approved" else None,
    )
    db.add(source)
    await db.flush()
    summary["sources_created"] = int(summary["sources_created"]) + 1
    return source


def hash_content(entry: dict[str, Any]) -> str:
    payload = "|".join(
        [
            entry.get("source_key", ""),
            entry.get("language", ""),
            entry.get("category", ""),
            entry.get("title", ""),
            entry.get("content", ""),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def keywords_to_text(value: str | list[str] | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        return " ".join(str(item) for item in value)
    return str(value)


async def _amain() -> int:
    parser = argparse.ArgumentParser(description="Seed curated standalone chatbot test knowledge.")
    parser.add_argument(
        "--allow-production",
        action="store_true",
        help="Allow seeding when ENVIRONMENT=production. Use only after content approval.",
    )
    args = parser.parse_args()
    result = await seed_required_test_knowledge(allow_production=args.allow_production)
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    warnings = result.get("warnings", [])
    if warnings:
        return 1
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(_amain()))


if __name__ == "__main__":
    main()
