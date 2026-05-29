# Phase 9W - Chat Session Start 500 Root Cause

## Failing Endpoint

`POST /chat/session/start`

Production backend:

`https://alte-ai-crm-backend-226875230147.europe-west1.run.app`

Origin:

`https://nimble-croissant-2f66e8.netlify.app`

## Safe Payload Used

```json
{
  "source_domain": "join.alte.edu.ge",
  "language": "en",
  "channel": "website_chat",
  "widget_variant": "pro_v2_safe",
  "metadata": {
    "mode": "diagnosis",
    "page_url": "https://nimble-croissant-2f66e8.netlify.app/join.html"
  }
}
```

No phone, email, contact details, lead, task, or customer creation flow was used.

## Status

- HTTP status: `500`
- CORS header: present after Phase 9V
- Browser classification: no longer a CORS allowlist issue

## Sanitized Exception

Cloud Run logs show:

`asyncpg.exceptions.InvalidPasswordError`

Sanitized stack frame path:

- `/app/app/api/routes_chat.py`
- `/app/app/services/chat_service.py`
- SQLAlchemy asyncpg connection checkout/flush path

The exception occurs during `start_session()` when the backend attempts to flush the new `Conversation` and open a PostgreSQL connection.

## Root Cause

Production database authentication is failing for the application DB user.

This is a DB credential / Secret Manager configuration issue, not a frontend payload issue and not a CORS issue.

## Affected Files

Runtime path:

- `backend/app/api/routes_chat.py`
- `backend/app/services/chat_service.py`
- `backend/app/core/database.py`
- production Cloud Run DB secret/env configuration

Code note:

- `ChatSessionStartRequest` now explicitly accepts optional `widget_variant` and `metadata` so the Pro v2 payload is formally supported.
- This schema support does not fix the production 500 because the production error happens at DB authentication.

## Fix Classification

`secret_or_db_credential`

## Approval Requirement

Production fix requires explicit approval to inspect/repair the production DB credential or Secret Manager mapping.

Do not change Secret Manager, DB users/passwords, migrations, seed data, or production DB without the next explicit approval.
