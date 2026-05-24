# Website Widget Production Embed

## A. Purpose

Prepare script snippets for adding the Alte AI CRM Chat Widget to:

- `https://alte.edu.ge`
- `https://join.alte.edu.ge`

This document is preparation only. Do not modify the real websites until website access and privacy approval are complete.

## B. Preconditions

- Cloud Run backend deployed and healthy.
- `/health` returns `200`.
- `/diagnostics/ai` returns Claude enabled without secrets.
- CORS includes:
  - `https://alte.edu.ge`
  - `https://join.alte.edu.ge`
- Website admin/developer access confirmed.
- Privacy/data approval confirmed.
- Consent text approved.
- Final widget asset URL confirmed.
- Rollback/removal plan confirmed.

## C. Embed Snippet For alte.edu.ge

Replace `YOUR_WIDGET_ASSET_URL` with the final hosted widget asset URL.

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
    sourceDomain: "alte.edu.ge",
    defaultLanguage: "ka",
    proactiveEnabled: true,
    proactiveDelayMs: 30000
  };
</script>
<script src="https://YOUR_WIDGET_ASSET_URL/alte-chat-widget.js"></script>
```

## D. Embed Snippet For join.alte.edu.ge

Use English as the default language and the join source domain.

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
    sourceDomain: "join.alte.edu.ge",
    defaultLanguage: "en",
    proactiveEnabled: true,
    proactiveDelayMs: 30000
  };
</script>
<script src="https://YOUR_WIDGET_ASSET_URL/alte-chat-widget.js"></script>
```

For a more aggressive admission landing-page prompt, `proactiveDelayMs` may be set to `5000` only if approved by the website/privacy owner.

## E. Consent Text

Georgian:

```text
საკონტაქტო მონაცემებს ვიყენებთ მხოლოდ კონსულტაციისთვის.
```

English:

```text
We use your contact details only to provide consultation.
```

## F. Privacy Policy Placeholder

The final widget should link to the approved Alte privacy policy URL when available.

Do not add a placeholder privacy URL to the production website. Use only the approved URL.

## G. Rollback / Removal

To disable the widget:

- Remove both script tags from the website.
- Or set `proactiveEnabled: false` to disable proactive prompts while keeping manual chat access.
- Or remove the widget asset URL if the widget must be disabled globally.
- Clear website/CDN cache if the site uses caching.
- Verify no JavaScript console errors remain after removal.
- Verify the page layout is unchanged after removal.

## H. Smoke Test Checklist

Run these checks on a staging/test page before adding the widget to production pages:

- Widget button appears in the bottom-right corner.
- Widget opens and closes.
- KA/EN toggle works.
- `alte.edu.ge` config sends `sourceDomain: "alte.edu.ge"` and default language `ka`.
- `join.alte.edu.ge` config sends `sourceDomain: "join.alte.edu.ge"` and default language `en`.
- Greeting appears.
- Quick replies render.
- Safe backend unavailable message works if backend is unreachable.
- Consent text is visible before or near contact collection.
- `/chat/session/start` succeeds.
- `/chat/message` succeeds for a general approved-source question.
- Tuition/deadline questions do not invent exact values.
- Human handover path is available.

Do not run production lead-creating smoke tests until the owner approves test records.

## I. Current Status

- Backend status: `CLOUD_RUN_DEPLOYED`
- Backend URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Widget embed status: `ACTUAL_EMBED_BLOCKED_PENDING_WEBSITE_PRIVACY_APPROVAL`
- Standalone production demo status: `BACKEND_DEPLOYED_STANDALONE_WIDGET_READY_PENDING_SITE_EMBED`
- Standalone demo page: `widget/standalone-production-demo.html`
- Transfer package: `WIDGET_TRANSFER_TO_ALTE_SITE.md`
- Privacy approval status: `PENDING`
- Production widget smoke status: `PENDING`
