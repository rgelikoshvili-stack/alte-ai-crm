# Phase 9W - Secret Or DB Credential Approval Required

PHASE_9W_SECRET_OR_DB_CREDENTIAL_STATUS=APPROVAL_REQUIRED

## Reason

`POST /chat/session/start` reaches the backend and attempts to create a chat conversation, but production logs show a sanitized PostgreSQL authentication failure:

`asyncpg.exceptions.InvalidPasswordError`

The failing operation is DB connection/flush during `start_session()`.

## Required Future Approval

Before fixing production, the user must explicitly approve a credential repair phase, for example:

`Approve Phase 9W-DB-Credential-Fix: inspect and repair production DATABASE_URL/DB user Secret Manager mapping`

## Future Work Scope After Approval

- Read current Cloud Run Secret Manager mapping safely.
- Confirm which secret provides the production DB URL/credential.
- Verify the Cloud SQL user credential without printing it.
- Update only the broken credential/mapping if required.
- Redeploy or update Cloud Run only if required.
- Re-run `/chat/session/start` and `/chat/message` safe smoke.

## Explicitly Not Done In This Phase

- Secret Manager changed: NO
- Production DB password/user changed: NO
- Production DB modified: NO
- Migration/seed run: NO
- Contact details sent: NO
- Lead/task/customer intentionally created: NO
- Public launch: NO
