# Phase 9W DB Credential Fix Result

PHASE_9W_DB_CREDENTIAL_FIX_STATUS=FIXED_PENDING_BROWSER_RETEST

Decision state:

BACKEND_DEPLOYED_DB_CREDENTIAL_FIXED_CHAT_READY_PENDING_BROWSER_RETEST

## Root Cause Summary

`POST /chat/session/start` failed with `asyncpg.exceptions.InvalidPasswordError` because the production Cloud SQL app user's password did not match the active `DATABASE_URL` Secret Manager credential.

## Fix Type

`db_user_password_repair_to_match_active_secret`

Actions:

- Inspected Cloud Run env/Secret Manager mapping without printing secret values.
- Confirmed `DATABASE_URL` maps to `alte-database-url`.
- Confirmed Cloud SQL attachment exists.
- Updated the Cloud SQL app user password to match the active `alte-database-url:latest` credential, with the password handled in memory and not printed.
- Confirmed Cloud Run mapping uses `DATABASE_URL=alte-database-url:latest`.

## Deployment

- Cloud Run deploy/config update happened: YES
- New separate revision name: Cloud Run kept serving `alte-ai-crm-backend-00016-2gk` after config update.
- Current serving revision: `alte-ai-crm-backend-00016-2gk`

## Production Smoke Result

- `/health`: 200
- `/diagnostics/ai`: 200, Claude enabled
- `/chat/session/start`: 200
- `/chat/session/start` CORS: exact origin `https://nimble-croissant-2f66e8.netlify.app`
- `/chat/message`: success in production DB credential smoke
- Production Netlify public chat CORS smoke: PASS
- Production department routing sidebar smoke: PASS `28/28`
- Production finance no-contact smoke: `21/22` passed; one deadline case timed out during read. No contact details were sent and no intentional lead/task creation occurred.
- Production knowledge smoke: `24/25` passed; one deadline conservativeness assertion needs review. No contact details were sent and no intentional lead/task creation occurred.
- Contact details sent: NO
- Contact-flow test run: NO
- Lead/task/customer intentionally created: NO

## Safety

- Secret Manager payload changed: NO
- Secret values printed: NO
- `DATABASE_URL` printed: NO
- DB migration run: NO
- DB seed run: NO
- DB schema changed: NO
- DB data changed: NO
- Real Alte site modified: NO
- Frontend design changed: NO
- Public launch: NO

## Next Step

Manual browser retest:

`https://nimble-croissant-2f66e8.netlify.app/join.html`
