# Secret Values Runbook

## A. Required Secrets

| Secret name | Purpose | Status |
| --- | --- | --- |
| `alte-db-password` | PostgreSQL app user password | NOT_CREATED / PENDING |
| `alte-database-url` | Full production SQLAlchemy async PostgreSQL URL | NOT_CREATED / PENDING |
| `alte-jwt-secret` | JWT signing secret | NOT_CREATED / PENDING |
| `alte-anthropic-api-key` | Anthropic Claude API key | NOT_CREATED / PENDING |

## B. Generate Values Safely

### DB Password

- Generate locally with a password manager or secure generator.
- Do not paste it into chat.
- Do not commit it.
- Store it only in Secret Manager and the temporary secure local workflow used to create the secret.

### JWT Secret

Generate a long random value locally. PowerShell example that prints locally only:

```powershell
[Convert]::ToBase64String((1..48 | ForEach-Object { Get-Random -Maximum 256 }))
```

### Anthropic API Key

- Create in Anthropic Console.
- If a key is ever pasted into chat, revoke and rotate it.
- Store it only in Secret Manager and local `.env` for controlled local testing.

### DATABASE_URL

Build from Cloud SQL connection details. Do not write the real password in docs.

```env
postgresql+asyncpg://USER:PASSWORD@HOST:5432/DB_NAME
```

## C. gcloud Commands Template

Documentation only. Do not run until approved.

```powershell
gcloud secrets create alte-db-password --replication-policy=automatic
gcloud secrets create alte-database-url --replication-policy=automatic
gcloud secrets create alte-jwt-secret --replication-policy=automatic
gcloud secrets create alte-anthropic-api-key --replication-policy=automatic
```

Add secret versions using local files or interactive input. Do not put real values directly into commands in docs.

## D. Verification

List secrets without printing values:

```powershell
gcloud secrets list
gcloud secrets versions list SECRET_NAME
```

## E. Status

- `alte-db-password`: NOT_CREATED / PENDING
- `alte-database-url`: NOT_CREATED / PENDING
- `alte-jwt-secret`: NOT_CREATED / PENDING
- `alte-anthropic-api-key`: NOT_CREATED / PENDING
