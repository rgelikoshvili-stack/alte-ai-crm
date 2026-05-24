# Standalone Production Widget Demo

This demo page runs from static hosting and uses the production Cloud Run backend:

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

It is intended for testing before the widget is embedded on the real Alte websites.

## Run Locally

```powershell
cd C:\tmp\alte-ai-crm\widget
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500/standalone-production-demo.html
```

## What It Tests

- Loads `alte-chat-widget.v0.8.js`.
- Uses the production backend URL.
- Allows switching:
  - `sourceDomain=alte.edu.ge`, `defaultLanguage=ka`
  - `sourceDomain=join.alte.edu.ge`, `defaultLanguage=en`
- Uses `proactiveEnabled=true`.
- Uses proactive delay:
  - `30000` ms for `alte.edu.ge`
  - `5000` ms for `join.alte.edu.ge`

## Safe Testing Rules

- This demo uses the production backend.
- Do not enter real student data unless approved.
- Contact details can create production CRM customer, lead, and task records.
- Use only safe messages unless production test records are approved.
- Do not paste API keys, passwords, or private data into the widget.

## Transfer To Real Website Later

After website admin/developer access and privacy/data approval:

1. Upload `alte-chat-widget.v0.8.js` to the approved website/CMS static asset location.
2. Replace `YOUR_FINAL_WIDGET_ASSET_URL` in `WIDGET_EMBED_SNIPPETS_FINAL.md`.
3. Add the correct snippet to a hidden/staging page first.
4. Run `STANDALONE_WIDGET_SMOKE_CHECKLIST.md` and `PRODUCTION_WIDGET_SMOKE_CHECKLIST.md`.
5. Move to public pages only after approval.

## Rollback

- Remove both script tags.
- Or remove/replace the widget asset.
- Or set `proactiveEnabled: false` to disable proactive prompts.
- Clear website/CDN cache if needed.

## Current Status

```text
BACKEND_DEPLOYED_STANDALONE_WIDGET_READY_PENDING_SITE_EMBED
```

Actual Alte website embed remains blocked until website/privacy approvals are confirmed.
