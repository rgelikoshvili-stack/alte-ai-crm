# Phase 9V Staging Operator CRM Test Workflow

PHASE_9V_STAGING_OPERATOR_CRM_STATUS=LOCAL_OPERATOR_CRM_CAN_TARGET_PRODUCTION_BACKEND_FOR_NETLIFY_TESTING

## Purpose

This workflow lets the team test the full chatbot-to-operator flow before the real Alte website embed.

## Test Topology

- Student chatbot test page:
  `https://nimble-croissant-2f66e8.netlify.app/`
- International/join chatbot test page:
  `https://nimble-croissant-2f66e8.netlify.app/join.html`
- Operator CRM local page:
  `http://127.0.0.1:5173/`
- Shared backend for staging test:
  `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`

## Operator Setup

1. Start the local CRM frontend:

   ```powershell
   cd C:\tmp\alte-ai-crm\frontend
   python -m http.server 5173
   ```

2. Open:

   ```text
   http://127.0.0.1:5173/
   ```

3. Click `Production API`.

4. If production auth is required, open Settings and log in with an approved operator account.

5. Open the Inbox view.

## Browser Test Flow

1. Open the Netlify chatbot page.
2. Send a safe message without phone/email/contact details.
3. Ask for an operator or use the contact/handover UI.
4. In local CRM, refresh Inbox.
5. Confirm the conversation appears.
6. Operator sends a reply from CRM.
7. Confirm the reply returns to the chatbot.

## Safety State

- Real Alte site modified: NO.
- Actual Alte embed: NO.
- Production DB schema changed: NO.
- Secret Manager changed: NO.
- Public launch: NO-GO.

## Remaining Before Public Launch

- Manual hosted browser smoke must pass.
- Official privacy URL remains required.
- Real Alte site asset upload and embed remain pending.
- Real-domain smoke remains pending.
- Public launch approval remains pending.
