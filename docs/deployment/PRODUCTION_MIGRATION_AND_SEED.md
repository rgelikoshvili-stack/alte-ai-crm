# Production Migration And Seed Runbook

## A. Migration Requirement

Run:

```powershell
alembic upgrade head
```

Current Phase 8G status:

- Cloud SQL instance status: `CLOUD_SQL_INSTANCE_CREATED`
- Database status: `DATABASE_CREATED`
- App user status: `DB_USER_CREATED`
- `DATABASE_URL` secret version: `VERSION_ADDED`
- Production migrations have not been run yet.
- Production seed has not been run yet.

## B. Knowledge Seed

Run:

```powershell
python -m app.scripts.seed_alte_knowledge
```

The seed script is idempotent.

## C. Options

### Option 1: Controlled Environment

Run migration from a controlled environment connected to Cloud SQL.

### Option 2: Cloud Run Job / Temporary Command

Use a Cloud Run Job or temporary one-off service command.

Do not implement the job until it is separately approved.

## D. Warnings

- Back up the database before migrations after production data exists.
- Do not run destructive migrations without review.
- Seed script is idempotent.
- Do not seed draft or unreviewed sensitive knowledge as approved.

## E. Verification After Migration

- `GET /health`
- `GET /diagnostics/ai`
- `GET /diagnostics/local-demo` or a production-safe diagnostics endpoint
- `GET /knowledge/sources`
- `GET /dashboard/overview`
