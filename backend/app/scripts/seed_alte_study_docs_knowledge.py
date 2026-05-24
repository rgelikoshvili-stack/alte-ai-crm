from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.models import KnowledgeSnippet, KnowledgeSource


SEED_PATH = (
    Path(__file__).resolve().parents[1]
    / "knowledge_seed"
    / "alte_study_docs"
    / "alte_study_docs_seed_v1.json"
)


def load_records(seed_path: Path = SEED_PATH) -> list[dict[str, Any]]:
    return json.loads(seed_path.read_text(encoding="utf-8"))


def is_production_environment() -> bool:
    return get_settings().ENVIRONMENT.lower().strip() == "production"


async def seed_alte_study_docs_knowledge(
    *,
    seed_path: Path = SEED_PATH,
    apply: bool = False,
    allow_production: bool = False,
) -> dict[str, int | str | list[str]]:
    records = load_records(seed_path)
    summary: dict[str, int | str | list[str]] = {
        "mode": "apply" if apply else "dry-run",
        "records_read": len(records),
        "sources_created": 0,
        "sources_updated": 0,
        "snippets_created": 0,
        "snippets_updated": 0,
        "snippets_skipped": 0,
        "review_required_records": sum(1 for item in records if item.get("review_required")),
        "high_sensitivity_records": sum(1 for item in records if item.get("sensitivity") == "high"),
        "warnings": [],
    }

    if not apply:
        return summary

    if is_production_environment() and not allow_production:
        summary["warnings"] = [
            "Refusing production import without --allow-production. This writes only Knowledge Base records."
        ]
        return summary

    async with AsyncSessionLocal() as db:
        for entry in records:
            source, source_created, source_updated = await upsert_source(db, entry)
            if source_created:
                summary["sources_created"] = int(summary["sources_created"]) + 1
            if source_updated:
                summary["sources_updated"] = int(summary["sources_updated"]) + 1

            content_hash = hash_content(entry)
            snippet = await db.scalar(
                select(KnowledgeSnippet).where(
                    KnowledgeSnippet.source_key == entry["source_key"],
                    KnowledgeSnippet.content_hash == content_hash,
                )
            )
            if snippet:
                changed = update_snippet_fields(snippet, entry, source.id, content_hash)
                if changed:
                    summary["snippets_updated"] = int(summary["snippets_updated"]) + 1
                else:
                    summary["snippets_skipped"] = int(summary["snippets_skipped"]) + 1
                continue

            db.add(build_snippet(entry, source.id, content_hash))
            summary["snippets_created"] = int(summary["snippets_created"]) + 1

        await db.commit()
    return summary


async def upsert_source(db, entry: dict[str, Any]) -> tuple[KnowledgeSource, bool, bool]:
    source = await db.scalar(
        select(KnowledgeSource).where(
            KnowledgeSource.source_key == entry["source_key"],
            KnowledgeSource.language == entry["language"],
            KnowledgeSource.category == entry["category"],
        )
    )
    if source is None:
        source = KnowledgeSource(
            source_key=entry["source_key"],
            title=f"{entry['source_key']} ({entry['language']}, {entry['category']})",
            source_type="alte_study_docs",
            status=entry.get("status", "approved"),
            language=entry["language"],
            source_url=entry.get("source_url"),
            source_domain=entry.get("source_domain"),
            category=entry["category"],
            sensitivity=entry.get("sensitivity"),
            review_required=bool(entry.get("review_required")),
            stale_after_days=entry.get("stale_after_days"),
            owner="phase_8_study_docs_import",
            approved_by="controlled-study-docs-seed" if entry.get("status") == "approved" else None,
        )
        db.add(source)
        await db.flush()
        return source, True, False

    changed = False
    for field in [
        "status",
        "source_domain",
        "category",
        "sensitivity",
        "review_required",
        "stale_after_days",
    ]:
        value = entry.get(field)
        if value is not None and getattr(source, field) != value:
            setattr(source, field, value)
            changed = True
    if source.source_type != "alte_study_docs":
        source.source_type = "alte_study_docs"
        changed = True
    if changed:
        await db.flush()
    return source, False, changed


def build_snippet(entry: dict[str, Any], source_id: str, content_hash: str) -> KnowledgeSnippet:
    return KnowledgeSnippet(
        source_id=source_id,
        source_key=entry["source_key"],
        title=entry["title"],
        content=entry["content"],
        category=entry["category"],
        source_domain=entry.get("source_domain"),
        sensitivity=entry.get("sensitivity"),
        review_required=bool(entry.get("review_required")),
        stale_after_days=entry.get("stale_after_days"),
        content_hash=content_hash,
        program_name=entry.get("program_name"),
        keywords=keywords_to_text(entry.get("keywords")),
        status=entry.get("status", "approved"),
        language=entry["language"],
    )


def update_snippet_fields(
    snippet: KnowledgeSnippet,
    entry: dict[str, Any],
    source_id: str,
    content_hash: str,
) -> bool:
    changed = False
    values = {
        "source_id": source_id,
        "title": entry["title"],
        "content": entry["content"],
        "category": entry["category"],
        "source_domain": entry.get("source_domain"),
        "sensitivity": entry.get("sensitivity"),
        "review_required": bool(entry.get("review_required")),
        "stale_after_days": entry.get("stale_after_days"),
        "content_hash": content_hash,
        "program_name": entry.get("program_name"),
        "keywords": keywords_to_text(entry.get("keywords")),
        "status": entry.get("status", "approved"),
        "language": entry["language"],
    }
    for field, value in values.items():
        if getattr(snippet, field) != value:
            setattr(snippet, field, value)
            changed = True
    return changed


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
    parser = argparse.ArgumentParser(description="Seed Alte study documents into Knowledge Base.")
    parser.add_argument("--apply", action="store_true", help="Write Knowledge Base records.")
    parser.add_argument("--allow-production", action="store_true", help="Allow write when ENVIRONMENT=production.")
    args = parser.parse_args()
    summary = await seed_alte_study_docs_knowledge(apply=args.apply, allow_production=args.allow_production)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if summary.get("warnings") else 0


def main() -> None:
    raise SystemExit(asyncio.run(_amain()))


if __name__ == "__main__":
    main()
