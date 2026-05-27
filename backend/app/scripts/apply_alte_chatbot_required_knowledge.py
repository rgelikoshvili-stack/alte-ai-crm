from __future__ import annotations

import argparse
import asyncio
import json
from hashlib import sha256
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
JSONL_PATH = PROJECT_ROOT / "backend" / "app" / "knowledge_seed" / "alte_chatbot_required_knowledge" / "alte_chatbot_required_knowledge.jsonl"


def load_rows() -> list[dict]:
    return [json.loads(line) for line in JSONL_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def sensitivity_for(row: dict) -> str:
    if row["department"] == "finance":
        return "high"
    if row["department"] in {"academic_registry", "student_services"}:
        return "medium"
    return "low"


def review_required_for(row: dict) -> bool:
    return (
        row["department"] in {"finance", "academic_registry", "student_services"}
        or row.get("handover_recommended") is True
        or "handover" in row.get("answer_policy", "")
        or "conservative" in row.get("answer_policy", "")
    )


def summarize(rows: list[dict]) -> dict:
    by_topic: dict[str, int] = {}
    by_department: dict[str, int] = {}
    for row in rows:
        by_topic[row["topic"]] = by_topic.get(row["topic"], 0) + 1
        by_department[row["department"]] = by_department.get(row["department"], 0) + 1
    return {
        "total_records": len(rows),
        "records_by_topic": by_topic,
        "records_by_department": by_department,
        "review_required_count": sum(1 for row in rows if review_required_for(row)),
        "draft_count": sum(1 for row in rows if review_required_for(row)),
        "approved_count": sum(1 for row in rows if not review_required_for(row)),
    }


async def apply_rows(rows: list[dict], *, approve_for_chatbot: bool = False) -> dict:
    from sqlalchemy import select

    from app.core.database import AsyncSessionLocal
    from app.models import KnowledgeSnippet, KnowledgeSource

    created_sources = 0
    created_snippets = 0
    updated_sources = 0
    updated_snippets = 0
    async with AsyncSessionLocal() as db:
        for row in rows:
            source_key = row["source_id"]
            review_required = review_required_for(row)
            sensitivity = sensitivity_for(row)
            source = await db.scalar(select(KnowledgeSource).where(KnowledgeSource.source_key == source_key))
            status = "approved" if approve_for_chatbot or not review_required else "draft"
            if source is None:
                source = KnowledgeSource(
                    source_key=source_key,
                    title=row["source_title"][:255],
                    source_type="alte_chatbot_required_document",
                    status=status,
                    language=row["language"],
                    source_url=row.get("source_url"),
                    source_domain="alte_chatbot_required_knowledge",
                    category=row["topic"][:120],
                    sensitivity=sensitivity,
                    review_required=review_required,
                    owner="alte_chatbot_required_knowledge",
                )
                db.add(source)
                await db.flush()
                created_sources += 1
            else:
                source.status = status
                source.review_required = review_required
                source.sensitivity = sensitivity
                source.category = row["topic"][:120]
                updated_sources += 1
            content = f"კითხვა: {row['question']}\n\nპასუხი: {row['answer']}"
            content_hash = sha256(content.encode("utf-8")).hexdigest()
            snippet = await db.scalar(select(KnowledgeSnippet).where(KnowledgeSnippet.source_key == source_key))
            if snippet is None:
                snippet = KnowledgeSnippet(
                    source_id=source.id,
                    source_key=source_key,
                    title=row["question"][:255],
                    content=content,
                    category=row["topic"][:120],
                    source_domain="alte_chatbot_required_knowledge",
                    sensitivity=sensitivity,
                    review_required=review_required,
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
                snippet.content = content
                snippet.content_hash = content_hash
                snippet.review_required = review_required
                snippet.sensitivity = sensitivity
                snippet.status = status
                snippet.category = row["topic"][:120]
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
    parser = argparse.ArgumentParser(description="Prepare or apply chatbot-required Alte knowledge.")
    parser.add_argument("--apply", action="store_true", help="Write to Knowledge Base tables. Omit for dry-run.")
    parser.add_argument("--dry-run", action="store_true", help="Dry-run only. This is the default.")
    parser.add_argument(
        "--approve-for-chatbot",
        action="store_true",
        help=(
            "Mark imported snippets/sources as approved for chatbot retrieval while preserving "
            "review_required metadata for sensitive topics."
        ),
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
