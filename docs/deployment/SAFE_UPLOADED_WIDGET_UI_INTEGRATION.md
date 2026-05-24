# Safe Uploaded Widget UI Integration

## Purpose

The uploaded `alte_university_ai_chatbot.html` file is a useful UI/UX reference, but its original architecture is unsafe for production because it calls Anthropic directly from the browser.

## Forbidden Pattern

Browser code must not call Anthropic directly and must not contain any Anthropic API key.

Forbidden:

```text
browser -> Anthropic API
```

## Safe Architecture

Required:

```text
browser widget -> FastAPI backend -> Claude -> Knowledge Base -> CRM business rules
```

The safe converted page is:

```text
widget/alte-university-ai-chatbot-safe.html
```

It calls:

- `POST /chat/session/start`
- `POST /chat/message`

against:

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

## Responsibilities

Browser widget:

- renders UI
- sends user messages to backend
- displays backend response, sources, handover state, and backend-created CRM IDs if returned
- never creates leads/tasks/customers directly
- never stores API keys

FastAPI backend:

- Claude calls
- Knowledge Base retrieval
- conservative answer policy
- no-contact lead guard
- CRM lead/task/customer rules
- audit and conversation persistence

## Local Testing

```powershell
cd C:\tmp\alte-ai-crm\widget
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500/alte-university-ai-chatbot-safe.html
```

Production CORS is restricted to real Alte domains. Local browser chat may be blocked. This is expected. API smoke should use backend scripts unless temporary CORS test mode is explicitly approved.

## Future Hosting

For real browser smoke, host the safe widget on an allowed Alte origin or an approved staging/hidden page:

- `https://alte.edu.ge`
- `https://join.alte.edu.ge`

## Remaining Blockers

- official content review
- privacy/data approval
- final widget asset URL
- actual site embed
- real-domain browser smoke
- Cloud Run redeploy for Phase 8Y finance no-contact guard

Public launch remains blocked.
