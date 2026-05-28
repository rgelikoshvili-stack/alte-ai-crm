# Phase 9S - Pro v2 Message Endpoint and CORS Fix

PHASE_9S_PRO_V2_MESSAGE_ENDPOINT_CORS_FIX_STATUS=READY_PENDING_NETLIFY_REDEPLOY_AND_BROWSER_RETEST

Decision state:

BACKEND_DEPLOYED_PRO_V2_MESSAGE_ENDPOINT_CORS_FIXED_PENDING_NETLIFY_REDEPLOY

## Browser Error Summary

Hosted Netlify Pro v2 page:

`https://nimble-croissant-2f66e8.netlify.app/join.html`

The browser attempted requests to:

`/chat/messages/...`

Those requests are not part of the approved browser chat message flow and were blocked by CORS in the browser.

## Root Cause

- The active test widget bridge in `test_site/alte-ai-chat-widget.html` still included operator polling through `GET /chat/messages/{conversation_id}`.
- The approved frontend browser message endpoints are only:
  - `POST /chat/session/start`
  - `POST /chat/message`
- The backend still has transcript support for controlled operator reply polling, but this Phase keeps the hosted test widget on the approved two-endpoint browser flow.

## Fix

- Removed `/chat/messages` polling from the test widget bridge.
- Preserved session start endpoint:
  - `/chat/session/start`
- Preserved message endpoint:
  - `/chat/message`
- Session payload keeps:
  - `channel: website_chat`
  - `widget_variant: pro_v2_safe`
  - `source_domain`
  - `language`
  - `metadata.page_url`
- Message payload keeps:
  - `conversation_id`
  - `session_id`
  - `message`
  - `language`
  - `source_domain`
  - `selected_department`
  - `selected_topic`
  - `widget_variant: pro_v2_safe`

## CORS Smoke Result

CORS smoke script:

`backend/app/scripts/production_netlify_pro_v2_cors_smoke.py`

Status:

`FAILED_NEEDS_REVIEW`

Details:

- OPTIONS/preflight is covered for:
  - `/chat/session/start`
  - `/chat/message`
- POST session/message checks are blocked by the current production DB credential mismatch:
  - Cloud Run logs show `InvalidPasswordError` for DB user `alte_app`
- This is not fixed in this phase because DB/Secret Manager changes are explicitly out of scope.

## Deployment Package

Rebuilt Netlify ZIP:

`dist/netlify_test_site_deploy.zip`

ZIP root includes:

- `index.html`
- `join.html`
- `alte-ai-chat-widget.js`
- `alte-ai-chat-widget.html`
- `_redirects`
- `README_GEO.md`
- `NETLIFY_DEPLOY_README_GEO.md`

## Status

- Netlify redeploy required: YES
- Browser smoke pending manual retest
- Real Alte site modified: NO
- Production DB modified: NO
- Contact details sent: NO
- Intentional lead/task/customer creation: NO
- Public launch: NO
