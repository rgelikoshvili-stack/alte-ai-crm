# Phase 9S - Pro v2 Message 500 Flow Fix

PHASE_9S_MESSAGE_500_FIX_STATUS=READY_PENDING_NETLIFY_REDEPLOY_AND_BROWSER_RETEST

Decision state:

BACKEND_DEPLOYED_PRO_V2_MESSAGE_500_FIXED_PENDING_NETLIFY_REDEPLOY

## Browser Error Summary

Observed test URL:

`https://nimble-croissant-2f66e8.netlify.app`

Observed browser failures:

- `POST /chat/message` returned `500`.
- `POST /chat/handover/{conversation_id}` returned `500`.
- Browser displayed a CORS warning because the backend error response did not include the expected CORS header.

This is not treated as only a CORS issue. The browser request reached the backend, and the remaining failure is backend 500 and/or frontend flow mismatch.

## Root Cause

- The frontend bridge was already using the approved normal message endpoint: `POST /chat/message`.
- The active Pro v2 interaction layer could request backend handover from typed operator intent instead of reserving `/chat/handover/{conversation_id}` for an explicit operator action.
- Production live smoke remains affected by the known production DB credential mismatch; this phase does not change DB credentials, Secret Manager, Cloud Run, or CORS.

## Fix Summary

- Kept normal message flow on:
  - `POST /chat/session/start`
  - `POST /chat/message`
- Confirmed message payload fields match `ChatMessageRequest`:
  - `conversation_id`
  - `message`
  - `session_id`
  - `source_domain`
  - `language`
  - `selected_department`
  - `selected_topic`
  - `page_url`
  - `widget_variant`
- Changed typed operator intent to render an operator card without automatically calling `/chat/handover/{conversation_id}`.
- Kept backend handover behind explicit operator/sidebar action.
- Added visible message error renderer:
  - `ვერ მივიღე პასუხი. სცადეთ თავიდან ან მიმართეთ ოპერატორს.`
  - `Could not get an answer. Please try again or contact an operator.`
- Added production smoke script:
  - `backend/app/scripts/production_chat_message_smoke.py`
- Added verifier:
  - `backend/app/scripts/verify_phase_9s_message_500_fix.py`

## Deployment Package

Netlify ZIP rebuilt:

`dist/netlify_test_site_deploy.zip`

Netlify redeploy required: YES

## Verification Result

- `compileall app`: PASS
- Targeted pytest: PASS
- `verify_phase_9s_message_500_fix`: PASS
- `test_site_session_payload_smoke`: FAIL, production `/chat/session/start` returned `500`.
- `test_site_api_smoke`: FAIL, production `/chat/session/start` returned `500`.
- `production_chat_message_smoke`: FAIL from this environment with sanitized `ConnectError`.

The frontend/package fix is ready, but live backend message smoke still requires production backend/DB credential repair before browser retest can pass.

## Safety

- Real Alte site modified: NO
- Production DB modified: NO
- DB migration/seed run: NO
- Secret Manager changed: NO
- Cloud Run/CORS changed: NO
- Contact details sent: NO
- Handover/contact-flow smoke run: NO
- Intentional lead/task/customer creation: NO
- Public launch: NO
