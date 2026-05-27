# Phase 9Y Operator Handover Message Persistence Fix

PHASE_9Y_OPERATOR_HANDOVER_MESSAGE_FIX_STATUS=READY_PENDING_NETLIFY_REDEPLOY_AND_BROWSER_RETEST

## Issue

The staged production diagnostic confirmed that chatbot handover conversations can appear in CRM Inbox, and operator replies can return to the same chatbot session. However, the Pro v2 frontend had a usability gap:

- The typed or button-based operator request was shown locally in the chatbot UI.
- The handover branch called `/chat/handover/{conversation_id}`.
- It did not persist the operator request text through `/chat/message` before handover.

As a result, a no-contact handover conversation could appear in the CRM Inbox with `human_handover=true`, but the operator might not see the user's explicit "connect me with an operator" message as the latest backend message.

## Production Diagnostic

Safe no-contact production diagnostic:

- session started: YES
- message posted: YES
- handover status: `contact_required`
- conversation found in Inbox: YES
- Inbox `human_handover=true`: YES
- operator reply created from CRM API: YES
- operator reply visible through chatbot transcript polling: YES
- contact details sent: NO
- lead/customer/task intentionally created: NO

The `contact_required` status is expected when the visitor does not provide phone/email. In that mode, the conversation is visible for handover review but no task/customer/lead is created.

## Fix

Updated the Pro v2 safe widget handover flow:

- Before calling `/chat/handover/{conversation_id}`, `AlteChatBackend.requestHandover()` now persists the operator request text via `/chat/message`.
- Typed operator requests pass the typed text to the backend.
- Sidebar/operator button requests pass the default operator request text to the backend.
- The handover request is marked with metadata: `handover_request=true`.

## Files Changed

- `widget/pro-v2.html`
- `widget/variants/pro-v2-chat.jsx`
- `test_site/alte-ai-chat-widget.html`
- `test_site/variants/pro-v2-chat.jsx`
- `dist/netlify_test_site/alte-ai-chat-widget.html`
- `dist/netlify_test_site/variants/pro-v2-chat.jsx`
- `dist/netlify_test_site_deploy.zip`

## Verification

- Targeted tests: `18 passed`.
- Frontend forbidden pattern scan: PASS.
- Active widget assets still do not contain:
  - `api.anthropic.com`
  - `ANTHROPIC_API_KEY`
  - `sk-ant-`
  - `DATABASE_URL`
  - `window.claude.complete`
  - `/api/chat`

## Next Step

Redeploy the updated Netlify package:

```text
dist/netlify_test_site_deploy.zip
```

Then retest:

1. Open `https://nimble-croissant-2f66e8.netlify.app/join.html`.
2. Ask for an operator.
3. Open local CRM `http://127.0.0.1:5173/`.
4. Select `Production API`.
5. Confirm the Inbox conversation shows the operator request text.
6. Send an operator reply.
7. Confirm the reply appears back in the chatbot.

Public launch remains NO-GO.

