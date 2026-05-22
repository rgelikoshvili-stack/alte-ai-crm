from __future__ import annotations

import asyncio
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models import KnowledgeSnippet, KnowledgeSource

SEED_PATH = Path(__file__).resolve().parents[1] / "knowledge_seed" / "alte_seed_v1.json"


async def seed_alte_knowledge(seed_path: Path = SEED_PATH) -> dict[str, int | list[str]]:
    data = json.loads(seed_path.read_text(encoding="utf-8"))
    summary: dict[str, int | list[str]] = {
        "sources_created": 0,
        "snippets_created": 0,
        "skipped_existing": 0,
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
                    effective_from=parse_date(entry.get("effective_from")),
                    effective_to=parse_date(entry.get("effective_until")),
                    status=entry.get("status", "approved"),
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
        return source

    source = KnowledgeSource(
        source_key=entry.get("source_key"),
        title=source_title(entry),
        source_type="manual",
        status=entry.get("status", "approved"),
        language=entry["language"],
        source_url=entry.get("source_url"),
        source_domain=entry.get("source_domain"),
        category=entry["category"],
        sensitivity=entry.get("sensitivity", "low"),
        review_required=bool(entry.get("review_required", False)),
        stale_after_days=entry.get("stale_after_days"),
        owner="Alte manual knowledge seed",
        approved_by="manual-seed",
        approved_at=datetime.now(UTC) if entry.get("status", "approved") == "approved" else None,
    )
    db.add(source)
    await db.flush()
    summary["sources_created"] = int(summary["sources_created"]) + 1
    return source


def source_title(entry: dict[str, Any]) -> str:
    return f"{entry['source_key']} ({entry['language']}, {entry['category']})"


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


def parse_date(value: str | None):
    if not value:
        return None
    return datetime.fromisoformat(value).date()


async def main() -> None:
    result = await seed_alte_knowledge()
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(main())
