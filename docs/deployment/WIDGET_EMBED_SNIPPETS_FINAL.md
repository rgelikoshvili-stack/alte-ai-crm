# Widget Embed Snippets Final

Current status: `ACTUAL_EMBED_BLOCKED_PENDING_WEBSITE_PRIVACY_APPROVAL`

Backend API URL:

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

Replace `YOUR_FINAL_WIDGET_ASSET_URL` with the approved hosted asset URL for `alte-chat-widget.v0.8.js`.

## A. alte.edu.ge Snippet

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
<script src="https://YOUR_FINAL_WIDGET_ASSET_URL/alte-chat-widget.v0.8.js"></script>
```

## B. join.alte.edu.ge Snippet

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
    sourceDomain: "join.alte.edu.ge",
    defaultLanguage: "en",
    proactiveEnabled: true,
    proactiveDelayMs: 5000
  };
</script>
<script src="https://YOUR_FINAL_WIDGET_ASSET_URL/alte-chat-widget.v0.8.js"></script>
```

## C. Notes

- Do not paste API keys into the snippet.
- The snippet is safe for a public website.
- The browser receives only the backend URL and widget config.
- Remove both script tags to roll back.
- Do not embed until website admin/developer access and privacy/data approval are confirmed.
