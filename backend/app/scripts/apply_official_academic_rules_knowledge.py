from __future__ import annotations

import argparse
import asyncio
import json
from hashlib import sha256
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
STRUCTURED_KNOWLEDGE_PATH = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "official_academic_rules_ka_en.json"
FULL_CHUNKS_PATH = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "official_academic_rules_full_chunks.json"


def load_rows(*, include_full_chunks: bool = False) -> list[dict]:
    data = json.loads(STRUCTURED_KNOWLEDGE_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise RuntimeError("Official academic rules knowledge artifact must be a list")
    if include_full_chunks:
        full_data = json.loads(FULL_CHUNKS_PATH.read_text(encoding="utf-8"))
        if not isinstance(full_data, list):
            raise RuntimeError("Official academic rules full chunks artifact must be a list")
        data = [*data, *full_data]
    return data


def review_required_for(row: dict) -> bool:
    policy = str(row.get("answer_policy") or "").lower()
    text = str(row.get("text") or "").lower()
    return (
        "handover" in policy
        or "partial" in text
        or "additional official source" in text
        or str(row.get("sensitivity") or "").lower() != "low"
    )


def summarize(rows: list[dict]) -> dict:
    by_topic: dict[str, int] = {}
    for row in rows:
        topic = str(row.get("topic") or "unknown")
        by_topic[topic] = by_topic.get(topic, 0) + 1
    return {
        "total_records": len(rows),
        "records_by_topic": by_topic,
        "review_required_count": sum(1 for row in rows if review_required_for(row)),
        "approved_count": len(rows),
    }


async def apply_rows(rows: list[dict], *, approve_for_chatbot: bool = False) -> dict:
    from sqlalchemy import select

    from app.core.database import AsyncSessionLocal
    from app.models import KnowledgeSnippet, KnowledgeSource

    created_sources = 0
    updated_sources = 0
    created_snippets = 0
    updated_snippets = 0
    async with AsyncSessionLocal() as db:
        for row in rows:
            source_key = row["source_id"]
            review_required = review_required_for(row)
            status = "approved" if approve_for_chatbot else "draft"
            source = await db.scalar(select(KnowledgeSource).where(KnowledgeSource.source_key == source_key))
            if source is None:
                source = KnowledgeSource(
                    source_key=source_key,
                    title=str(row["document_title"])[:255],
                    source_type="official_academic_rules",
                    status=status,
                    language=row["language"],
                    source_url=None,
                    source_domain="official_academic_rules",
                    category=str(row["topic"])[:120],
                    sensitivity="medium",
                    review_required=review_required,
                    owner="phase_9t_official_academic_rules_full" if source_key.startswith("official_academic_rules_full_") else "phase_9t_official_academic_rules",
                )
                db.add(source)
                await db.flush()
                created_sources += 1
            else:
                source.title = str(row["document_title"])[:255]
                source.source_type = "official_academic_rules"
                source.status = status
                source.language = row["language"]
                source.source_domain = "official_academic_rules"
                source.category = str(row["topic"])[:120]
                source.sensitivity = "medium"
                source.review_required = review_required
                source.owner = "phase_9t_official_academic_rules_full" if source_key.startswith("official_academic_rules_full_") else "phase_9t_official_academic_rules"
                updated_sources += 1

            content = (
                f"Official source: {row['document_title']}\n"
                f"Reference: {row['page_article_reference']}\n"
                f"Policy: {row['answer_policy']}\n\n"
                f"{row['text']}"
            )
            content_hash = sha256(content.encode("utf-8")).hexdigest()
            snippet = await db.scalar(select(KnowledgeSnippet).where(KnowledgeSnippet.source_key == source_key))
            if snippet is None:
                snippet = KnowledgeSnippet(
                    source_id=source.id,
                    source_key=source_key,
                    title=str(row["page_article_reference"])[:255],
                    content=content,
                    category=str(row["topic"])[:120],
                    source_domain="official_academic_rules",
                    sensitivity="medium",
                    review_required=review_required,
                    stale_after_days=365,
                    content_hash=content_hash,
                    program_name=None,
                    keywords=row.get("keywords") or ", ".join(row.get("qa_ids") or []),
                    status=status,
                    language=row["language"],
                )
                db.add(snippet)
                created_snippets += 1
            else:
                snippet.title = str(row["page_article_reference"])[:255]
                snippet.content = content
                snippet.content_hash = content_hash
                snippet.category = str(row["topic"])[:120]
                snippet.source_domain = "official_academic_rules"
                snippet.sensitivity = "medium"
                snippet.review_required = review_required
                snippet.stale_after_days = 365
                snippet.keywords = row.get("keywords") or ", ".join(row.get("qa_ids") or [])
                snippet.status = status
                snippet.language = row["language"]
                updated_snippets += 1
        await db.commit()
    return {
        "created_sources": created_sources,
        "updated_sources": updated_sources,
        "created_snippets": created_snippets,
        "updated_snippets": updated_snippets,
        "approve_for_chatbot": approve_for_chatbot,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare or apply official academic rules knowledge.")
    parser.add_argument("--apply", action="store_true", help="Write to Knowledge Base tables. Omit for dry-run.")
    parser.add_argument("--dry-run", action="store_true", help="Dry-run only. This is the default.")
    parser.add_argument(
        "--approve-for-chatbot",
        action="store_true",
        help="Mark snippets/sources approved for chatbot retrieval while preserving review_required metadata.",
    )
    parser.add_argument(
        "--include-full-chunks",
        action="store_true",
        help="Apply both the 20 structured answers and full chunks extracted from the five official files.",
    )
    args = parser.parse_args()
    rows = load_rows(include_full_chunks=args.include_full_chunks)
    summary = summarize(rows)
    if not args.apply:
        print(json.dumps({"mode": "dry-run", "would_write": False, **summary}, ensure_ascii=False, indent=2))
        return
    result = asyncio.run(apply_rows(rows, approve_for_chatbot=args.approve_for_chatbot))
    print(json.dumps({"mode": "apply", "would_write": True, **summary, **result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
