# Phase 9AB Netlify Redeploy And Visual QA Result

PHASE_9AB_NETLIFY_REDEPLOY_STATUS=BLOCKED_NETLIFY_AUTH_REQUIRED

Decision state:

```text
BACKEND_DEPLOYED_WIDGET_MOBILE_RESPONSIVE_FIXED_PENDING_NETLIFY_REDEPLOY
```

Public launch: NO-GO

## Scope

- Netlify test site: `https://nimble-croissant-2f66e8.netlify.app/join.html`
- Existing Netlify site name: `nimble-croissant-2f66e8`
- Publish directory: `test_site`
- Branch commit intended for deploy: `9c96a88 phase 9ab: fix mobile responsive widget qa`
- Real Alte site modified: NO
- Backend modified/deployed: NO
- CORS changed: NO
- Secret Manager changed: NO
- Production DB changed: NO
- Contact details sent: NO
- Lead/task/customer created: NO

## Branch And Asset State

Confirmed current branch contains:

- `9c96a88 phase 9ab: fix mobile responsive widget qa`

Confirmed local asset includes mobile responsive guard:

- `test_site/variants/pro-v2-chat.jsx`
- `@media (max-width: 1024px)`
- `.cw-win.expanded .cw-side, .cw-side{ display:none; }`
- `max-width:calc(100vw - 16px)`

## Netlify Deploy Attempt

Netlify CLI was installed locally, but this machine is not authenticated with Netlify and no `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID`, or `.netlify/state.json` site linkage is available.

Attempted deploy:

```text
netlify deploy --prod --dir test_site --site nimble-croissant-2f66e8 --message "phase 9ab mobile responsive widget qa"
```

Result:

```text
Unauthorized: could not retrieve project
```

Deploy ID: unavailable because deploy did not start.

## Deployed Asset Freshness

Live asset checked:

```text
https://nimble-croissant-2f66e8.netlify.app/variants/pro-v2-chat.jsx
```

Result:

- HTTP fetch succeeded.
- The deployed asset does not contain `@media (max-width: 1024px)`.
- The deployed asset is stale relative to the current branch.

`join.html` status:

- `https://nimble-croissant-2f66e8.netlify.app/join.html`: 200

## Strict Visual QA

Script:

```text
python -m app.scripts.visual_qa_netlify_widget
```

Netlify result:

- Desktop `1440x900`: PASS
- Mobile `430x932`: FAIL
- Mobile `390x844`: FAIL
- Mobile `375x667`: FAIL

Failure reason:

- `sidebarVisible=true` on all mobile viewports.
- Header and composer are visible.
- No horizontal scroll was detected.
- Modal is inside viewport, but the stale desktop sidebar keeps the chat column too narrow.

Local fixed-asset result:

- Desktop `1440x900`: PASS
- Mobile `430x932`: PASS, `sidebarVisible=false`
- Mobile `390x844`: PASS, `sidebarVisible=false`
- Mobile `375x667`: PASS, `sidebarVisible=false`

## Screenshot Evidence

Local fixed-asset PASS:

- `docs/deployment/visual_qa/local_widget_desktop_1440x900_phase_9ab.png`
- `docs/deployment/visual_qa/local_widget_mobile_430x932_phase_9ab.png`
- `docs/deployment/visual_qa/local_widget_mobile_390x844_phase_9ab.png`
- `docs/deployment/visual_qa/local_widget_mobile_375x667_phase_9ab.png`

Netlify stale-asset FAIL:

- `docs/deployment/visual_qa/netlify_widget_desktop_1440x900_phase_9ab.png`
- `docs/deployment/visual_qa/netlify_widget_mobile_430x932_phase_9ab.png`
- `docs/deployment/visual_qa/netlify_widget_mobile_390x844_phase_9ab.png`
- `docs/deployment/visual_qa/netlify_widget_mobile_375x667_phase_9ab.png`

Automation JSON:

- `docs/deployment/visual_qa/phase_9ab_visual_qa_result_local.json`
- `docs/deployment/visual_qa/phase_9ab_visual_qa_result_netlify.json`

## Required Next Step

Redeploy the existing Netlify site from the current branch assets using an authenticated Netlify session or token with access to `nimble-croissant-2f66e8`.

After redeploy:

1. Confirm live `variants/pro-v2-chat.jsx` contains `@media (max-width: 1024px)`.
2. Confirm `join.html` returns 200.
3. Rerun strict Netlify visual QA.
4. Only then set:

```text
PHASE_9AB_MOBILE_RESPONSIVE_STATUS=PASSED_PENDING_PRIVACY_AND_EMBED_APPROVAL
BACKEND_DEPLOYED_WIDGET_MOBILE_RESPONSIVE_VISUAL_QA_PASSED_PENDING_PRIVACY_AND_EMBED_APPROVAL
```
