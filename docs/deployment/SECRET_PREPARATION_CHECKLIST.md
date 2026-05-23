# Secret Preparation Checklist

Secret creation must happen only after:

- Cloud SQL pilot tier is approved.
- Cloud SQL instance creation is explicitly approved.
- User confirms Phase 8F-Execution.

Cloud SQL pilot tier is now approved, so the next required step is secret values preparation and Secret Manager creation approval.

## Required Secrets

### 1. `alte-db-password`

- [ ] Generated locally.
- [ ] Not pasted into chat.
- [ ] Not committed.
- [ ] Stored in password manager or secure local note until Secret Manager creation.

### 2. `alte-database-url`

- [ ] Built only after Cloud SQL host/connection info is known.
- [ ] Not committed.
- [ ] Uses PostgreSQL async format:

```env
postgresql+asyncpg://USER:PASSWORD@HOST:5432/alte_ai_crm
```

### 3. `alte-jwt-secret`

- [ ] Generated locally.
- [ ] Long random value.
- [ ] Not committed.

### 4. `alte-anthropic-api-key`

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
