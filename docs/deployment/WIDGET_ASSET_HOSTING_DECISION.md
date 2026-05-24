# Widget Asset Hosting Decision

## Purpose

Choose how to host `alte-chat-widget.v0.8.js` for the production website embed.

Current status: `ACTUAL_EMBED_BLOCKED_PENDING_WEBSITE_PRIVACY_APPROVAL`

## Option A - Website/CMS Static Asset Hosting

Upload `widget/alte-chat-widget.v0.8.js` to the website or CMS static assets.

Recommended if Alte developer/admin access is available.

Pros:

- Easiest first production embed path.
- Website team controls the asset lifecycle.
- Rollback is simple by removing the script tag or replacing the uploaded file.
- No new Google Cloud Storage bucket or CDN configuration required.

Cons:

- Requires Alte website developer/admin access.
- Cache invalidation depends on website/CMS tooling.

Decision: Recommended for first production embed.

## Option B - Google Cloud Storage Static Asset

Host the versioned JavaScript file in a Cloud Storage bucket, optionally with CDN later.

Pros:

- Versioned asset hosting can be independent of the CMS.
- CDN can be added later.

Cons:

- Requires bucket, CORS, cache headers, IAM, and public asset configuration.
- Adds another cloud resource to operate.

Decision: Later option only. Do not create Cloud Storage unless explicitly approved.

## Option C - Cloud Run Static Route

Serve the widget asset from the backend.

Pros:

- Same backend URL can serve API and widget file.
- Avoids website/CMS asset upload if unavailable.

Cons:

- Requires backend static route/config and a new Cloud Run revision.
- Couples widget asset delivery to backend app deploys.

Decision: Not recommended unless website/CMS hosting and Cloud Storage are unavailable.

## Recommendation

Use Option A - Website/CMS static asset hosting for the first production embed.

If website access is not available yet, prepare only:

- `widget/alte-chat-widget.v0.8.js`
- `WIDGET_EMBED_SNIPPETS_FINAL.md`
- `WEBSITE_DEVELOPER_HANDOFF.md`
- `PRODUCTION_WIDGET_SMOKE_CHECKLIST.md`

Do not perform the actual website embed until website admin/developer access and privacy/data approval are confirmed.
