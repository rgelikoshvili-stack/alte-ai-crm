from __future__ import annotations

import asyncio
import csv
from pathlib import Path

from sqlalchemy import or_, select

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.models import KnowledgeSnippet, KnowledgeSource


REPORT_PATH = Path(__file__).resolve().parents[2] / "reports" / "knowledge_review_queue.csv"
REVIEW_CATEGORIES = {"finance", "deadlines", "international_admissions", "medicine", "medicine_md"}


def recommended_action(snippet: KnowledgeSnippet, source: KnowledgeSource) -> str:
    category = (snippet.category or source.category or "").lower()
    if category in {"finance", "deadlines"}:
        return "NEEDS_OFFICIAL_SOURCE"
    if category in {"international_admissions", "medicine", "medicine_md"}:
        return "HANDOVER_ONLY"
    if snippet.status == "draft" or source.status == "draft":
        return "REWRITE"
    if snippet.review_required or source.review_required:
        return "APPROVE"
    return "APPROVE"


def preview(content: str | None, limit: int = 180) -> str:
    text = " ".join((content or "").split())
    return text[:limit]


async def export_review_queue(output_path: Path = REPORT_PATH) -> dict[str, int | str]:
    settings = get_settings()
    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured. Set it locally without printing it, then rerun.")

    query = (
        select(KnowledgeSnippet, KnowledgeSource)
        .join(KnowledgeSource, KnowledgeSnippet.source_id == KnowledgeSource.id)
        .where(
            or_(
                KnowledgeSnippet.review_required.is_(True),
                KnowledgeSource.review_required.is_(True),
                KnowledgeSnippet.status.in_(["draft", "review_required"]),
                KnowledgeSource.status.in_(["draft", "review_required"]),
                KnowledgeSnippet.category.in_(REVIEW_CATEGORIES),
                KnowledgeSource.category.in_(REVIEW_CATEGORIES),
            )
        )
        .order_by(KnowledgeSnippet.category.asc(), KnowledgeSnippet.language.asc(), KnowledgeSnippet.title.asc())
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows_written = 0
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(query)).all()
        with output_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "source_key",
                    "title",
                    "category",
                    "department",
                    "language",
                    "source_domain",
                    "status",
                    "review_required",
                    "sensitivity",
                    "stale_after_days",
                    "content_preview",
                    "recommended_action",
                ],
            )
            writer.writeheader()
            for snippet, source in rows:
                writer.writerow(
                    {
                        "source_key": snippet.source_key or source.source_key or "",
                        "title": snippet.title,
                        "category": snippet.category or source.category or "",
                        "department": "",
                        "language": snippet.language or source.language or "",
                        "source_domain": snippet.source_domain or source.source_domain or "",
                        "status": snippet.status,
                        "review_required": str(bool(snippet.review_required or source.review_required)).lower(),
                        "sensitivity": snippet.sensitivity or source.sensitivity or "",
                        "stale_after_days": snippet.stale_after_days if snippet.stale_after_days is not None else "",
                        "content_preview": preview(snippet.content),
                        "recommended_action": recommended_action(snippet, source),
                    }
                )
                rows_written += 1
    return {"rows_written": rows_written, "output_path": str(output_path)}


async def _amain() -> int:
    try:
        result = await export_review_queue()
    except Exception as exc:
        print(f"FAIL knowledge review queue export: {exc}")
        return 1
    print(f"PASS knowledge review queue export: rows_written={result['rows_written']}, output_path={result['output_path']}")
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(_amain()))


if __name__ == "__main__":
    main()
