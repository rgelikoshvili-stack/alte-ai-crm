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

## Phase 8G Execution Status

- Corrected Cloud SQL approach: Enterprise edition with low-cost/shared-core pilot tier.
- Instance status: `CLOUD_SQL_INSTANCE_CREATED`
- Instance: `alte-ai-crm-db`
- Region: `europe-west1`
- Tier: `db-f1-micro`
- Database status: `DATABASE_CREATED`
- Database: `alte_ai_crm`
- App user status: `DB_USER_CREATED`
- App user: `alte_app`
- High availability: disabled for pilot (`ZONAL`)
- `alte-database-url` secret version: `VERSION_ADDED`
- Cloud Run deployment: not performed.
- Docker image push: not performed.

The real production `DATABASE_URL` is stored only in Secret Manager and ignored local files. It is not documented here.

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
