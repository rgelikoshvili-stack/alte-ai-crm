# Phase 9AB Netlify Deploy Source Fix Result

PHASE_9AB_NETLIFY_DEPLOY_SOURCE_FIX_STATUS=PUSHED_TO_MASTER_PENDING_NETLIFY_REDEPLOY_AND_VISUAL_QA

Decision state:

```text
BACKEND_DEPLOYED_WIDGET_MOBILE_RESPONSIVE_FIXED_ON_MASTER_PENDING_NETLIFY_REDEPLOY
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

## Required Netlify Verification

After Netlify redeploys `master`, verify the live asset:

```powershell
curl.exe https://nimble-croissant-2f66e8.netlify.app/variants/pro-v2-chat.jsx | findstr /C:"@media (max-width: 1024px)"
```

Then run strict visual QA:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\python.exe -m app.scripts.visual_qa_netlify_widget
```

Expected:

- Desktop `1440x900`: PASS
- Mobile `430x932`: PASS
- Mobile `390x844`: PASS
- Mobile `375x667`: PASS
- `sidebarVisible=false` on mobile viewports

## Current Status

This commit fixes the deploy-source mismatch in Git. Netlify visual QA must be rerun after Netlify finishes redeploying `master`.
