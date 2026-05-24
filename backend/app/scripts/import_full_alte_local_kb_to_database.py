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


BACKEND_ROOT = Path(__file__).resolve().parents[2]
SEED_PATH = BACKEND_ROOT / "app" / "knowledge_seed" / "full_alte_local_kb" / "full_alte_local_kb_normalized.jsonl"


def load_records(seed_path: Path = SEED_PATH) -> list[dict[str, Any]]:
    if not seed_path.exists():
        raise FileNotFoundError(f"Missing normalized KB file: {seed_path}")
    return [json.loads(line) for line in seed_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def is_production_environment() -> bool:
    return get_settings().ENVIRONMENT.lower().strip() == "production"


async def import_full_alte_local_kb(
    *,
    seed_path: Path = SEED_PATH,
    apply: bool = False,
    allow_production: bool = False,
) -> dict[str, Any]:
    records = load_records(seed_path)
    summary: dict[str, Any] = {
        "mode": "apply" if apply else "dry-run",
        "records_read": len(records),
        "sources_created": 0,
        "sources_updated": 0,
        "chunks_created": 0,
        "chunks_updated": 0,
        "chunks_skipped_duplicate": 0,
        "high_sensitivity_chunks": sum(1 for item in records if item.get("sensitivity") == "high"),
        "review_required_chunks": sum(1 for item in records if item.get("review_required")),
        "warnings": [],
    }

    if not apply:
        return summary
    if is_production_environment() and not allow_production:
        summary["warnings"].append("Refusing production import without --allow-production.")
        return summary

    async with AsyncSessionLocal() as db:
        for entry in records:
            source, created, updated = await upsert_source(db, entry)
            summary["sources_created"] += int(created)
            summary["sources_updated"] += int(updated)

            content_hash = hash_content(entry)
            snippet = await db.scalar(
                select(KnowledgeSnippet).where(
                    KnowledgeSnippet.source_key == entry["source_key"],
                    KnowledgeSnippet.content_hash == content_hash,
                )
            )
            if snippet:
                changed = update_snippet(snippet, entry, source.id, content_hash)
                summary["chunks_updated"] += int(changed)
                summary["chunks_skipped_duplicate"] += int(not changed)
                continue

            db.add(build_snippet(entry, source.id, content_hash))
            summary["chunks_created"] += 1
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
    values = {
        "title": source_title(entry),
        "source_type": "full_alte_local_kb",
        "status": entry.get("status", "approved"),
        "language": entry["language"],
        "source_url": entry.get("source_url"),
        "source_domain": entry.get("source_domain"),
        "category": entry["category"],
        "sensitivity": entry.get("sensitivity"),
        "review_required": bool(entry.get("review_required")),
        "stale_after_days": entry.get("stale_after_days"),
        "owner": "phase_8_full_local_kb_import",
    }
    if source is None:
        source = KnowledgeSource(source_key=entry["source_key"], **values)
        db.add(source)
        await db.flush()
        return source, True, False

    changed = False
    for field, value in values.items():
        if getattr(source, field) != value:
            setattr(source, field, value)
            changed = True
    if changed:
        await db.flush()
    return source, False, changed


def source_title(entry: dict[str, Any]) -> str:
    title = entry.get("title") or entry["source_key"]
    return f"{title} ({entry['category']})"[:255]


def build_snippet(entry: dict[str, Any], source_id: str, content_hash: str) -> KnowledgeSnippet:
    return KnowledgeSnippet(
        source_id=source_id,
        source_key=entry["source_key"],
        title=entry["title"][:255],
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


def update_snippet(snippet: KnowledgeSnippet, entry: dict[str, Any], source_id: str, content_hash: str) -> bool:
    values = {
        "source_id": source_id,
        "title": entry["title"][:255],
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
    changed = False
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
    parser = argparse.ArgumentParser(description="Import full local Alte KB into the app Knowledge Base.")
    parser.add_argument("--dry-run", action="store_true", help="Validate input and print summary without writing.")
    parser.add_argument("--apply", action="store_true", help="Write Knowledge Base records.")
    parser.add_argument("--allow-production", action="store_true", help="Allow write when ENVIRONMENT=production.")
    args = parser.parse_args()
    summary = await import_full_alte_local_kb(apply=args.apply, allow_production=args.allow_production)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if summary.get("warnings") else 0


def main() -> None:
    raise SystemExit(asyncio.run(_amain()))


if __name__ == "__main__":
    main()
