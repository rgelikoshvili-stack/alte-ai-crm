# Phase 9AB Netlify Deploy Source Fix Result

PHASE_9AB_NETLIFY_DEPLOY_SOURCE_FIX_STATUS=PASSED_NETLIFY_VISUAL_QA

Decision state:

```text
BACKEND_DEPLOYED_WIDGET_MOBILE_RESPONSIVE_VISUAL_QA_PASSED_PENDING_PRIVACY_AND_EMBED_APPROVAL
```

Public launch: NO-GO

## Scope

- Netlify test site: `https://nimble-croissant-2f66e8.netlify.app/join.html`
- Existing Netlify project: `nimble-croissant-2f66e8`
- Publish directory: `test_site`
- Real Alte site modified: NO
- Backend modified/deployed: NO
- CORS changed: NO
- Secret Manager changed: NO
- Production DB changed: NO
- Contact details sent: NO
- Lead/task/customer created: NO

## Root Cause

Netlify continued serving a stale `variants/pro-v2-chat.jsx` after dashboard redeploy because the production deploy source appears to track the repository default branch, `master`.

GitHub default branch:

```text
master
```

Before this fix:

- `origin/master` did not contain `@media (max-width: 1024px)` in `test_site/variants/pro-v2-chat.jsx`.
- `origin/phase-9s-agent-preview-cors-note` did contain the mobile responsive guard.
- Commits `9c96a88` and `7b1e008` existed only on `phase-9s-agent-preview-cors-note`, not on `master`.

## Fix

Copied the fixed `test_site` assets from `phase-9s-agent-preview-cors-note` to `master` so Netlify production deploys from the current fixed widget files.

Files updated on `master`:

- `test_site/alte-ai-chat-widget.js`
- `test_site/index.html`
- `test_site/join.html`
- `test_site/variants/pro-v2-chat.jsx`

Confirmed local `master` now includes:

```text
@media (max-width: 1024px)
.cw-win.expanded .cw-side,
max-width:calc(100vw - 16px)
```

## Netlify Verification

Netlify was refreshed by pushing the fixed `test_site` assets to `master`.

Master commit:

```text
26c538e phase 9ab: fix netlify deploy source for mobile widget
```

Live asset freshness was verified with cache busting:

```powershell
curl.exe "https://nimble-croissant-2f66e8.netlify.app/variants/pro-v2-chat.jsx?v=26c538e"
```

The downloaded live asset was `49,256` bytes and contains:

```text
@media (max-width: 1024px)
.cw-win.expanded .cw-side,
max-width:calc(100vw - 16px)
```

Strict visual QA was run against:

```text
https://nimble-croissant-2f66e8.netlify.app/join.html
```

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\python.exe -m app.scripts.visual_qa_netlify_widget
```

Result: PASS

## Visual QA Results

- Desktop `1440x900`: PASS
  - `documentScrollWidth=1440`
  - `bodyScrollWidth=1440`
  - `modalWidth=980`
  - `sidebarVisible=true`
- Mobile `430x932`: PASS
  - `documentScrollWidth=430`
  - `bodyScrollWidth=430`
  - `modalWidth=418`
  - `sidebarVisible=false`
- Mobile `390x844`: PASS
  - `documentScrollWidth=390`
  - `bodyScrollWidth=390`
  - `modalWidth=378`
  - `sidebarVisible=false`
- Mobile `375x667`: PASS
  - `documentScrollWidth=375`
  - `bodyScrollWidth=375`
  - `modalWidth=363`
  - `sidebarVisible=false`

Screenshots:

- `docs/deployment/visual_qa/netlify_widget_desktop_1440x900_phase_9ab.png`
- `docs/deployment/visual_qa/netlify_widget_mobile_430x932_phase_9ab.png`
- `docs/deployment/visual_qa/netlify_widget_mobile_390x844_phase_9ab.png`
- `docs/deployment/visual_qa/netlify_widget_mobile_375x667_phase_9ab.png`

## Current Status

Netlify now serves the fixed `master` asset and strict visual QA passes on desktop and mobile.

Remaining blockers:

- privacy URL
- contact-flow approval
- final asset URL
- staged real-site embed approval
- real-domain smoke
- dirty tree reconciliation
- final public launch approval
