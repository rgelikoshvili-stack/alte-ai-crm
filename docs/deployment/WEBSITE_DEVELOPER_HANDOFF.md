# Website Developer Handoff

Current status: `ACTUAL_EMBED_BLOCKED_PENDING_WEBSITE_PRIVACY_APPROVAL`

## Backend API

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

Do not change the backend URL without notifying the project owner.

## Widget Asset

File:

```text
alte-chat-widget.v0.8.js
```

Recommended hosting:

```text
Website/CMS static asset hosting
```

Final asset URL placeholder:

```text
https://YOUR_FINAL_WIDGET_ASSET_URL/alte-chat-widget.v0.8.js
```

## Where To Place Script Tags

Place the config script before the widget script, ideally before the closing `</body>` tag.

Use the snippets from `WIDGET_EMBED_SNIPPETS_FINAL.md`.

## Expected Behavior

- Floating chat button appears in the bottom-right corner.
- Widget opens and closes without layout shift.
- KA/EN language toggle works.
- `alte.edu.ge` uses Georgian by default.
- `join.alte.edu.ge` uses English by default.
- Backend calls go only to the Cloud Run backend URL.
- No secrets are exposed in browser code.
- No external trackers are added.

## Consent Text

Georgian:

```text
საკონტაქტო მონაცემებს ვიყენებთ მხოლოდ კონსულტაციისთვის.
```

English:

```text
We use your contact details only to provide consultation.
```

## Privacy Policy

Add the approved Alte privacy policy URL when available.

Do not add a placeholder privacy URL to production pages.

## Rollback Steps

- Remove both widget script tags.
- Or set `proactiveEnabled: false` to disable proactive prompts.
- Or remove the widget asset URL if the widget must be disabled globally.
- Clear website/CDN cache.
- Verify no JavaScript console errors remain.
- Verify the page layout is unchanged.

## Smoke Test

Use `PRODUCTION_WIDGET_SMOKE_CHECKLIST.md`.

Start with a staging/test page before production pages.

Standalone sandbox package:

- `widget/standalone-production-demo.html`
- `widget/STANDALONE_PRODUCTION_DEMO.md`
- `STANDALONE_WIDGET_SMOKE_CHECKLIST.md`
- `WIDGET_TRANSFER_TO_ALTE_SITE.md`

Current standalone status: `BACKEND_DEPLOYED_STANDALONE_WIDGET_READY_PENDING_SITE_EMBED`

## Owner Placeholders

- Project owner: `PENDING`
- Website developer/admin owner: `PENDING`
- Privacy/data owner: `PENDING`
- Rollback owner: `PENDING`
