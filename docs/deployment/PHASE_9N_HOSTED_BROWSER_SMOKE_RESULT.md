# Phase 9N Hosted Browser Smoke Result

HOSTED_BROWSER_SMOKE_STATUS=PENDING_REDEPLOY_AND_MANUAL_RETEST

## Current State

- test origin URL: `https://alte-ai-chat-test.netlify.app`
- actual deployed Netlify URL: `https://nimble-croissant-2f66e8.netlify.app`
- CORS configured: YES
- hosted page deployed: YES, at actual Netlify origin
- browser smoke executed: NO
- real Alte site modified: NO
- public launch: NO
- current blocker: updated Pro v2 operator workflow package has not yet been redeployed to Netlify after the local rebuild.
- deploy fix instructions: `docs/test_origin_handoff/NETLIFY_DEPLOY_FIX_GEO.md`
- site-name/deploy troubleshooting: `docs/test_origin_handoff/NETLIFY_SITE_NAME_TROUBLESHOOTING_GEO.md`
- corrected deploy package: `dist/netlify_test_site_deploy.zip`
- Netlify package manifest: `docs/test_origin_handoff/NETLIFY_TEST_SITE_PACKAGE_MANIFEST.md`
- next required action: redeploy the latest `dist/netlify_test_site_deploy.zip` to the actual Netlify site or trigger Git deploy from latest `master`.
- actual Netlify origin CORS update: DONE
- result doc: `docs/deployment/PHASE_9N_ACTUAL_NETLIFY_ORIGIN_CORS_RESULT.md`
- session/start payload issue found: browser request reached backend but returned `422`.
- frontend payload fix prepared: `channel` now uses backend-compatible `website_chat`.
- payload fix result: `docs/deployment/PHASE_9N_TEST_WIDGET_SESSION_PAYLOAD_FIX_RESULT.md`
- next required action: redeploy Netlify package `dist/netlify_test_site_deploy.zip`, then manually retest the browser page at `https://nimble-croissant-2f66e8.netlify.app`; do not enter phone/email/contact details.
- frontend event binding issue found: Pro v2 shell rendered, but initialization stopped on `addEventListener` for a missing mapped control.
- frontend event binding fix prepared: `cw-attach`/`cw-voice` are mapped and event binding is guarded with `on(...)`.
- event binding fix result: `docs/deployment/PHASE_9S_FRONTEND_EVENT_BINDING_FIX_RESULT.md`

## Manual Browser Smoke Instructions

1. Open `https://nimble-croissant-2f66e8.netlify.app`.
2. Open DevTools Console and Network.
3. Confirm widget loads.
4. Confirm no CORS errors.
5. Send safe messages only; do not enter phone/email/contact details.
6. Confirm responses render.
7. Confirm there are no direct AI provider requests.
8. Confirm no frontend API keys are exposed.

## Expected Future PASS Criteria

- widget loads.
- no console errors.
- no CORS errors.
- backend calls succeed.
- no direct AI provider calls.
- no frontend keys.
- department routing works.
- sensitive answers conservative.
- no contact details sent.
- no intentional lead/task/customer creation.

Do not mark hosted browser smoke passed until the temporary origin is hosted and the browser checklist passes.

## Phase 9Q Pro v2 Update

- The hosted test package now contains the safe Pro v2 widget adaptation.
- Netlify redeploy is required before the browser can show the updated Pro v2 safe UI.
- Browser smoke remains pending and must not be marked passed until manual retest confirms the new widget works.

Decision state:

```text
BACKEND_DEPLOYED_PRO_V2_SAFE_WIDGET_READY_PENDING_NETLIFY_REDEPLOY_AND_BROWSER_RETEST
```

## Phase 9Q-9R Rebuild Update

- Large Pro v2 safe modal package is prepared.
- Hosted browser smoke is still pending Netlify redeploy and manual retest.
- Do not mark browser smoke passed until the updated Netlify page is opened and verified.

Decision state:

```text
BACKEND_DEPLOYED_PRO_V2_REBUILT_AND_FUNCTION_GAPS_AUDITED_PENDING_NETLIFY_REDEPLOY
```

## Phase 9S Exact ZIP Source Port Update

- Exact ZIP-source Pro v2 port is prepared.
- The rebuilt widget uses the source `.cw-win`, `.cw-win.expanded`, `.cw-backdrop`, `.cw-side`, and `.cw-comp` visual model.
- Backend calls remain limited to `/chat/session/start` and `/chat/message`.
- Hosted browser smoke is still pending Netlify redeploy and manual retest.
- Do not mark browser smoke passed until the updated Netlify page is opened and verified.

Decision state:

```text
BACKEND_DEPLOYED_EXACT_ZIP_SOURCE_PRO_V2_WIDGET_READY_PENDING_NETLIFY_REDEPLOY
```

## Phase 9S Event Binding Fix Update

- The Pro v2 initialization crash from unguarded `addEventListener` binding has been fixed locally.
- Netlify package was rebuilt and requires redeploy.
- Hosted browser smoke remains pending until manual retest confirms the chat body renders and controls work.

Decision state:

```text
BACKEND_DEPLOYED_PRO_V2_EVENT_BINDING_FIXED_PENDING_NETLIFY_REDEPLOY
```

## Phase 9T/9U Operator Workflow Package Update

- Netlify deploy package has been rebuilt from the local Pro v2 chatbot source.
- Package now includes `alte-ai-chat-widget.html` and `variants/` at the ZIP root.
- Chatbot package includes operator handover/contact support through `/chat/contact/{conversation_id}`.
- Chatbot package includes operator reply polling through `/chat/messages/{conversation_id}` with session guard.
- Operator-answer knowledge candidate creation remains CRM/backend-side only and is not exposed in the public widget.
- Hosted browser smoke remains pending until the updated package is redeployed to Netlify and manually retested.

Decision state:

```text
BACKEND_LOCAL_OPERATOR_ANSWER_REVIEW_LEARNING_READY_PENDING_UI_REVIEW_AND_APPROVAL
```
