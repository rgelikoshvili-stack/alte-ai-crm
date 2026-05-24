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

Current Phase 8H status:

- Production DB connectivity checked: `PASS`
- Alembic version table width correction applied: `alembic_version.version_num VARCHAR(128)`
- Alembic migration status: `MIGRATIONS_COMPLETED`
- Current revision: `006_phase_7b_knowledge_governance`
- Production schema verification: `PASS`
- Production-safe core bootstrap: `PRODUCTION_SAFE_BOOTSTRAP_COMPLETED`
- Knowledge seed status: `KNOWLEDGE_SEED_COMPLETED`
- Production DB seed verification: `PRODUCTION_DB_SEED_VERIFIED`

Correction note:

The first production migration attempt stopped safely because PostgreSQL created Alembic's default `version_num` column as `VARCHAR(32)`, while revision `006_phase_7b_knowledge_governance` is longer. Phase 8H-Correction prepared the Alembic version table with `VARCHAR(128)` without dropping tables or deleting rows, then reran `alembic upgrade head`.

## B. Knowledge Seed

Run:

```powershell
python -m app.scripts.seed_alte_knowledge
```

The seed script is idempotent.

Phase 8H seed result:

- Knowledge sources created: 10
- Knowledge snippets created: 17
- Warnings: none

Production-safe bootstrap result:

- Departments created: 4
- Pipelines created: 1
- Pipeline stages created: 7
- Fake customers/leads/conversations/messages were not created.

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
