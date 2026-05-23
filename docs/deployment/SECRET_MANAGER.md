# Secret Manager Mapping

Production secrets must be stored in Google Cloud Secret Manager, not in `.env` files or source control.

## Secrets

| Secret name | Env variable | Description | Required production |
| --- | --- | --- | --- |
| `alte-database-url` | `DATABASE_URL` | PostgreSQL async SQLAlchemy URL | Yes |
| `alte-jwt-secret` | `JWT_SECRET` | JWT signing secret | Yes |
| `alte-anthropic-api-key` | `ANTHROPIC_API_KEY` | Anthropic Claude API key | Yes |

## Non-Secret Environment Variables

| Env variable | Example |
| --- | --- |
| `ENVIRONMENT` | `production` |
| `APP_VERSION` | `0.8.0` |
| `AUTH_REQUIRED` | `true` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `120` |
| `AI_PROVIDER` | `claude` |
| `AI_MODEL` | `claude-sonnet-4-5-20250929` |
| `AI_TIMEOUT_SECONDS` | `20` |
| `AI_CONFIDENCE_THRESHOLD` | `0.70` |
| `AI_MAX_TOKENS` | `1200` |
| `CORS_ORIGINS` | `https://alte.edu.ge,https://join.alte.edu.ge` |

## Placeholder Commands

```powershell
gcloud secrets create alte-database-url --project PROJECT_ID
gcloud secrets versions add alte-database-url --data-file=database-url.txt --project PROJECT_ID

gcloud secrets create alte-jwt-secret --project PROJECT_ID
gcloud secrets versions add alte-jwt-secret --data-file=jwt-secret.txt --project PROJECT_ID

gcloud secrets create alte-anthropic-api-key --project PROJECT_ID
gcloud secrets versions add alte-anthropic-api-key --data-file=anthropic-api-key.txt --project PROJECT_ID
```

The files above must be local temporary files and must not be committed.
