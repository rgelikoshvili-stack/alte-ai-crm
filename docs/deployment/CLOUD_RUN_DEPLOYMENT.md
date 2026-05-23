# Cloud Run Deployment Guide

This guide prepares Alte AI CRM for a future Google Cloud Run deployment. It does not require or perform deployment by itself.

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
