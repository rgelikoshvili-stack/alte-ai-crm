# CORS and Widget Origins

The website widget can call the backend only from allowed origins.

## Local Origins

```text
http://127.0.0.1:5500
http://localhost:5500
http://127.0.0.1:5173
http://localhost:5173
```

## Production Origins

```text
https://alte.edu.ge
https://join.alte.edu.ge
```

Do not use wildcard `*` in production.

## Widget Dependency

The widget `apiBaseUrl` must point to the public Cloud Run backend URL.

Future production snippet:

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "https://YOUR_CLOUD_RUN_SERVICE_URL",
    sourceDomain: "alte.edu.ge",
    defaultLanguage: "ka",
    proactiveEnabled: true,
    proactiveDelayMs: 30000
  };
</script>
<script src="https://YOUR_WIDGET_URL/alte-chat-widget.js"></script>
```

For `join.alte.edu.ge`, set:

```js
sourceDomain: "join.alte.edu.ge",
defaultLanguage: "en"
```
