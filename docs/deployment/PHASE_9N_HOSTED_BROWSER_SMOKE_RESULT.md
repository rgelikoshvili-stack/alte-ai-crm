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
- current blocker: Netlify returns `Site not found / not deployed`
- deploy fix instructions: `docs/test_origin_handoff/NETLIFY_DEPLOY_FIX_GEO.md`
- site-name/deploy troubleshooting: `docs/test_origin_handoff/NETLIFY_SITE_NAME_TROUBLESHOOTING_GEO.md`
- corrected deploy package: `dist/netlify_test_site_deploy.zip`
- Netlify package manifest: `docs/test_origin_handoff/NETLIFY_TEST_SITE_PACKAGE_MANIFEST.md`
- next required action: confirm the actual Netlify dashboard URL/site name, ensure deploy status is `Published`, and upload `dist/netlify_test_site_deploy.zip` to the correct Netlify site or configure Git deploy with publish directory `test_site`.
- actual Netlify origin CORS update: DONE
- result doc: `docs/deployment/PHASE_9N_ACTUAL_NETLIFY_ORIGIN_CORS_RESULT.md`
- session/start payload issue found: browser request reached backend but returned `422`.
- frontend payload fix prepared: `channel` now uses backend-compatible `website_chat`.
- payload fix result: `docs/deployment/PHASE_9N_TEST_WIDGET_SESSION_PAYLOAD_FIX_RESULT.md`
- next required action: redeploy Netlify package `dist/netlify_test_site_deploy.zip`, then manually retest the browser page at `https://nimble-croissant-2f66e8.netlify.app`; do not enter phone/email/contact details.

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
