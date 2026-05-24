# Uploaded Widget UI Review

Source file: `docs/knowledge_evidence/uploaded_widget_ui/alte_university_ai_chatbot.html`

## Findings

The uploaded HTML is useful as a UI and UX reference. It includes:

- Alte University sidebar branding
- department navigation
- KA/EN language switch
- chat bubbles
- handover/operator card
- lead card mockup
- department routing UX
- embedded Knowledge Base prompt/demo behavior

## Production Safety Review

The uploaded file currently calls Anthropic directly from the browser:

```text
fetch('https://api.anthropic.com/v1/messages', ...)
```

direct browser Anthropic calls are forbidden for production. The browser must never call Anthropic directly, must never contain an Anthropic API key, and must never treat a frontend prompt as the source of truth.

Production architecture must be:

```text
browser widget -> FastAPI backend -> Claude -> Knowledge Base -> CRM business rules
```

The FastAPI backend is responsible for:

- Claude calls
- Knowledge Base retrieval
- conservative answer policy
- no-contact lead guard
- CRM lead/task/customer rules
- audit and conversation persistence

The uploaded UI has been converted into a safe backend-connected standalone widget page at:

```text
widget/alte-university-ai-chatbot-safe.html
```

Public launch remains blocked until official content review, privacy/data approval, final widget asset hosting, actual site embed, and real-domain browser smoke are completed.
