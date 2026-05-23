# Deployment Variables Template

Fill this file only with non-secret deployment planning values. Do not put real passwords or API keys here.

| Variable | Planned value |
| --- | --- |
| `PROJECT_ID` | `YOUR_PROJECT_ID` |
| `REGION` | `europe-west1` or `europe-west3` |
| `SERVICE_NAME` | `alte-ai-crm-backend` |
| `ARTIFACT_REPOSITORY` | `alte-ai-crm` |
| `IMAGE_NAME` | `alte-ai-crm-backend` |
| `IMAGE_TAG` | `v0.8-production-prep` |
| `CLOUD_SQL_INSTANCE` | `alte-ai-crm-db` |
| `DB_NAME` | `alte_ai_crm` |
| `DB_USER` | `alte_app` |
| `DB_PASSWORD_SECRET` | `alte-db-password` |
| `DATABASE_URL_SECRET` | `alte-database-url` |
| `JWT_SECRET_NAME` | `alte-jwt-secret` |
| `ANTHROPIC_SECRET_NAME` | `alte-anthropic-api-key` |
| `CORS_ORIGINS` | `https://alte.edu.ge,https://join.alte.edu.ge` |

Notes:

- This is a template only.
- Do not commit real database passwords.
- Do not commit real Anthropic API keys.
- Store secrets in Secret Manager.
