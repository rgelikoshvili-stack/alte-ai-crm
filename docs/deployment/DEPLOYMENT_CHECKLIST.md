# Deployment Checklist

Before using this checklist, fill/review:

- `DEPLOYMENT_VARIABLES.template.md`
- `GOOGLE_CLOUD_PREFLIGHT.md`
- `COMMAND_PLAN_GCLOUD.md`
- `DEPLOYMENT_RISK_REGISTER.md`
- `PRODUCTION_READINESS_DECISION.md`

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

- [x] Check `/health`. Phase 8I result: `/health: 200`.
- [x] Check `/version`. Phase 8I result: `/version: 200`.
- [x] Check `/diagnostics/ai`. Phase 8I result: `/diagnostics/ai: 200`.
- [x] Check `/diagnostics/local-demo`. Phase 8I result: `/diagnostics/local-demo: 200`.
- [x] Check `/dashboard/overview`. Phase 8I result: `/dashboard/overview: 401` without bearer token, expected with `AUTH_REQUIRED=true`.
- [ ] Test widget against Cloud Run URL.
- [ ] Verify no secrets in logs.
- [ ] Verify AI interactions are logged.
- [ ] Verify lead/task creation from website chat flow.

## Phase 8I Status

- Cloud Run deployment: `CLOUD_RUN_DEPLOYED`
- Deployment status: `BACKEND_DEPLOYED_PENDING_WEBSITE_PRIVACY`
- Docker image: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.8-cloud-run`
- Cloud SQL: `CLOUD_SQL_ATTACHED`
- Secret Manager: `SECRET_MANAGER_MAPPED`
- Website admin/developer access pending.
- Privacy/data approval pending.
- Actual website widget embed pending.

## Rollback

- [ ] Keep previous image tag.
- [ ] Roll back Cloud Run revision if needed.
- [ ] Do not delete the database.
- [ ] Use restore/backups only through an approved incident process.
