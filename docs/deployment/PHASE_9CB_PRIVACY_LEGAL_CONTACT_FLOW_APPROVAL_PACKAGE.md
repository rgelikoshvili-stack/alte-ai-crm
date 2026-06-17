# Phase 9CB Privacy Legal Contact Flow Approval Package

Date: 2026-06-15

Branch: `phase-9s-agent-preview-cors-note`

Decision: `CONTACT_FLOW_PRIVACY_LEGAL_APPROVAL_PENDING_PUBLIC_LAUNCH_NO_GO`

Public launch: `NO-GO`

## Source Documents

- `docs/deployment/PHASE_9CA_LAUNCH_APPROVAL_GATES_REFRESH.md`: FOUND
- `docs/deployment/PHASE_9AZ_FINAL_APPROVAL_PACKAGE.md`: NOT_FOUND
- `docs/deployment/FINAL_PREFLIGHT_GATE.md`: FOUND
- `docs/deployment/PHASE_9P_PUBLIC_LAUNCH_DECISION.md`: FOUND

## Current Backend Status

Production backend:

- Revision: `alte-ai-crm-backend-00054-m6r`
- Traffic: `100%`
- Health: PASS, HTTP 200
- Image tag: `v0.9-phase-9by-calendar-hotfix`
- Image digest: `sha256:b456378796a91c2ca2140935affbcdc0bd7edabc18b3a694e8a25761e9234fb3`
- Rollback target: `alte-ai-crm-backend-00053-pbz`

Verified QA status:

- Full 9AS: PASS, 53/53
- Focused 9AT: PASS, 7/7
- Operator alignment: PASS, 7/7
- Program Catalog source QA: PASS
- 9BE Academic Calendar: PASS
- 9BF/9BG focused: PASS, 12/12
- Worktree/deploy hygiene: clean at Phase 9CA baseline

Contact-flow status:

- Contact flow enabled for public launch: NO
- Real contact-flow QA executed in this phase: NO
- Real contact data submitted in this phase: NO
- Lead/customer/task created in this phase: NO

## Data Collection Summary

The following fields are confirmed from backend schemas, models, routes, and service code. This section describes what the chatbot/contact flow may collect or create if the contact flow is later approved and executed.

| Area | Confirmed fields or records | Notes |
| --- | --- | --- |
| Session and conversation context | `conversation_id`, `session_id`, `channel`, `source_domain`, `language`, `widget_variant`, `metadata`, `page_url` | Used to associate chat requests with the same browser session and source context. |
| User chat content | chat `message`, contact-form `message`, `question`, `note` | Stored as conversation/message content when submitted through chat or contact form paths. |
| Contact identity | `first_name`, `last_name`, `full_name`, `phone`, `email` | Contact submission requires consent and at least phone or email before CRM contact write behavior. |
| Interest and routing | `interest_area`, `selected_department`, `selected_topic`, `department_id`, `source_domain`, `source_channel` | Used for lead routing, department selection, and follow-up context. |
| Customer record | first name, last name, phone, email, source channel, consent status, timestamps | Contact submission stores `consent_status` as `explicit_chat_contact_request`. |
| Lead record | customer link, interest area, program, department, assigned user, stage, status, priority, source channel, source domain, campaign tag, handover flags/reason, qualification status, recommended next action, timestamps | Some values can be derived from the chat/contact payload and AI routing context. |
| Conversation record | customer link, lead link, channel, status, language, AI handled flag, human handover flag, summary | Tracks the lifecycle of the chat. |
| Message record | sender type, text, channel message id, metadata, timestamp | Metadata can include handover/contact flags, selected department/topic, source domain, and session id. |
| Operator task record | lead/customer links, department, title, description, due date, priority, status, timestamps | Contact flow can create or reuse a human handover task after approved contact submission. |
| Audit/operator context | action/entity metadata, handover status, operator notes/status if used in CRM | Audit and operator records support traceability and handoff. |

Confirmed safety behavior:

- `/chat/contact/{conversation_id}` requires explicit consent before contact handover.
- `/chat/contact/{conversation_id}` requires phone or email before CRM contact write behavior.
- `/chat/handover/{conversation_id}` without existing contact/lead context marks the conversation waiting for operator but does not create a customer, lead, or task.
- No-contact guards prevent informational/admissions-style chat messages from creating leads or tasks without contact information.

## Consent And Privacy Requirements

The following approvals are required before public launch or any real contact-flow write approval:

| Requirement | Status | Required owner/legal decision |
| --- | --- | --- |
| User-facing privacy notice | PENDING | Approve final privacy notice text and public URL/location. |
| Consent wording before contact submission | PENDING | Approve the exact checkbox/copy shown before phone/email submission. |
| Data retention policy | PENDING | Define how long chat messages, contacts, leads, tasks, and audit records are retained. |
| Access control for leads/tasks | PENDING | Confirm which operators/admins can view contact data, messages, leads, and tasks. |
| Deletion/correction request process | PENDING | Define how users request correction or deletion of contact/chat records. |
| Legal basis for processing | PENDING | Legal owner to confirm the basis for processing contact requests and follow-up. |
| Minors/student data caution | PENDING | Confirm wording and handling for applicants/students who may provide sensitive or age-related context. |
| Human operator handoff wording | PENDING | Approve wording that tells users when a human/operator follow-up may occur. |
| No-spam/no-unwanted-contact wording | PENDING | Confirm users understand contact details are used only for requested follow-up. |

