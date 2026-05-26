# Phase 9U Operator Answer Knowledge Candidates Result

PHASE_9U_OPERATOR_ANSWER_KNOWLEDGE_STATUS=OPERATOR_ANSWERS_TO_DRAFT_REVIEW_QUEUE_READY

## Scope

- Goal: allow useful operator replies to become reviewed knowledge candidates for future AI answers.
- Netlify test package rebuilt with the local Pro v2 operator workflow HTML and required `variants/` source files.
- Updated deploy package: `dist/netlify_test_site_deploy.zip`.
- Manual Netlify redeploy required: YES.
- Hosted browser smoke passed: NO.
- Real Alte site modified: NO.
- Cloud Run deploy: NO.
- CORS change: NO.
- Production DB change: NO.
- Secret Manager change: NO.
- Public launch: NO-GO.

## Behavior

- Operator replies can be converted into knowledge candidates through:
  - `POST /knowledge/operator-reply-candidates/{message_id}`
- Only messages with `sender_type=operator` are accepted.
- The candidate is created as:
  - `KnowledgeSource.status=draft`
  - `KnowledgeSource.review_required=true`
  - `KnowledgeSource.source_type=faq`
  - `KnowledgeSnippet.status=draft`
  - `KnowledgeSnippet.review_required=true`
- The previous visitor question is included with the operator answer for reviewer context.
- The source key is idempotent:
  - `operator_reply:{message_id}`
- Repeated requests return the existing candidate instead of duplicating knowledge.

## Safety

- Automatic learning from operator replies: no.
- Automatic approval: no.
- AI retrieval uses approved knowledge only by default.
- Sensitive topics still require official review before exact public answers.
- Operator-created candidates must pass the knowledge review queue before becoming approved source material.

## Files Changed

- `backend/app/schemas/knowledge.py`
- `backend/app/services/knowledge_service.py`
- `backend/app/api/routes_knowledge.py`
- `backend/app/tests/test_phase_9u_operator_answer_knowledge_candidates.py`
- `backend/app/scripts/verify_phase_9u_operator_answer_knowledge_candidates.py`

## Next Step

Add CRM UI affordance on the operator conversation page:

- button: “Create knowledge candidate from this reply”
- show candidate status: draft / review required / approved
- keep approval in the existing knowledge review workflow

Decision state:

```text
BACKEND_LOCAL_OPERATOR_ANSWER_REVIEW_LEARNING_READY_PENDING_UI_REVIEW_AND_APPROVAL
```

## CRM UI Update

- Operator conversation messages now include a `Create knowledge candidate` action for operator replies.
- The action calls `POST /knowledge/operator-reply-candidates/{message_id}`.
- Existing candidates are reused instead of duplicated.
- Existing candidates are detected with `source_key=operator_reply:{message_id}`.
- Candidate status is shown beside each operator reply.
- `Open review` jumps to the Knowledge page and fills the candidate search.
- Knowledge page includes an `Operator answer drafts` quick filter for draft FAQ-style operator answer candidates.
- Operator answer draft review cards include `Approve` and `Archive` actions using the existing knowledge approval endpoints.
- Operator answer draft review cards include editable content and `Save draft` before approval.
- Draft metadata editing is available for category, sensitivity, and language.
- `Save draft` updates both source and snippet records to keep review metadata consistent.
- Remaining polish: manual CRM browser workflow verification before packaging for Netlify/production.

Additional files changed:

- `frontend/app.js`
- `frontend/styles.css`
