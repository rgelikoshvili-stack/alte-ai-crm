# Standalone Test Site Runbook

## Start Local Static Server

```powershell
cd C:\tmp\alte-ai-crm\widget
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500/full-standalone-chatbot-test.html
```

## What The Page Uses

- Widget asset: `./alte-chat-widget.v0.8.js`
- Production backend: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Source domains:
  - `alte.edu.ge`
  - `join.alte.edu.ge`
- Languages:
  - `ka`
  - `en`

## Safety Rules

- This test site uses the production backend.
- Do not enter real student data unless approved.
- Contact details can create production CRM records if submitted through the widget.
- Use safe non-contact messages for routine smoke tests.

## CORS Note

Local browser CORS may be blocked by production CORS. This is expected because production is restricted to the real Alte domains.

Backend/API smoke can still be run:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.standalone_chatbot_api_smoke
```

Full browser smoke should happen from an allowed domain or after explicit temporary CORS test-mode approval.
