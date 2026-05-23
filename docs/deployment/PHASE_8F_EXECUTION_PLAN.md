# Phase 8F Execution Plan

Do not run until the user explicitly approves actual cloud resource creation.

This plan is for the next phase. Phase 8F-Prep creates the checklist only.

## A. Pre-Check Commands

```powershell
cd C:\tmp\alte-ai-crm
git status --short --branch

cd C:\tmp\alte-ai-crm\backend
python -m app.scripts.verify_release_checkpoint
python -m app.scripts.verify_deployment_docs
python -m app.scripts.verify_final_preflight
python -m app.scripts.verify_phase_8e_readiness
python -m app.scripts.verify_phase_8f_prep
```

## B. gcloud Project Setup

```powershell
gcloud auth login
gcloud config set project project-1e145fd0-c30e-4aac-a34
```

## C. API Enablement Commands

```powershell
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

## D. Cloud SQL Creation Command Template

Review tier, cost, storage, backups and high availability before execution.

```powershell
gcloud sql instances create alte-ai-crm-db `
  --database-version=POSTGRES_16 `
  --tier=REVIEW_AND_SELECT_TIER `
  --region=europe-west1

gcloud sql databases create alte_ai_crm --instance=alte-ai-crm-db
gcloud sql users create alte_app --instance=alte-ai-crm-db --password="DO_NOT_PUT_REAL_PASSWORD_IN_DOCS"
```

## E. Secret Manager Creation Command Template

Use placeholders only. Do not put real values directly in docs.

```powershell
gcloud secrets create alte-db-password --replication-policy=automatic
gcloud secrets create alte-database-url --replication-policy=automatic
gcloud secrets create alte-jwt-secret --replication-policy=automatic
gcloud secrets create alte-anthropic-api-key --replication-policy=automatic
```

Add secret versions from local files or interactive input that are not committed.

## F. Docker Build / Push Plan

Use Artifact Registry for container image publishing.

Recommended split: Phase 8G or later, after Cloud SQL and Secret Manager are ready.

## G. Cloud Run Deploy Plan

Cloud Run deployment should be Phase 8G/8H, not Phase 8F-Prep.

## H. Rollback Notes

- Use Cloud Run revision rollback.
- Do not delete the database as rollback.
- Keep previous image tag.
- Prepare secrets rotation plan.
