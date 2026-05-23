# Environment Variables

## Reference Table

| Variable | Required local | Required production | Example | Description | Secret |
| --- | --- | --- | --- | --- | --- |
| `DATABASE_URL` | Yes | Yes | `sqlite+aiosqlite:///./alte_ai_crm_local.db` | Database connection URL | Yes in production |
| `JWT_SECRET` | Yes | Yes | `local-dev-secret` | JWT signing secret | Yes |
| `ANTHROPIC_API_KEY` | Placeholder for mock, real for Claude | Yes | `your-real-key` | Anthropic Claude API key | Yes |
| `ENVIRONMENT` | Yes | Yes | `development` | Runtime environment label | No |
| `APP_VERSION` | Yes | Yes | `0.1.0` | App version shown by `/version` | No |
| `AUTH_REQUIRED` | Yes | Yes | `false` | Enables auth/RBAC middleware | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Yes | Yes | `480` | Login token lifetime | No |
| `AI_PROVIDER` | Yes | Yes | `mock` or `claude` | Selects mock or Claude AI provider | No |
| `AI_MODEL` | Yes | Yes | `claude-sonnet-4-5` | Claude model name | No |
| `AI_TIMEOUT_SECONDS` | Yes | Yes | `20` | AI request timeout | No |
| `AI_CONFIDENCE_THRESHOLD` | Yes | Yes | `0.70` | Below this, force safe handover | No |
| `AI_MAX_TOKENS` | Yes | Yes | `1200` | Max Claude output tokens | No |
| `CORS_ORIGINS` | Yes | Yes | `http://127.0.0.1:5500` | Comma-separated allowed origins | No |

## Local Mock Example

```env
DATABASE_URL=sqlite+aiosqlite:///./alte_ai_crm_local.db
JWT_SECRET=local-dev-secret
ANTHROPIC_API_KEY=local-placeholder
ENVIRONMENT=development
APP_VERSION=0.1.0
AUTH_REQUIRED=false
ACCESS_TOKEN_EXPIRE_MINUTES=480
AI_PROVIDER=mock
AI_MODEL=claude-sonnet-4-5
AI_TIMEOUT_SECONDS=20
AI_CONFIDENCE_THRESHOLD=0.70
AI_MAX_TOKENS=1200
CORS_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
```

## Local Claude Example

```env
DATABASE_URL=sqlite+aiosqlite:///./alte_ai_crm_local.db
JWT_SECRET=local-dev-secret
ANTHROPIC_API_KEY=your-real-key
ENVIRONMENT=development
APP_VERSION=0.1.0
AUTH_REQUIRED=false
ACCESS_TOKEN_EXPIRE_MINUTES=480
AI_PROVIDER=claude
AI_MODEL=claude-sonnet-4-5
AI_TIMEOUT_SECONDS=20
AI_CONFIDENCE_THRESHOLD=0.70
AI_MAX_TOKENS=1200
CORS_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
```

## Production Example

```env
DATABASE_URL=postgresql+asyncpg://...
JWT_SECRET=from-secret-manager
ANTHROPIC_API_KEY=from-secret-manager
ENVIRONMENT=production
APP_VERSION=0.1.0
AUTH_REQUIRED=true
ACCESS_TOKEN_EXPIRE_MINUTES=480
AI_PROVIDER=claude
AI_MODEL=claude-sonnet-4-5
AI_TIMEOUT_SECONDS=20
AI_CONFIDENCE_THRESHOLD=0.70
AI_MAX_TOKENS=1200
CORS_ORIGINS=https://alte.edu.ge,https://join.alte.edu.ge
```

Production values marked as secrets must be stored in Secret Manager or an equivalent secret store, not in source control.
