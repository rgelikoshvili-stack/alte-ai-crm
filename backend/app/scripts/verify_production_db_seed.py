from __future__ import annotations

import asyncio
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


COUNT_QUERIES = {
    "departments": "SELECT COUNT(*) FROM departments",
    "pipelines": "SELECT COUNT(*) FROM pipelines",
    "pipeline_stages": "SELECT COUNT(*) FROM pipeline_stages",
    "knowledge_sources": "SELECT COUNT(*) FROM knowledge_sources",
    "knowledge_snippets": "SELECT COUNT(*) FROM knowledge_snippets",
}


async def verify_seed() -> bool:
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        print("Production DB seed: FAIL")
        print("database_type: missing")
        return False
    database_type = "postgresql" if database_url.startswith("postgresql") else "sqlite" if database_url.startswith("sqlite") else "other"
    engine = create_async_engine(database_url, pool_pre_ping=True)
    try:
        counts: dict[str, int] = {}
        async with engine.connect() as conn:
            for name, query in COUNT_QUERIES.items():
                counts[name] = int((await conn.execute(text(query))).scalar_one())
        failed = [name for name, value in counts.items() if value <= 0]
        print("Production DB seed: PASS" if not failed else "Production DB seed: FAIL")
        print(f"database_type: {database_type}")
        for name, value in counts.items():
            print(f"{name}: {value}")
        return not failed
    except Exception as exc:
        print("Production DB seed: FAIL")
        print(f"database_type: {database_type}")
        print(f"error_type: {exc.__class__.__name__}")
        return False
    finally:
        await engine.dispose()


def main() -> None:
    if not asyncio.run(verify_seed()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
