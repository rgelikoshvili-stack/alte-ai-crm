# Phase 9W Chatbot Function Audit Result

PHASE_9W_CHATBOT_FUNCTION_AUDIT_STATUS=AUTOMATED_FUNCTION_SMOKE_PASSED_PENDING_MANUAL_BROWSER_WORKFLOW

## Scope

This audit checks the current Pro v2 chatbot, backend chat flow, CORS readiness, safe AI behavior, department routing, no-contact guard, and operator workflow readiness before any real Alte website embed.

Real Alte site modified: NO.
Actual Alte embed: NO.
Cloud Run/CORS changed in this audit: NO.
Production DB schema changed: NO.
Secret Manager changed: NO.
Public launch: NO-GO.

## Automated Results

| Area | Result |
| --- | --- |
| Session payload smoke | 2/2 PASS |
| Test site API smoke | 10/10 PASS |
| CORS smoke | 10/10 PASS |
| Security/reliability smoke | 16/16 PASS |
| Department routing/sidebar smoke | 28/28 PASS |
| Finance no-contact smoke | 24/24 PASS |
| Knowledge smoke | 25/25 PASS |
| Local operator workflow smoke | 5/5 PASS |
| Phase 9T/9U/9V targeted tests | 18 passed |
| Phase 9T verifier | PASS |
| Phase 9U verifier | PASS |
| Phase 9V verifier | PASS |

## Confirmed Chatbot Functions

- Pro v2 widget uses backend-only endpoints for session and message flow.
- Session start payload uses `channel=website_chat` and `widget_variant=pro_v2_safe`.
- Chat message payload carries `selected_department` and `selected_topic`.
- AI answers come from the FastAPI backend, where Claude/Cloud AI is used securely.
- Department routing is confirmed for sidebar context.
- Finance and other sensitive topics remain conservative without contact details.
- No-contact guard prevents customer/lead/task creation in safe smoke tests.
- Handover routing is confirmed by backend smoke.
- Local operator workflow can create and process the chatbot/operator path in TestClient.
- Operator replies can become draft knowledge candidates with `review_required=true`.
- Operator reply candidates are idempotent by `operator_reply:{message_id}`.
- Operator answers are not automatically approved or learned by the public AI.

## Frontend Safety

Scanned frontend/widget assets contain no forbidden direct provider or secret patterns:

- `api.anthropic.com`: absent
- `ANTHROPIC_API_KEY`: absent
- `sk-ant-`: absent
- `DATABASE_URL`: absent
- `window.claude.complete`: absent
- `/api/chat`: absent from active safe widget assets

The browser must call only:

- `/chat/session/start`
- `/chat/message`
- approved supporting chat endpoints for handover/contact/message polling where explicitly wired

## Warning Noted

The test site API smoke produced one non-blocking warning for an IT support message:

- AI indicated `should_create_lead=true`.
- No contact details were sent.
- No CRM record was created.

This confirms that the no-contact CRM guard held. The warning should remain visible for future refinement of AI intent flags, but it is not a data-safety failure.

## Manual Browser Workflow Still Required

Automated API and local workflow checks passed, but the full human browser workflow still needs manual confirmation:

1. Open `https://nimble-croissant-2f66e8.netlify.app/join.html`.
2. Send a safe chatbot message.
3. Use operator/handover flow.
4. Open `http://127.0.0.1:5173/`.
5. Select `Production API`.
6. Log in with the approved temporary operator account.
7. Open Inbox and confirm the conversation appears.
8. Send an operator reply.
9. Confirm the reply appears back in the chatbot.
10. Open Knowledge review and confirm the operator reply can be saved as a draft candidate.

## Decision State

```text
BACKEND_CHATBOT_FUNCTION_AUDIT_PASSED_PENDING_MANUAL_BROWSER_WORKFLOW
```

