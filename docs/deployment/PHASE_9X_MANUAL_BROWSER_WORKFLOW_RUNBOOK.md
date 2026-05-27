# Phase 9X Manual Browser Workflow Runbook

PHASE_9X_MANUAL_BROWSER_WORKFLOW_RUNBOOK_STATUS=READY_FOR_MANUAL_TEST

## Purpose

This runbook verifies the complete staged browser workflow before any real Alte website embed:

Netlify Pro v2 chatbot -> production backend -> local operator CRM in Production API mode -> operator reply -> chatbot polling -> operator reply knowledge candidate review.

This is not a public launch test and does not modify the real Alte website.

## Test URLs

- Netlify chatbot KA page: `https://nimble-croissant-2f66e8.netlify.app/`
- Netlify chatbot EN/join page: `https://nimble-croissant-2f66e8.netlify.app/join.html`
- Local operator CRM: `http://127.0.0.1:5173/`
- Production backend: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`

## Prerequisites

- Local CRM server is running:

  ```powershell
  cd C:\tmp\alte-ai-crm\frontend
  python -m http.server 5173
  ```

- Netlify page opens and shows the Pro v2 chatbot.
- CRM page opens locally.
- Approved temporary operator account is available to the tester.
- Use only safe test messages.
- Do not enter real phone numbers or real personal contact details.

## Safety Rules

- Do not modify `alte.edu.ge` or `join.alte.edu.ge`.
- Do not upload assets to the real Alte website.
- Do not mark public launch complete.
- Do not run DB migrations or seed production.
- Do not change Secret Manager.
- Do not print or share secrets.
- Do not use real applicant personal details.

## Browser Workflow

### A. Chatbot Load And AI Reply

1. Open `https://nimble-croissant-2f66e8.netlify.app/join.html`.
2. Open DevTools Console and Network.
3. Confirm the Pro v2 widget is visible.
4. Confirm there are no console errors.
5. Confirm there are no requests to `api.anthropic.com`.
6. Send safe message:

   ```text
   What documents do international students need?
   ```

7. Confirm the request goes to `/chat/session/start` and `/chat/message`.
8. Confirm an AI answer appears.
9. Confirm there is no 422 response.
10. Confirm there is no CORS error.

### B. Department And Handover

1. Select a department in the sidebar, such as International or Finance.
2. Send a safe department-specific question.
3. Confirm the active department changes visually.
4. Confirm answer is conservative for sensitive facts.
5. Ask for an operator or use the operator/handover UI.
6. Confirm the chatbot shows operator/handover state.

### C. Operator CRM Inbox

1. Open `http://127.0.0.1:5173/`.
2. Click `Production API`.
3. Open Settings and log in with the approved operator account.
4. Open Inbox.
5. Refresh if needed.
6. Confirm the chatbot conversation appears.
7. Confirm selected department/context is visible if available.

### D. Operator Reply Return

1. Open the staged conversation in Inbox.
2. Send an operator reply with safe text, for example:

   ```text
   Hello, this is a test operator reply from the staging CRM.
   ```

3. Return to the Netlify chatbot tab.
4. Wait for polling or send another safe message if needed.
5. Confirm the operator reply appears in the chatbot.

### E. Knowledge Candidate Review

1. In CRM conversation, find the operator reply.
2. Click `Create knowledge candidate`.
3. Confirm candidate status appears beside the reply.
4. Click `Open review`.
5. Confirm Knowledge page opens with the candidate/search.
6. Confirm candidate is `draft` / `review_required`.
7. Confirm it can be edited and saved as draft.
8. Do not approve public sensitive facts unless a real reviewer has approved them.

## Pass Criteria

- Pro v2 widget loads without console errors.
- Browser calls only approved backend endpoints.
- AI answer returns from production backend.
- Department selection works.
- Operator/handover path appears in CRM Inbox.
- Operator reply returns to chatbot.
- Operator reply candidate can be created and opened in Knowledge review.
- Candidate remains review-gated.
- Public launch remains NO-GO.

## Fail Handling

Record the exact failed step, browser console error, network status code, endpoint URL, and whether the issue is:

- frontend UI issue
- backend API issue
- auth/login issue
- CORS issue
- operator workflow issue
- knowledge review UI issue

