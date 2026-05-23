# Production Environment Mapping

| Env var | Source | Production value / placeholder | Required | Secret | Validation rule | Current status |
| --- | --- | --- | --- | --- | --- | --- |
| `DATABASE_URL` | Secret Manager | `alte-database-url` | Yes | Yes | Must be PostgreSQL async URL | Pending secret creation |
| `JWT_SECRET` | Secret Manager | `alte-jwt-secret` | Yes | Yes | Must be non-placeholder long random value | Pending secret creation |
| `ANTHROPIC_API_KEY` | Secret Manager | `alte-anthropic-api-key` | Yes | Yes | Must be non-placeholder Anthropic key | Pending secret creation |
| `ENVIRONMENT` | Plain env var | `production` | Yes | No | Must equal `production` | Planned |
| `APP_VERSION` | Plain env var | `0.8.0` | Yes | No | Non-empty version | Planned |
| `AUTH_REQUIRED` | Plain env var | `true` | Yes | No | Must be true in production | Planned |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Plain env var | `120` | Yes | No | Positive integer | Planned |
| `AI_PROVIDER` | Plain env var | `claude` | Yes | No | Must be `claude` for production | Planned |
| `AI_MODEL` | Plain env var | `claude-sonnet-4-5-20250929` | Yes | No | Current Sonnet model ID | Planned |
| `AI_TIMEOUT_SECONDS` | Plain env var | `20` | Yes | No | Positive integer | Planned |
| `AI_CONFIDENCE_THRESHOLD` | Plain env var | `0.70` | Yes | No | Float between 0 and 1 | Planned |
| `AI_MAX_TOKENS` | Plain env var | `1200` | Yes | No | Positive integer | Planned |
| `CORS_ORIGINS` | Plain env var | `https://alte.edu.ge,https://join.alte.edu.ge` | Yes | No | No wildcard in production | Confirmed draft |

## Secret Preparation References

- Use `SECRET_VALUES_PREPARATION_WORKSHEET.md` to track which secret values the user must prepare locally.
- Use `SECRET_MANAGER_APPROVAL_GATE.md` before any Secret Manager creation.
- Use `DATABASE_URL_CONSTRUCTION.md` to build the final PostgreSQL async URL after Cloud SQL connection details are known.
- Use `scripts/prepare_secret_values.ps1` for local guidance only. It does not create secrets or call `gcloud`.

All secret-backed env vars remain pending until Secret Manager creation is explicitly approved and completed.
