# Local Secret Values Preparation

This phase prepares local-only secret values. It does not create Secret Manager secrets and does not create Google Cloud resources.

Never paste secrets into chat, screenshots, GitHub, docs, prompts, or shared tickets.

## Local Storage Warning

`.local-secrets/` is ignored by Git, but it must still be treated as sensitive. Keep it local, temporary, and outside screenshots or shared archives.

Prefer storing final values in a password manager until the Secret Manager execution phase.

## DB Password

Purpose:

Cloud SQL app user password for `alte_app`.

Generate locally using a password manager or secure local generator. Do not save the value in docs.

The helper script can prepare a local placeholder file:

```powershell
.\scripts\prepare_local_secret_values.ps1
```

## JWT Secret

Purpose:

JWT signing secret for production auth.

Suggested local PowerShell generation:

```powershell
[Convert]::ToBase64String((1..48 | ForEach-Object { Get-Random -Maximum 256 }))
```

Store the generated value in a password manager or Secret Manager during execution.

## Anthropic API Key Readiness

The helper script never asks for and never prints the Anthropic API key.

To verify local readiness without printing the key, check that `backend/.env` contains an `ANTHROPIC_API_KEY` line manually, or use an editor search. Do not copy the value into docs or chat.

If the key was ever exposed, revoke and rotate it in Anthropic Console before production use.

## DATABASE_URL

`DATABASE_URL` remains pending until the Cloud SQL instance exists and its connection method is selected.

Production format:

```text
postgresql+asyncpg://alte_app:DB_PASSWORD@HOST:5432/alte_ai_crm
```

Store the final value only in Secret Manager as `alte-database-url`.

## Status Checklist

- DB password generated: `yes/no`
- JWT secret generated: `yes/no`
- Anthropic key available: `yes/no`
- `DATABASE_URL` pending until Cloud SQL instance exists: `yes`

Current status: `LOCAL_SECRET_VALUES_PREPARED_FOR_USER_ACTION`
