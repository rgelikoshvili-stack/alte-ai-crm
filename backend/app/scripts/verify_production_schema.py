from __future__ import annotations

import asyncio
import os

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine


EXPECTED_TABLES = [
    "departments",
    "customers",
    "leads",
    "conversations",
    "messages",
    "tasks",
    "knowledge_sources",
    "knowledge_snippets",
    "ai_interactions",
    "audit_logs",
]


async def verify_schema() -> bool:
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        print("Production schema: FAIL")
        print("database_type: missing")
        return False

    database_type = "postgresql" if database_url.startswith("postgresql") else "sqlite" if database_url.startswith("sqlite") else "other"
    engine = create_async_engine(database_url, pool_pre_ping=True)
    try:
        async with engine.connect() as conn:
            table_names = await conn.run_sync(lambda sync_conn: set(inspect(sync_conn).get_table_names()))
        missing = [table for table in EXPECTED_TABLES if table not in table_names]
        if missing:
            print("Production schema: FAIL")
            print(f"database_type: {database_type}")
            print(f"missing_tables: {','.join(missing)}")
            return False
        print("Production schema: PASS")
        print(f"database_type: {database_type}")
        print(f"tables_verified: {len(EXPECTED_TABLES)}")
        return True
    except Exception as exc:
        print("Production schema: FAIL")
        print(f"database_type: {database_type}")
        print(f"error_type: {exc.__class__.__name__}")
        return False
    finally:
        await engine.dispose()


def main() -> None:
    if not asyncio.run(verify_schema()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
