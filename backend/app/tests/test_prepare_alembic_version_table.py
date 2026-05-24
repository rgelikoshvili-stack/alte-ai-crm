import asyncio

from app.scripts import prepare_alembic_version_table


def test_prepare_alembic_version_table_importable():
    assert prepare_alembic_version_table.database_type("postgresql+asyncpg://user:pass@host/db") == "postgresql"


def test_prepare_alembic_version_table_database_type_detection():
    assert prepare_alembic_version_table.database_type("sqlite+aiosqlite:///./test.db") == "sqlite"
    assert prepare_alembic_version_table.database_type("mysql://user:pass@host/db") == "other"


def test_prepare_alembic_version_table_sqlite_noop(monkeypatch, capsys):
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

    result = asyncio.run(prepare_alembic_version_table.prepare_alembic_version_table())

    captured = capsys.readouterr()
    assert result is True
    assert "DATABASE_URL" not in captured.out
