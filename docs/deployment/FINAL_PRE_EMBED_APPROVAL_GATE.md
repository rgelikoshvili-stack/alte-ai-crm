# Final Pre-Embed Approval Gate

## A. Current Technical Status

- Production backend is deployed and healthy.
- Cloud Run service URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Cloud Run service: `alte-ai-crm-backend`
- Claude is enabled through the backend.
- Cloud SQL is ready.
- Secret Manager is ready.
- Full local Alte Knowledge Base has been imported into production Knowledge Base.
- Sensitive KB content remains `review_required`.
- Finance/tuition/scholarship/deadline no-contact guard is deployed and verified in production.
- Safe Pro widget candidate is ready.

## B. Selected Widget

Selected candidate:

```text
widget/alte-university-ai-chatbot-safe-pro.html
```

Design style:

```text
compact PIP-style widget with selected Pro polish
```

Reason:

- Least intrusive for public `alte.edu.ge` pages.
- Safe backend-connected architecture.
- KA/EN support.
- No direct Anthropic browser call.
- No frontend API key or secret.
- Frontend renders backend state only; backend remains responsible for AI, Knowledge Base, and CRM business rules.

Baseline widget remains available:

```text
widget/alte-university-ai-chatbot-safe.html
```

## C. Blockers

These items are not approved and remain pending:

- Human reviewer decisions: `PENDING`
- Official content approval: `PENDING`
- Privacy/data approval: `PENDING`
- Final widget asset URL: `PENDING`
- Website admin/developer deployment confirmation: `PENDING`
- Actual site embed: `PENDING`
- Real-domain browser smoke: `PENDING`

## D. Approval Requirements

Required before actual embed:

1. Human reviewer decisions completed, or explicit approval to keep sensitive content handover/review-required.
2. Official content approval.
3. Privacy/data approval.
4. Final widget asset hosting URL selected.
5. Alte website admin/developer confirms where the snippet will be inserted.
6. Real-domain smoke plan approved.

## E. Go/No-Go

```text
FINAL_PRE_EMBED_STATUS=NO_GO_PENDING_APPROVALS
```

Do not mark GO. Do not embed on the real Alte website until all required approvals and the final asset URL are confirmed.
