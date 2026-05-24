from __future__ import annotations

import asyncio
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


def database_type(database_url: str) -> str:
    if database_url.startswith("postgresql"):
        return "postgresql"
    if database_url.startswith("sqlite"):
        return "sqlite"
    return "other"


async def check_connection() -> bool:
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        print("DB connection: FAIL")
        print("database_type: missing")
        return False

    engine = create_async_engine(database_url, pool_pre_ping=True)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("DB connection: PASS")
        print(f"database_type: {database_type(database_url)}")
        return True
    except Exception as exc:
        print("DB connection: FAIL")
        print(f"database_type: {database_type(database_url)}")
        print(f"error_type: {exc.__class__.__name__}")
        return False
    finally:
        await engine.dispose()


def main() -> None:
    if not asyncio.run(check_connection()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
