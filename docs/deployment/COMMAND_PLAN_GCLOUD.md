# Google Cloud Command Plan

Do not run these commands until values are reviewed.

This file is a command template only. It does not contain real secrets.

## A. Set Variables In PowerShell

```powershell
$PROJECT_ID="your-project-id"
$REGION="europe-west1"
$SERVICE_NAME="alte-ai-crm-backend"
$REPOSITORY="alte-ai-crm"
$IMAGE_NAME="alte-ai-crm-backend"
$IMAGE_TAG="v0.8-production-prep"
```

## B. Configure gcloud

```powershell
gcloud auth login
gcloud config set project $PROJECT_ID
```

## C. Enable APIs

```powershell
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable iam.googleapis.com
```

## D. Create Artifact Registry Repository

```powershell
gcloud artifacts repositories create $REPOSITORY --repository-format=docker --location=$REGION
```

## E. Build And Push Image

```powershell
gcloud builds submit ./backend --tag "$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_NAME:$IMAGE_TAG"
```

## F. Create Cloud SQL PostgreSQL Instance

Review cost, region, storage, backup and tier before running.

```powershell
gcloud sql instances create alte-ai-crm-db --database-version=POSTGRES_16 --tier=db-f1-micro --region=$REGION
gcloud sql databases create alte_ai_crm --instance=alte-ai-crm-db
gcloud sql users create alte_app --instance=alte-ai-crm-db --password="DO_NOT_PUT_REAL_PASSWORD_IN_DOCS"
```

## G. Secret Manager

```powershell
gcloud secrets create alte-database-url --replication-policy=automatic
gcloud secrets create alte-jwt-secret --replication-policy=automatic
gcloud secrets create alte-anthropic-api-key --replication-policy=automatic
```

Add secret versions interactively or from local files that are not committed.

## H. Deploy Cloud Run

```powershell
gcloud run deploy $SERVICE_NAME `
  --image "$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_NAME:$IMAGE_TAG" `
  --region $REGION `
  --platform managed `
  --allow-unauthenticated `
  --port 8080 `
  --set-env-vars ENVIRONMENT=production,APP_VERSION=0.8.0,AUTH_REQUIRED=true,AI_PROVIDER=claude,AI_MODEL=claude-sonnet-4-5-20250929,AI_TIMEOUT_SECONDS=20,AI_CONFIDENCE_THRESHOLD=0.70,AI_MAX_TOKENS=1200,CORS_ORIGINS=https://alte.edu.ge,https://join.alte.edu.ge `
  --set-secrets DATABASE_URL=alte-database-url:latest,JWT_SECRET=alte-jwt-secret:latest,ANTHROPIC_API_KEY=alte-anthropic-api-key:latest
```

## I. Post Deploy Checks

```text
GET /health
GET /diagnostics/ai
GET /dashboard/overview
```

## J. Migration Strategy

Option 1: one-off Cloud Run job or temporary command.

Option 2: local migration through an authorized Cloud SQL connection.

Do not implement or run the migration job until it is separately approved.
