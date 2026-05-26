# Phase 9N Actual Netlify Origin CORS Result

PHASE_9N_ACTUAL_NETLIFY_ORIGIN_CORS_STATUS=READY_PENDING_MANUAL_BROWSER_RETEST

## Origins

- Actual Netlify origin: `https://nimble-croissant-2f66e8.netlify.app`
- Previous planned origin: `https://alte-ai-chat-test.netlify.app`

## Cloud Run CORS Update

- CORS update executed: YES
- Update type: Cloud Run environment update only
- Image built: NO
- Image changed: NO
- Backend image currently serving: `v0.9-security-reliability-fixes`
- Previous revision: `alte-ai-crm-backend-00009-bhk`
- New serving revision: `alte-ai-crm-backend-00010-g47`
- Wildcard CORS used: NO

Allowed origins after update:

```text
https://alte.edu.ge
https://join.alte.edu.ge
https://alte-ai-chat-test.netlify.app
https://nimble-croissant-2f66e8.netlify.app
```

## Endpoint Checks

- `/health`: `200`
- `/version`: `200`
- `/diagnostics/ai`: `200`, Claude enabled, no secret values exposed
- `/dashboard/overview` without auth: `401`

## CORS Smoke Result

Command:

```powershell
python -m app.scripts.production_test_origin_cors_smoke
```

Result:

- total tests: 10
- passed: 10
- failed: 0
- actual Netlify origin allowed: true
- previous temporary origin allowed: true
- Alte origins still allowed: true
- random origin blocked: true

## API Smoke Results

- test site API smoke: 10/10 passed
- security/reliability smoke: 16/16 passed
- department routing smoke: 28/28 passed
- finance no-contact smoke: 24/24 passed
- knowledge smoke after study docs: 25/25 passed

## Hosted Browser Smoke

- hosted browser smoke status: `PENDING_REDEPLOY_AND_MANUAL_RETEST`
- Manual browser retest must use:
  `https://nimble-croissant-2f66e8.netlify.app`
- CORS issue is fixed and the widget is visible, but `/chat/session/start` returned `422` before this payload fix.
- Frontend session payload fix is prepared; Netlify redeploy is required before browser retest.
- Browser smoke is not marked passed yet.

## Safety Confirmation

- real Alte site modified: NO
- asset uploaded to Alte: NO
- actual Alte embed: NO
- public launch: NO
- contact details sent: NO
- contact-flow test run: NO
- intentional production lead/task/customer creation: NO
- DB migration/seed: NO
- production DB change: NO
- Secret Manager change: NO
- wildcard CORS: NO
