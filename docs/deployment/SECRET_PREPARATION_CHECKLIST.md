# Secret Preparation Checklist

Secret creation must happen only after:

- Cloud SQL pilot tier is approved.
- Cloud SQL instance creation is explicitly approved.
- User confirms Phase 8F-Execution.

Cloud SQL pilot tier is now approved, so the next required step is secret values preparation and Secret Manager creation approval.

Secret Manager creation approval: `APPROVED_FOR_NEXT_EXECUTION`

Use these Phase 8F-Secrets-Prep references before execution:

- `SECRET_VALUES_PREPARATION_WORKSHEET.md`
- `SECRET_MANAGER_APPROVAL_GATE.md`
- `DATABASE_URL_CONSTRUCTION.md`
- `scripts/prepare_secret_values.ps1`
- `LOCAL_SECRET_VALUES_PREP.md`
- `scripts/prepare_local_secret_values.ps1`

## Required Secrets

### 1. `alte-db-password`

Status: `NOT_CREATED / PENDING_USER_GENERATION`

- [ ] Generated locally.
- [ ] Not pasted into chat.
- [ ] Not committed.
- [ ] Stored in password manager or secure local note until Secret Manager creation.

### 2. `alte-database-url`

Status: `NOT_CREATED / PENDING_CLOUD_SQL_CREATION`

- [ ] Built only after Cloud SQL host/connection info is known.
- [ ] Not committed.
- [ ] Uses PostgreSQL async format:

```env
postgresql+asyncpg://USER:PASSWORD@HOST:5432/alte_ai_crm
```

### 3. `alte-jwt-secret`

Status: `NOT_CREATED / PENDING_USER_GENERATION`

- [ ] Generated locally.
- [ ] Long random value.
- [ ] Not committed.

### 4. `alte-anthropic-api-key`

Status: `NOT_CREATED / PENDING_USER_CONFIRMATION`

- [ ] Created in Anthropic Console.
- [ ] If ever exposed, revoked and rotated.
- [ ] Stored only in Secret Manager and local `.env` if needed.

## Final Secret Safety Checks

- [ ] DB password prepared.
- [ ] JWT secret prepared.
- [ ] Anthropic key prepared.
- [ ] `DATABASE_URL` prepared.
- [ ] None pasted into chat.
- [ ] None saved in docs.
- [ ] None committed.
- [ ] Secret Manager creation explicitly approved.
- [ ] Local secret values preparation completed, if using the helper script.
- [ ] Real secret values entered only into Secret Manager or a password manager.
