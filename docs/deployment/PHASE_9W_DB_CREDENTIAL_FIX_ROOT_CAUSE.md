# Phase 9W DB Credential Fix Root Cause

## Failing Exception

`asyncpg.exceptions.InvalidPasswordError`

## Configuration Inspection

- Expected app DB env var: `DATABASE_URL`
- Code path: `backend/app/core/config.py` -> `backend/app/core/database.py`
- DB driver format expected by app: SQLAlchemy async PostgreSQL URL
- Cloud Run service: `alte-ai-crm-backend`
- Cloud Run region: `europe-west1`
- Cloud SQL attachment: present
- Cloud SQL instance: `project-1e145fd0-c30e-4aac-a34:europe-west1:alte-ai-crm-db`
- Cloud Run `DATABASE_URL` mapping before repair: `Secret Manager / alte-database-url / latest`
- Relevant DB secret versions: `1` enabled, `2` enabled

Secret payload values were not printed.

## Root Cause Type

`D. DB user password was rotated but secret not updated or DB user password no longer matched the active Secret Manager DATABASE_URL credential.`

The active secret mapping existed and used the expected env var name. The code expected `DATABASE_URL` correctly. Cloud SQL attachment existed. The failure happened only when opening the PostgreSQL connection during chat session creation.

## Fix Type

Credential repair:

- Read active `alte-database-url` secret value in memory only.
- Parsed only the DB username/password in memory.
- Updated the Cloud SQL app user's password to match the active secret value.
- Restored/confirmed Cloud Run `DATABASE_URL` mapping to `alte-database-url:latest`.

No secret payload was printed.

## Production Approval

The user explicitly approved:

`Phase 9W-DB-Credential-Fix: Inspect and repair production DATABASE_URL / DB user Secret Manager mapping.`

## Production Change Classification

- Config/credential repair: YES
- Secret Manager payload changed: NO
- Cloud SQL DB user password changed: YES
- DB schema changed: NO
- DB data changed: NO
- Migration run: NO
- Seed run: NO