## Contact-Flow Approval Gates

All contact-flow gates remain PENDING unless a later owner-approved record explicitly completes them.

| Gate | Status | Notes |
| --- | --- | --- |
| Dry-run/safety contact-flow QA | PENDING | May be run later without creating real production contacts if owner approves the test scope. |
| Real write approval | PENDING | Required before any production contact/customer/lead/task write test. |
| Operator notification approval | PENDING | Confirm how operators are notified and who is responsible. |
| CRM lead/customer/task mapping approval | PENDING | Confirm field mapping, departments, priorities, and task due-date behavior. |
| No-spam/no-unwanted-contact wording approval | PENDING | Confirm user-facing wording before public collection. |
| Rollback/disable-contact-flow plan | PENDING | Confirm how contact collection can be disabled or reverted quickly. |
| Support/operator handoff approval | PENDING | Confirm operators are ready to handle live requests. |

## Safe Contact-Flow Test Plan

The following tests are recommended later only after explicit owner approval. They were not run in Phase 9CB.

| Test | Environment | Write behavior | Approval required |
| --- | --- | --- | --- |
| Dry-run form validation | Local or production-safe dry run | No real contact write | Owner approval for dry-run scope |
| Consent-required validation | Local or dry run | No real contact write | Owner approval for validation scope |
| Missing phone/email validation | Local or dry run | No real contact write | Owner approval for validation scope |
| Fake test lead in isolated environment | Isolated/non-production if available | Test-only write | Owner approval and test-data definition |
| Production write with explicit owner-approved test data | Production | One approved test contact/customer/lead/task | Owner and legal approval required |
| Duplicate task check | Same approved test context | May inspect or create approved test task | Owner approval required |
| Operator view verification | Operator CRM view | Read-only unless approved | Operator/support approval required |
| Disable/rollback contact flow check | Configuration/runbook | No user data required | Owner approval for disable/rollback procedure |

Rules for future tests:

- Do not use real applicant/student personal data without explicit approval.
- Do not run contact creation from public traffic during testing.
- Do not create duplicate tasks intentionally unless the test plan requires and approves it.
- Record test data values separately and do not commit secrets or private personal data to the repository.

## Risks

| Risk | Impact | Required mitigation before launch |
| --- | --- | --- |
| Accidental real lead creation | User contact data could enter CRM before legal/owner approval. | Keep contact-flow write approval pending until explicit sign-off. |
| Missing or unclear privacy notice | Users may not understand data collection and follow-up. | Approve public privacy notice and consent copy. |
| Unclear consent | Contact details may be submitted without adequate user agreement. | Approve explicit consent wording and checkbox behavior. |
| Unsupported sensitive data | Users may submit personal, student, health, or age-related context. | Add guidance and retention/access handling for sensitive submissions. |
| Duplicate or incorrect operator task | Operators may receive duplicate or misrouted follow-up work. | Approve CRM mapping and run duplicate-task QA. |
| User expectation mismatch | User may expect only AI response, not human follow-up. | Make handoff/contact wording explicit before submission. |
| Operator readiness gap | Live requests may be missed or delayed. | Complete support/operator handoff approval. |

## Approval Checklist

Owner/legal must explicitly approve all applicable items before public launch:

- Final privacy notice and public URL/location.
- Consent checkbox/copy before contact submission.
- Data retention and deletion/correction process.
- Operator/admin access scope for contact data.
- Contact-flow real write test plan.
- CRM customer/lead/task field mapping.
- Operator notification and support handoff process.
- No-spam/no-unwanted-contact wording.
- Rollback/disable-contact-flow plan.
- Final public launch decision.

## Decision

`CONTACT_FLOW_PRIVACY_LEGAL_APPROVAL_PENDING_PUBLIC_LAUNCH_NO_GO`

Backend is technically deployed and verified, but privacy/legal/contact-flow gates remain pending. Public launch remains `NO-GO`.

## Safety Confirmations

- Backend deploy performed in this phase: NO
- Rollback performed in this phase: NO
- Real `alte.edu.ge` modified: NO
- Real `join.alte.edu.ge` modified: NO
- Assets uploaded or embedded: NO
- Frontend/Netlify changed: NO
- DB/schema/migration/seed/import changed: NO
- Secret Manager/CORS changed: NO
- Bridge Hub changed: NO
- Contact flow submitted: NO
- Lead/customer/task created: NO
- Secrets/tokens/passwords/DATABASE_URL printed: NO
- Public launch marked GO: NO
