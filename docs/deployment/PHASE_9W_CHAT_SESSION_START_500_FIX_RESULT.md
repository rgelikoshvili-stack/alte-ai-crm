# Phase 9W - Chat Session Start 500 Diagnosis Result

PHASE_9W_CHAT_SESSION_START_STATUS=BLOCKED_PENDING_DB_OR_SECRET_APPROVAL

Decision state:

BACKEND_DEPLOYED_CHAT_SESSION_START_500_DIAGNOSED_PENDING_APPROVAL

## Root Cause

`POST /chat/session/start` returns backend `500` because production PostgreSQL authentication fails when the service attempts to create/flush a new `Conversation`.

Sanitized exception type:

`asyncpg.exceptions.InvalidPasswordError`

This is not a CORS issue. Phase 9V restored exact-origin CORS headers, including on backend error responses.

## Fix Summary

No production credential fix was performed in this phase because the user rules prohibit Secret Manager, DB credential, production DB, migration, and seed changes without explicit approval.

Safe code/docs updates prepared:

- Added a production diagnosis script.
- Explicitly allowed `widget_variant` and `metadata` in the session start schema.
- Added root-cause and approval-required docs.
- Added Phase 9W tests and verifier.

## Backend Redeploy

Backend redeploy required for credential fix: YES, after approval if Cloud Run config/Secret mapping is changed.

Backend redeploy performed in this phase: NO.

Current serving revision remains:

`alte-ai-crm-backend-00016-2gk`

## Production Diagnosis

- Endpoint: `/chat/session/start`
- Safe origin: `https://nimble-croissant-2f66e8.netlify.app`
- Status: `500`
- CORS header: present
- Contact details sent: NO
- Lead/task/customer intentionally created: NO

## Chat Message Smoke

`/chat/message` smoke is blocked because session start does not return a valid `conversation_id` until DB credential repair is approved and completed.

## Safety

- DB migration/seed run: NO
- Production DB modified: NO
- Secret Manager changed: NO
- Real Alte site modified: NO
- Contact details sent: NO
- Lead/task/customer intentionally created: NO
- Public launch: NO
