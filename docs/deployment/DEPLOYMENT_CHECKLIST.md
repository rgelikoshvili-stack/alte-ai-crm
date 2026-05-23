# Deployment Checklist

## Before Deployment

- [ ] Tests pass with `AI_PROVIDER=mock`.
- [ ] Claude live validation passed locally.
- [ ] `.env` is not tracked by Git.
- [ ] Docker build passes.
- [ ] `python -m app.scripts.startup_check` passes with production env.
- [ ] Cloud SQL PostgreSQL instance is created.
- [ ] Secret Manager secrets are created.
- [ ] CORS origins are set to `https://alte.edu.ge,https://join.alte.edu.ge`.
- [ ] Knowledge seed is prepared.
- [ ] Backup/release tag is created.

## Deployment

- [ ] Build image.
- [ ] Push image to Artifact Registry.
- [ ] Deploy Cloud Run service.
- [ ] Attach Cloud SQL.
- [ ] Map Secret Manager secrets.
- [ ] Set non-secret env vars.
- [ ] Run Alembic migrations.
- [ ] Run Alte knowledge seed.

## After Deployment

- [ ] Check `/health`.
- [ ] Check `/diagnostics/ai`.
- [ ] Check `/dashboard/overview`.
- [ ] Test widget against Cloud Run URL.
- [ ] Verify no secrets in logs.
- [ ] Verify AI interactions are logged.
- [ ] Verify lead/task creation from website chat flow.

## Rollback

- [ ] Keep previous image tag.
- [ ] Roll back Cloud Run revision if needed.
- [ ] Do not delete the database.
- [ ] Use restore/backups only through an approved incident process.
