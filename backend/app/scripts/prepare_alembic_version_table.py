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


async def prepare_alembic_version_table() -> bool:
    database_url = os.getenv("DATABASE_URL", "")
    db_type = database_type(database_url)
    if not database_url:
        print("Alembic version table preparation: FAIL")
        print("database_type: missing")
        return False

    if db_type != "postgresql":
        print("Alembic version table preparation: PASS")
        print(f"database_type: {db_type}")
        print("action: no-op")
        return True

    engine = create_async_engine(database_url, pool_pre_ping=True)
    try:
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS alembic_version (
                        version_num VARCHAR(128) NOT NULL,
                        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                    )
                    """
                )
            )
            await conn.execute(
                text("ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(128)")
            )

        print("Alembic version table preparation: PASS")
        print("database_type: postgresql")
        print("action: prepared VARCHAR(128)")
        return True
    except Exception as exc:
        print("Alembic version table preparation: FAIL")
        print("database_type: postgresql")
        print(f"error_type: {exc.__class__.__name__}")
        return False
    finally:
        await engine.dispose()


def main() -> None:
    if not asyncio.run(prepare_alembic_version_table()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
