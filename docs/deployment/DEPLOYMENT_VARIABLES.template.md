# Deployment Variables Template

Fill this file only with non-secret deployment planning values. Do not put real passwords or API keys here.

## Current Draft

| Variable | Planned value | Status / note |
| --- | --- | --- |
| `PROJECT_ID` | `project-1e145fd0-c30e-4aac-a34` | User-provided Google Cloud project ID. |
| `REGION` | `europe-west1` | User-confirmed region. |
| `SERVICE_NAME` | `alte-ai-crm-backend` | Safe default. |
| `ARTIFACT_REPOSITORY` | `alte-ai-crm` | Safe default. |
| `IMAGE_NAME` | `alte-ai-crm-backend` | Safe default. |
| `IMAGE_TAG` | `v0.8-production-prep` | Safe deployment-prep tag. |
| `CLOUD_SQL_INSTANCE` | `alte-ai-crm-db` | Safe default; cost/tier must be approved before creation. |
| `DB_NAME` | `alte_ai_crm` | Safe default. |
| `DB_USER` | `alte_app` | Safe default app user. |
| `DB_PASSWORD_SECRET` | `alte-db-password` | Secret Manager name only; do not store password here. |
| `DATABASE_URL_SECRET` | `alte-database-url` | Secret Manager name only; stores full production DB URL later. |
| `JWT_SECRET_NAME` | `alte-jwt-secret` | Secret Manager name only. |
| `ANTHROPIC_SECRET_NAME` | `alte-anthropic-api-key` | Secret Manager name only. |
| `CORS_ORIGINS` | `https://alte.edu.ge,https://join.alte.edu.ge` | User-confirmed production origins. |
| `GITHUB_REMOTE_URL` | `https://github.com/rgelikoshvili-stack/alte-ai-crm` | User-provided repository URL. |
| `BILLING_STATUS` | `enabled` | User-confirmed. |

## Values Needed From Project Owner

- Confirm GitHub push permissions.
- Confirm release tag name.
- Confirm Cloud SQL instance tier/cost
- Confirm Alte website admin/developer access
- Confirm whether `join.alte.edu.ge` is included at first launch. Current draft includes it.

## Notes

- This is a template only.
- Do not commit real database passwords.
- Do not commit real Anthropic API keys.
- Do not paste secrets into chat or screenshots.
- Store secrets in Secret Manager.
