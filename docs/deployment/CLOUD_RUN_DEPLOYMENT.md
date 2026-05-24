# Cloud Run Deployment Guide

This guide prepares Alte AI CRM for a future Google Cloud Run deployment. It does not require or perform deployment by itself.

Review these planning files before running any cloud command:

- `DEPLOYMENT_VARIABLES.template.md`
- `GOOGLE_CLOUD_PREFLIGHT.md`
- `COMMAND_PLAN_GCLOUD.md`
- `DEPLOYMENT_RISK_REGISTER.md`
- `PRODUCTION_READINESS_DECISION.md`

## Prerequisites

- Google Cloud project with billing enabled
- `gcloud` CLI installed and authenticated
- Cloud Run API enabled
- Artifact Registry API enabled
- Cloud SQL Admin API enabled
- Secret Manager API enabled
- PostgreSQL database prepared in Cloud SQL
- Secrets created in Secret Manager

Recommended placeholders:

- `PROJECT_ID`
- `REGION` such as `europe-west1` or `europe-west3`
- `SERVICE_NAME=alte-ai-crm-backend`
- `IMAGE_URL=REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/alte-ai-crm-backend:TAG`

## Build Image

```powershell
cd C:\tmp\alte-ai-crm
docker build -t alte-ai-crm-backend:local ./backend
```

Artifact Registry example:

```powershell
gcloud artifacts repositories create REPOSITORY `
  --repository-format=docker `
  --location=REGION `
  --project=PROJECT_ID

docker tag alte-ai-crm-backend:local IMAGE_URL
docker push IMAGE_URL
```

## Deploy Cloud Run

Example deployment command with placeholders:

```powershell
gcloud run deploy SERVICE_NAME `
  --image IMAGE_URL `
  --region REGION `
  --project PROJECT_ID `
  --platform managed `
  --allow-unauthenticated `
  --port 8080 `
  --set-env-vars ENVIRONMENT=production,APP_VERSION=0.8.0,AUTH_REQUIRED=true,AI_PROVIDER=claude,AI_MODEL=claude-sonnet-4-5-20250929,AI_TIMEOUT_SECONDS=20,AI_CONFIDENCE_THRESHOLD=0.70,AI_MAX_TOKENS=1200,CORS_ORIGINS=https://alte.edu.ge\,https://join.alte.edu.ge `
  --set-secrets DATABASE_URL=alte-database-url:latest,JWT_SECRET=alte-jwt-secret:latest,ANTHROPIC_API_KEY=alte-anthropic-api-key:latest
```

If using Cloud SQL integration, also attach the Cloud SQL instance through Cloud Run settings or the `--add-cloudsql-instances` flag.

## Health Checks

After deployment:

```text
GET https://SERVICE_URL/health
GET https://SERVICE_URL/diagnostics/local-demo
GET https://SERVICE_URL/diagnostics/ai
```

Expected:

- `/health` returns `status=ok`
- `/diagnostics/ai` shows Claude enabled without exposing secrets
- diagnostics do not print full database URLs or API keys

## Rollback

- Keep the previous image tag.
- Roll back to the previous Cloud Run revision if the new revision fails.
- Do not delete the database as a rollback method.
- Keep database migrations forward-compatible and separately approved.

## Phase 8I Execution Status

Deployment status: `BACKEND_DEPLOYED_PENDING_WEBSITE_PRIVACY`

- Cloud Run service: `alte-ai-crm-backend`
- Cloud Run deployment: `CLOUD_RUN_DEPLOYED`
- Region: `europe-west1`
- Service URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Docker image: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.8-cloud-run`
- Image tag: `v0.8-cloud-run`
- Artifact Registry repository: `alte-ai-crm`
- Cloud SQL attachment: `CLOUD_SQL_ATTACHED`
- Cloud SQL connection: `project-1e145fd0-c30e-4aac-a34:europe-west1:alte-ai-crm-db`
- Secret Manager mapping: `SECRET_MANAGER_MAPPED`
- `DATABASE_URL`, `JWT_SECRET`, and `ANTHROPIC_API_KEY` are mapped from Secret Manager and are not documented as values.
- Unauthenticated access: enabled for the public website widget API surface.

Verification:

- `/health: 200`
- `/version: 200`
- `/diagnostics/ai: 200`
- `/diagnostics/local-demo: 200`
- `/dashboard/overview: 401` because `AUTH_REQUIRED=true` and no bearer token was supplied.

Launch blockers:

- Website admin/developer access pending.
- Privacy/data approval pending.
- Actual website widget embed pending.
- Production widget smoke from `alte.edu.ge` / `join.alte.edu.ge` pending.
