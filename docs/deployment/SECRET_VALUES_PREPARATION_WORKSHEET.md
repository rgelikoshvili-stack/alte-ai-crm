# Secret Values Preparation Worksheet

This worksheet is for planning only. Never write real secret values into this file, Git, screenshots, chat messages, or shared documents.

## A. `alte-db-password`

Purpose:

Cloud SQL app user password for `DB_USER=alte_app`.

Preparation:

- Generate locally using a password manager or secure generator.
- Do not paste the password into chat.
- Do not save the password in Git or documentation.
- Store the password temporarily in a password manager until Secret Manager creation.

Status: `PENDING_USER_GENERATION`

## B. `alte-jwt-secret`

Purpose:

JWT signing secret for backend authentication.

Preparation:

- Generate a long random value locally.
- Do not paste it into chat.
- Do not save it in docs.
- Store it in Secret Manager for production.

Suggested local PowerShell generation:

```powershell
[Convert]::ToBase64String((1..48 | ForEach-Object { Get-Random -Maximum 256 }))
```

Status: `PENDING_USER_GENERATION`

## C. `alte-anthropic-api-key`

Purpose:

Claude API access for `AI_PROVIDER=claude`.

Preparation:

- Create or rotate the key in Anthropic Console.
- If the key was ever exposed in chat or screenshot, revoke and rotate it.
- Store it only in local `.env` for local testing and Secret Manager for production.

Status: `PENDING_USER_CONFIRMATION`

## D. `alte-database-url`

Purpose:

SQLAlchemy async PostgreSQL connection string for production.

Depends on:

- Cloud SQL instance host or connection method.
- DB password.
- DB user.
- DB name.

Format:

```text
postgresql+asyncpg://alte_app:DB_PASSWORD@HOST:5432/alte_ai_crm
```

Status: `PENDING_CLOUD_SQL_CREATION`

## Strong Warning

Never write real secret values into this worksheet. The final values must be entered only into Secret Manager or a secure local password manager.

## Local Preparation Step

Local secret values preparation is ready:

- Guide: `LOCAL_SECRET_VALUES_PREP.md`
- Helper script: `scripts/prepare_local_secret_values.ps1`

The helper creates only local ignored files when the user explicitly confirms. It does not create Secret Manager secrets and does not call `gcloud`.
