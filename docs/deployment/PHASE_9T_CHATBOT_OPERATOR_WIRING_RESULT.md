# Phase 9T Chatbot Operator Wiring Result

PHASE_9T_CHATBOT_OPERATOR_WIRING_STATUS=LOCAL_CODE_READY_PENDING_BROWSER_WORKFLOW_TEST

## Scope

Phase 9T starts the full Pro v2 chatbot-to-operator workflow from the local source-of-truth widget:

- chatbot UI: `widget/pro-v2.html`
- operator CRM UI: `frontend/index.html`
- backend: FastAPI chat/CRM services

The Pro v2 visual design is not changed. This phase wires chatbot actions to the existing backend and CRM workflow.

## Implemented

- Added public-safe contact handover endpoint:
  - `POST /chat/contact/{conversation_id}`
- Added public-safe transcript endpoint for the same browser session:
  - `GET /chat/messages/{conversation_id}?session_id=...`
- Both endpoints require a valid chat `session_id`.
- Contact handover:
  - requires explicit consent
  - requires phone or email
  - creates/updates customer
  - creates/updates lead
  - marks conversation as `human_handover=true`
  - creates one operator handover task
- Pro v2 local widget now passes:
  - `selected_department`
  - `selected_topic`
  - `widget_variant=pro_v2_safe`
  - `channel=website_chat`
- Pro v2 operator request now calls backend handover.
- Pro v2 contact modal no longer ships fake default contact values.
- Pro v2 polls operator messages from backend so CRM replies can appear in the chatbot.

## Operator CRM Fit

The existing operator CRM already supports:

- Inbox: `GET /inbox`
- Conversation detail/messages
- Operator reply:
  - `POST /conversations/{conversation_id}/messages`

Phase 9T connects the chatbot side to that existing operator workflow.

## Safety

- Real `alte.edu.ge` was not modified.
- Real `join.alte.edu.ge` was not modified.
- No Cloud Run deploy was executed.
- No CORS change was executed.
- No database migration or seed was executed.
- No Secret Manager change was executed.
- No frontend API key was added.
- Browser still uses backend endpoints, not direct Claude/Anthropic calls.
- Public launch remains NO-GO.

## Verification

- Targeted backend tests: `12 passed`
- Compile check: passed
- Local workflow smoke script added:
  - `python -m app.scripts.local_pro_v2_operator_workflow_smoke`

## Next Step

Run a local browser workflow:

1. Open `http://127.0.0.1:5500/pro-v2.html`.
2. Start/continue a chatbot conversation.
3. Request operator or submit contact.
4. Open `http://127.0.0.1:5173/`.
5. Confirm the conversation appears in CRM Inbox.
6. Send operator reply from CRM.
7. Confirm the operator reply appears back in the chatbot.

Decision state:

```text
BACKEND_LOCAL_PRO_V2_OPERATOR_WIRING_READY_PENDING_BROWSER_WORKFLOW_TEST
```
