from __future__ import annotations

import argparse
import asyncio
import json
from hashlib import sha256
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
JSONL_PATH = PROJECT_ROOT / "backend" / "app" / "knowledge_seed" / "official_alte_8_pdf_kb" / "official_alte_8_pdf_kb_normalized.jsonl"


def load_rows() -> list[dict]:
    return [json.loads(line) for line in JSONL_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def summarize(rows: list[dict]) -> dict:
    by_file: dict[str, int] = {}
    for row in rows:
        by_file[row["source_file"]] = by_file.get(row["source_file"], 0) + 1
    return {
        "total_chunks": len(rows),
        "chunks_by_document": by_file,
        "review_required_count": sum(1 for row in rows if row.get("review_required")),
        "public_answer_allowed_count": sum(1 for row in rows if row.get("public_answer_allowed")),
    }


async def apply_rows(rows: list[dict], *, approve_for_chatbot: bool = False) -> dict:
    from sqlalchemy import select

    from app.core.database import AsyncSessionLocal
    from app.models import KnowledgeSnippet, KnowledgeSource

    created_sources = 0
    created_snippets = 0
    updated_snippets = 0
    async with AsyncSessionLocal() as db:
        for row in rows:
            source_key = row["source_id"]
            source = await db.scalar(select(KnowledgeSource).where(KnowledgeSource.source_key == source_key))
            status = "approved" if approve_for_chatbot or not row["review_required"] else "draft"
            if source is None:
                source = KnowledgeSource(
                    source_key=source_key,
                    title=f"{row['document_title']} p.{row['page_start']}",
                    source_type="pdf",
                    status=status,
                    language=row["language"],
                    source_url=None,
                    source_domain="official_alte_pdf_kb",
                    category=row["topic"],
                    sensitivity=row["sensitivity"],
                    review_required=row["review_required"],
                    owner="official_alte_8_pdf_kb",
                )
                db.add(source)
                await db.flush()
                created_sources += 1
            else:
                source.title = f"{row['document_title']} p.{row['page_start']}"
                source.source_type = "pdf"
                source.status = status
                source.language = row["language"]
                source.source_domain = "official_alte_pdf_kb"
                source.category = row["topic"]
                source.sensitivity = row["sensitivity"]
                source.review_required = row["review_required"]
                source.owner = "official_alte_8_pdf_kb"
            content_hash = sha256(row["content"].encode("utf-8")).hexdigest()
            snippet = await db.scalar(select(KnowledgeSnippet).where(KnowledgeSnippet.source_key == source_key))
            if snippet is None:
                snippet = KnowledgeSnippet(
                    source_id=source.id,
                    source_key=source_key,
                    title=f"{row['document_title']} p.{row['page_start']} c.{row['chunk_index']}",
                    content=row["content"],
                    category=row["topic"],
                    source_domain="official_alte_pdf_kb",
                    sensitivity=row["sensitivity"],
                    review_required=row["review_required"],
                    stale_after_days=365,
                    content_hash=content_hash,
                    program_name=None,
                    keywords=",".join(row.get("keywords") or []),
                    status=status,
                    language=row["language"],
                )
                db.add(snippet)
                created_snippets += 1
            else:
                snippet.title = f"{row['document_title']} p.{row['page_start']} c.{row['chunk_index']}"
                snippet.content = row["content"]
                snippet.category = row["topic"]
                snippet.source_domain = "official_alte_pdf_kb"
                snippet.sensitivity = row["sensitivity"]
                snippet.stale_after_days = 365
                snippet.content_hash = content_hash
                snippet.review_required = row["review_required"]
                snippet.keywords = ",".join(row.get("keywords") or [])
                snippet.status = status
                snippet.language = row["language"]
                updated_snippets += 1
        await db.commit()
    return {
        "created_sources": created_sources,
        "created_snippets": created_snippets,
        "updated_snippets": updated_snippets,
        "approve_for_chatbot": approve_for_chatbot,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare or apply the official Alte 8 PDF knowledge base.")
    parser.add_argument("--apply", action="store_true", help="Write to Knowledge Base tables. Omit for dry-run.")
    parser.add_argument("--dry-run", action="store_true", help="Dry-run only. This is the default.")
    parser.add_argument(
        "--approve-for-chatbot",
        action="store_true",
        help="Mark snippets/sources approved for chatbot retrieval while preserving review_required metadata.",
    )
    args = parser.parse_args()
    rows = load_rows()
    summary = summarize(rows)
    if not args.apply:
        print(json.dumps({"mode": "dry-run", "would_write": False, **summary}, ensure_ascii=False, indent=2))
        return
    result = asyncio.run(apply_rows(rows, approve_for_chatbot=args.approve_for_chatbot))
    print(json.dumps({"mode": "apply", "would_write": True, **summary, **result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
