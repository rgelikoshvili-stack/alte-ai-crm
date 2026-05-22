# Alte Public Chat Widget

Lightweight static website chat widget for Alte AI CRM. It can be embedded with one JavaScript file and calls the existing backend chat endpoints.

## What It Does

- Floating bottom-right chat button
- KA/EN language toggle
- Local session storage for `conversation_id` and `session_id`
- Calls:
  - `POST /chat/session/start`
  - `POST /chat/message`
  - `POST /chat/handover/{conversation_id}` is backend-compatible for later UI use
- Quick replies for programs, admission, tuition, international students, and human handover
- Safe backend unavailable message
- Consent line for contact data collection
- Optional local proactive prompt

## Run Locally

Backend:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Widget demo:

```powershell
cd C:\tmp\alte-ai-crm\widget
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500/demo.html
```

## Embed Snippet

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "http://127.0.0.1:8000",
    sourceDomain: "alte.edu.ge",
    defaultLanguage: "ka"
  };
</script>
<script src="./alte-chat-widget.js"></script>
```

International admissions demo:

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "http://127.0.0.1:8000",
    sourceDomain: "join.alte.edu.ge",
    defaultLanguage: "en"
  };
</script>
<script src="./alte-chat-widget.js"></script>
```

## Config Options

- `apiBaseUrl`: backend base URL
- `sourceDomain`: `alte.edu.ge` or `join.alte.edu.ge`; if omitted, inferred from hostname
- `defaultLanguage`: `ka` or `en`
- `proactiveEnabled`: `true` or `false`
- `proactiveDelayMs`: delay before showing a local prompt while closed

## Current Limitations

- Static/local widget only
- No analytics tracking
- No public deployment
- No WhatsApp, Messenger, Instagram, or Email integration
- No scraping or live site ingestion
- No full privacy policy page in this phase
