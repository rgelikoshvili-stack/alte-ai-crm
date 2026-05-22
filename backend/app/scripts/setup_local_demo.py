from __future__ import annotations

import asyncio
import json

from sqlalchemy import inspect

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal, engine
from app.services.bootstrap_service import bootstrap_local_demo_data
from app.scripts.seed_alte_knowledge import seed_alte_knowledge

REQUIRED_TABLES = {
    "departments",
    "pipeline_stages",
    "knowledge_sources",
    "knowledge_snippets",
}


async def setup_local_demo() -> dict:
    settings = get_settings()
    tables_ready = await required_tables_exist()
    if not tables_ready:
        return {
            "database_url": mask_database_url(settings.DATABASE_URL),
            "migrations_ready": False,
            "message": "Run: alembic upgrade head",
            "next_commands": next_commands(),
        }

    async with AsyncSessionLocal() as session:
        bootstrap_summary = await bootstrap_local_demo_data(session)
    knowledge_summary = await seed_alte_knowledge()
    return {
        "database_url": mask_database_url(settings.DATABASE_URL),
        "migrations_ready": True,
        "bootstrap_demo": bootstrap_summary,
        "alte_knowledge_seed": knowledge_summary,
        "next_commands": next_commands(),
    }


async def required_tables_exist() -> bool:
    async with engine.begin() as conn:
        table_names = await conn.run_sync(lambda sync_conn: set(inspect(sync_conn).get_table_names()))
    return REQUIRED_TABLES.issubset(table_names)


def mask_database_url(database_url: str) -> str:
    if database_url.startswith("sqlite"):
        return "sqlite://***"
    if "@" in database_url:
        prefix, _, suffix = database_url.rpartition("@")
        scheme = prefix.split("://", 1)[0] if "://" in prefix else "database"
        return f"{scheme}://***@{suffix}"
    return "***"


def next_commands() -> dict[str, str]:
    return {
        "backend": "cd C:\\tmp\\alte-ai-crm\\backend && .\\.venv\\Scripts\\Activate.ps1 && uvicorn app.main:app --reload",
        "widget": "cd C:\\tmp\\alte-ai-crm\\widget && python -m http.server 5500",
        "demo_url": "http://127.0.0.1:5500/demo.html",
        "smoke": "cd C:\\tmp\\alte-ai-crm\\backend && .\\.venv\\Scripts\\Activate.ps1 && python -m app.scripts.e2e_local_smoke",
    }


async def main() -> None:
    result = await setup_local_demo()
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(main())
