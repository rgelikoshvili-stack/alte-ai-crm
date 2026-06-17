from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
from hashlib import sha256

from google.cloud.sql.connector import create_async_connector
from google.oauth2.credentials import Credentials
from sqlalchemy import func, select
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import KnowledgeSnippet, KnowledgeSource
from app.scripts.apply_official_alte_8_pdf_kb import load_rows, summarize


DEFAULT_INSTANCE_CONNECTION_NAME = "project-1e145fd0-c30e-4aac-a34:europe-west1:alte-ai-crm-db"


def database_parts() -> tuple[str, str, str]:
    raw_url = os.environ.get("DATABASE_URL")
    if not raw_url:
        raise RuntimeError("DATABASE_URL must be set from Secret Manager without printing it")
    url = make_url(raw_url)
    if not url.username or not url.password or not url.database:
        raise RuntimeError("DATABASE_URL is missing required connection fields")
    return url.username, url.password, url.database


def connector_credentials() -> Credentials | None:
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        return None
    token = os.environ.get("GCLOUD_ACCESS_TOKEN")
    if token is None:
        completed = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            check=True,
            capture_output=True,
            text=True,
        )
        token = completed.stdout.strip()
    if not token:
        raise RuntimeError("Unable to obtain a Google access token for Cloud SQL connector")
    return Credentials(token=token)


async def apply_rows_cloudsql(rows: list[dict], *, approve_for_chatbot: bool) -> dict:
    user, password, db_name = database_parts()
    instance_connection_name = os.environ.get("CLOUD_SQL_INSTANCE_CONNECTION_NAME", DEFAULT_INSTANCE_CONNECTION_NAME)
    connector = await create_async_connector(credentials=connector_credentials())

    async def getconn():
        return await connector.connect_async(
            instance_connection_name,
            "asyncpg",
            user=user,
            password=password,
            db=db_name,
        )

    engine = create_async_engine("postgresql+asyncpg://", async_creator=getconn, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    created_sources = 0
    updated_sources = 0
    created_snippets = 0
    updated_snippets = 0
    async with session_factory() as db:
        for row in rows:
            source_key = row["source_id"]
            status = "approved" if approve_for_chatbot or not row["review_required"] else "draft"
            source = await db.scalar(select(KnowledgeSource).where(KnowledgeSource.source_key == source_key))
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
                updated_sources += 1

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
                snippet.review_required = row["review_required"]
                snippet.stale_after_days = 365
                snippet.content_hash = content_hash
                snippet.keywords = ",".join(row.get("keywords") or [])
                snippet.status = status
                snippet.language = row["language"]
                updated_snippets += 1

        production_source_count = await db.scalar(
            select(func.count(KnowledgeSource.id)).where(KnowledgeSource.owner == "official_alte_8_pdf_kb")
        )
        production_snippet_count = await db.scalar(
            select(func.count(KnowledgeSnippet.id)).where(KnowledgeSnippet.source_domain == "official_alte_pdf_kb")
        )
        production_approved_snippet_count = await db.scalar(
            select(func.count(KnowledgeSnippet.id)).where(
                KnowledgeSnippet.source_domain == "official_alte_pdf_kb",
                KnowledgeSnippet.status == "approved",
            )
        )
        await db.commit()

    await engine.dispose()
    await connector.close_async()
    return {
        "created_sources": created_sources,
        "updated_sources": updated_sources,
        "created_snippets": created_snippets,
        "updated_snippets": updated_snippets,
        "approve_for_chatbot": approve_for_chatbot,
        "production_source_count": production_source_count,
        "production_snippet_count": production_snippet_count,
        "production_approved_snippet_count": production_approved_snippet_count,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply official Alte 8 PDF KB through Cloud SQL connector.")
    parser.add_argument("--apply", action="store_true", help="Write to production KB tables.")
    parser.add_argument("--approve-for-chatbot", action="store_true", help="Approve snippets/sources for chatbot retrieval.")
    args = parser.parse_args()
    rows = load_rows()
    summary = summarize(rows)
    if not args.apply:
        print(json.dumps({"mode": "dry-run", "would_write": False, **summary}, ensure_ascii=False, indent=2))
        return
    result = asyncio.run(apply_rows_cloudsql(rows, approve_for_chatbot=args.approve_for_chatbot))
    print(json.dumps({"mode": "apply", "would_write": True, **summary, **result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
