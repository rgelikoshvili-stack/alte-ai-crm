# Alte AI CRM Operator Frontend

Phase 5B static operator workspace for the existing FastAPI backend.

Run backend first:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Serve the frontend:

```powershell
cd C:\tmp\alte-ai-crm\frontend
python -m http.server 5173
```

Open:

```text
http://127.0.0.1:5173
```

The UI expects the API at `http://127.0.0.1:8000` by default. Change the API field in the top bar if needed.

For the hosted Netlify chatbot test, click `Production API` in the top bar so the local operator CRM reads the same backend as:

```text
https://nimble-croissant-2f66e8.netlify.app/
```

That sets the CRM API to:

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

Then use the Inbox view to see chatbot conversations and send operator replies.

If backend `AUTH_REQUIRED=true`, use Settings to log in. The returned token is stored in localStorage and sent as a bearer token with API requests.

Available views:

- Dashboard
- Inbox
- Leads
- Pipeline
- Tasks
- Knowledge
- Analytics
- Settings

This phase does not add real Claude calls, omnichannel integrations, or website widget behavior.
