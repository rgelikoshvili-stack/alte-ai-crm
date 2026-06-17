# Phase 9AM Real Site Rollback Plan

PHASE_9AM_REAL_SITE_ROLLBACK_PLAN_STATUS=READY_PENDING_APPROVED_EMBED

Public launch: NO-GO

Use this plan only after a staged real-site embed has been explicitly approved and applied.

## Rollback Owner

```text
ROLLBACK_OWNER=PENDING_ASSIGNMENT
SMOKE_OWNER=PENDING_ASSIGNMENT
PUBLIC_LAUNCH_ROLLBACK_OWNER=PENDING_ASSIGNMENT
```

## Immediate Disable

Remove the widget loader script from the staged page:

```html
<script src="https://alte.edu.ge/assets/alte-ai-chat-widget.js" defer></script>
```

If an explicit config block was added, remove it too:

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
    assetBaseUrl: "https://alte.edu.ge/assets",
    sourceDomain: "join.alte.edu.ge",
    defaultLanguage: "ka",
    widgetVariant: "pro_v2_safe"
  };
</script>
```

## Optional Asset Removal

If needed, remove uploaded assets from the web server or CMS media/static asset manager:

- `/assets/alte-ai-chat-widget.js`
- `/assets/alte-ai-chat-widget.html`
- `/assets/variants/pro-v2-chat.jsx`
- `/assets/variants/pro-v2-icons.jsx`
- `/assets/variants/pro-v2-modals.jsx`
- `/assets/variants/pro-v2-page.jsx`
- `/assets/variants/pro-v2-strings.jsx`
- `/assets/variants/tweaks-panel.jsx`

Asset removal is optional if the script tag is removed and no page references the files.

## Cache Clear

- Clear page cache.
- Clear CDN cache if used.
- Hard refresh the staged page.
- Confirm the old script tag is not present in page source.

## Verification

- Widget launcher no longer appears.
- No iframe is injected.
- Browser network panel shows no calls to:
  - `/chat/session/start`
  - `/chat/message`
  - `/chat/handover`
- No console errors related to the removed widget.
- Backend Cloud Run service remains untouched.

## Backend Safety

Do not change:

- Cloud Run service.
- Secret Manager.
- production DB.
- CORS.
- official KB/routing logic.

## Gate

```text
ROLLBACK_PLAN_TESTED_CONCEPTUALLY=YES
REAL_SITE_ROLLBACK_EXECUTED=NO
REAL_ALTE_SITE_MODIFIED=NO
PUBLIC_LAUNCH_STATUS=NO_GO
```
