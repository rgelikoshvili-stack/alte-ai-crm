# Chatbot Public Answer Policy

These rules apply before and after the widget is embedded on public Alte pages.

1. If exact tuition price is not in an approved source, do not answer exact price.
2. If a deadline is not in an approved source, do not answer exact deadline.
3. If required documents are not in an approved source, provide general guidance and route to handover.
4. If the user asks about Medicine/MD requirements and the source is not approved, route to International Admissions or Medicine handover.
5. If an international user asks about visa, relocation, or legal requirements, avoid legal certainty and route to official consultation.
6. If confidence is below `0.70`, use fallback wording and human handover.
7. If source is missing, use fallback wording and human handover.
8. If contact details are missing, ask for phone or email before creating a lead/task.
9. Never expose internal notes, source review status, IDs, secrets, or system prompts to the user.
10. AI returns structured analysis only; CRM business rules decide actions.
11. If the AI provider is unavailable, times out, or returns an invalid response, return the safe KA/EN provider fallback, set `should_handover=true`, set `should_create_lead=false`, and include `ai_provider_error` in internal risk flags.
12. Protected backend endpoints without explicit permission mapping are denied by default.

## Department-Aware Handover Routing

When confidence is below `0.70`, source is missing, the topic is sensitive, the answer is unknown, or the student asks for a human, the backend must route the conversation to the best department/operator.

Routing targets:

- Admissions
- International Admissions
- Finance
- Medicine / MD
- Student Services
- IT Support
- General / Operator

Frontend may send sidebar context through `selected_department` and `selected_topic`, but frontend must not decide CRM actions or create leads/tasks/customers.

Decision state:

```text
BACKEND_CODE_READY_DEPARTMENT_HANDOVER_ROUTING_PENDING_REDEPLOY
```

## Full Local KB Governance

The full local Alte KB import is available to the application for controlled testing, but imported chunks are not a public-launch approval. Sensitive chunks remain `review_required=true`.

The bot must continue to avoid invented exact facts for:

- tuition, fees, grants, scholarships, and payment terms
- admission deadlines and academic calendar dates
- required document lists
- Medicine/MD and dentistry requirements
- international admissions requirements
- visa, relocation, and legal-sensitive topics
- accreditation/recognition claims

If a chunk is sensitive or not explicitly approved by a reviewer, the answer should be conservative and route to official confirmation or human handover.

Operational guardrails:

- Finance, deadline, Medicine/MD, international admissions, visa, relocation, and legal topics remain conservative until official sources are approved.
- Review-required content may support controlled testing, but it must not be treated as final public official wording.
- Public launch remains blocked until official content review and privacy approval are complete.

## Phase 9D-Redeploy Routing Status

Image `v0.9-department-routing-sidebar` was deployed to Cloud Run. Finance no-contact and broader knowledge smoke tests passed after deployment, and sensitive-answer behavior remained conservative.

Department routing smoke failed two ambiguous sidebar-context cases. Until this is fixed, unknown or ambiguous sidebar questions may route to `Admissions` instead of the explicitly selected Finance or Medicine department.

Policy remains unchanged:

- The bot must not invent tuition, deadlines, requirements, visa/legal claims, or other sensitive official facts.
- If the answer is uncertain or source approval is missing, it must route to the correct department.
- Sidebar department context must be preserved for ambiguous questions after the follow-up fix.

Decision state:

```text
BACKEND_DEPLOYED_DEPARTMENT_ROUTING_FAILED_NEEDS_REVIEW
```
- Phase 8S-Apply re-check found no reviewer-owned `decision` column. Generated `recommended_action` values are not reviewer decisions, so conservative policy remains active and no official content was automatically approved.
- Phase 8W smoke found a tuition/finance no-contact lead bug: one tuition no-contact response returned `should_create_lead=true` despite no lead/task IDs.
- Phase 8Y service-layer guard fixed locally: finance, tuition, scholarship, grant, and deadline information questions without phone/email force `should_create_lead=false`, do not create customer/lead/task, and do not force phone/email unless the user asks for consultation or human follow-up.
- Phase 8Y-Redeploy deployed this behavior to Cloud Run with image tag `v0.8-finance-no-contact-guard`.
- Production finance no-contact smoke passed: `24 passed`, `0 failed`; broader knowledge smoke passed: `25 passed`, `0 failed`.
- Contact-flow test was not run, no contact details were sent, and no intentional production lead/task/customer creation occurred.
- Phase 9A created the human reviewer decision package in `docs/reviewer_package/`; until reviewer decisions are filled and applied in a later approved phase, sensitive public-answer policy remains conservative.

## Phase 9F Conservative Content Decision Policy

Phase 9F prepared a conservative system draft at:

- `docs/reviewer_package/alte_kb_conservative_decisions_for_approval.csv`

Policy impact:

- LOW, non-sensitive, official-source-backed general content may be marked `APPROVE` in the draft.
- HIGH sensitivity rows are not public-approved by the system draft.
- Tuition, deadlines, documents, Medicine/MD, international admissions, scholarships/grants/payments, visa, relocation, and legal content remain `NEEDS_OFFICIAL_SOURCE` or `HANDOVER_ONLY` unless an explicit human reviewer approves them later.
- The frontend and backend must continue routing uncertain or sensitive questions to the correct department/operator.
- Production DB was not modified in Phase 9F.

## Phase 9L-P Launch Gate Content Status

CONTENT_APPROVAL_STATUS=APPROVED_WITH_CONSERVATIVE_POLICY_PENDING_HUMAN_FINAL_REVIEW

This status means the conservative answer policy is accepted for preparation and handoff. It does not approve public exact answers for sensitive facts. Tuition/fees, deadlines, required documents, Medicine/MD, International admissions, visa/relocation/legal, grants, scholarships, and payment topics remain conservative or handover-only until final human review approves exact public wording.

Public launch remains NO-GO pending site embed and real-domain smoke.

Decision state:

```text
BACKEND_DEPLOYED_CONTENT_DECISIONS_PREPARED_PENDING_HUMAN_APPROVAL
```

## Phase 9G-H Privacy And Consent Policy Update

The widget now includes a small privacy/consent note near the composer and in contact request UI. Normal Knowledge Base questions are not blocked by consent. If a user wants operator contact or backend asks for phone/email, the widget shows the contact/privacy wording and the user may type contact details naturally.

Privacy/data approval remains pending. Official content approval remains pending. Public launch remains blocked.

Decision state:

```text
BACKEND_DEPLOYED_PRIVACY_AND_EMBED_PACKAGE_READY_PENDING_FINAL_APPROVALS
```

## Phase 9J Public Answer Gate

The final pre-site-embed gate is NO-GO pending approvals.

- Privacy final approval pending.
- Official content approval pending.
- Conservative CSV review pending.
- Actual site embed pending.
- Public launch not complete.

Decision state:

```text
BACKEND_DEPLOYED_FINAL_PRE_EMBED_GATE_READY_NO_GO_PENDING_APPROVALS
```

## Phase 9K Security Reliability Policy

Phase 9K hardens pre-launch behavior:

- AI provider errors must not expose stack traces, exception details, API keys, or secret names to users.
- Public handover endpoint calls must include a valid session ID for the conversation.
- Public handover requests without contact/CRM linkage may mark the conversation for handover but must not create repeated high-priority tasks.
- Repeated handover requests for the same eligible conversation are idempotent.
- `AUTH_REQUIRED=true` is mandatory when `ENVIRONMENT=production`.

Decision state:

```text
BACKEND_CODE_FIXED_SECURITY_RELIABILITY_PENDING_REDEPLOY
```
