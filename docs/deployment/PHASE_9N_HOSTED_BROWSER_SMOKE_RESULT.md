# Phase 9N Hosted Browser Smoke Result

HOSTED_BROWSER_SMOKE_STATUS=BLOCKED_PENDING_NETLIFY_REDEPLOY

## Current State

- test origin URL: `https://alte-ai-chat-test.netlify.app`
- CORS configured: YES
- hosted page deployed: NO
- browser smoke executed: NO
- real Alte site modified: NO
- public launch: NO
- current blocker: Netlify returns `Site not found / not deployed`
- deploy fix instructions: `docs/test_origin_handoff/NETLIFY_DEPLOY_FIX_GEO.md`
- corrected deploy package: `dist/netlify_test_site_deploy.zip`
- Netlify package manifest: `docs/test_origin_handoff/NETLIFY_TEST_SITE_PACKAGE_MANIFEST.md`
- next required action: redeploy the Netlify test site with `test_site` as publish directory or upload the deploy ZIP.

## Manual Browser Smoke Instructions

1. Open `https://alte-ai-chat-test.netlify.app`.
2. Open DevTools Console and Network.
3. Confirm widget loads.
4. Confirm no CORS errors.
5. Send safe messages only; do not enter phone/email/contact details.
6. Confirm responses render.
7. Confirm there are no `api.anthropic.com` requests.
8. Confirm no frontend API keys are exposed.

## Expected Future PASS Criteria

- widget loads.
- no console errors.
- no CORS errors.
- backend calls succeed.
- no `api.anthropic.com` calls.
- no frontend keys.
- department routing works.
- sensitive answers conservative.
- no contact details sent.
- no intentional lead/task/customer creation.

Do not mark hosted browser smoke passed until the temporary origin is hosted and the browser checklist passes.
