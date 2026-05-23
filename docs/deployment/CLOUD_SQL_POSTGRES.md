# Cloud SQL PostgreSQL Guide

Production should use PostgreSQL, not SQLite.

## Create Database

Create a Cloud SQL PostgreSQL instance in the selected region.

Recommended database name:

```text
alte_ai_crm
```

Create a dedicated database user and store the password in Secret Manager.

## Connection Options

Preferred options:

- Cloud Run Cloud SQL integration / connector
- Private IP if the network is prepared
- Public IP only if access is tightly controlled

Production `DATABASE_URL` format:

```env
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:5432/alte_ai_crm
```

Store the full production `DATABASE_URL` as the `alte-database-url` secret.

## Migrations

Run migrations after the Cloud SQL database is reachable:

```powershell
cd backend
alembic upgrade head
```

Run the approved local knowledge seed:

```powershell
python -m app.scripts.seed_alte_knowledge
```

## Warnings

- Never use SQLite in production.
- Never print database passwords in logs.
- Never commit production `DATABASE_URL`.
- Confirm backup and restore policy before production launch.
