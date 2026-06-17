# Phase 9AQ Chatbot Operator CRM Alignment QA Result

PHASE_9AQ_ALIGNMENT_STATUS=FAILED_PENDING_FIXES

Decision state:
BACKEND_DEPLOYED_CHATBOT_OPERATOR_ALIGNMENT_QA_FAILED_PENDING_FIXES

Public launch: NO-GO

## Scope

Phase 9AQ checked whether the live Netlify chatbot, production backend conversation state, routing metadata, handover/waiting state, and Operator CRM APIs/UI model work together as one system.

Tested URLs:

- Visitor chatbot: https://nimble-croissant-2f66e8.netlify.app/join.html
- Production backend: https://alte-ai-crm-backend-226875230147.europe-west1.run.app
- Local Operator CRM: http://127.0.0.1:5173

Backend revision:

- Last known deployed revision: `alte-ai-crm-backend-00035-g2b`
- Last known image: `v0.9-phase-9ap-fix-9ao-qa-bugs`

Netlify source status:

- Phase 9AP frontend fixes were verified live before this QA.
- Phase 9AQ did not upload, redeploy, or modify Netlify assets.

Safety status:

- Real Alte site modified: NO
- REAL_ALTE_SITE_MODIFIED=NO
- Asset upload executed: NO
- Real-site embed executed: NO
- Backend deployed in this phase: NO
- Production DB schema changed: NO
- Secret Manager changed: NO
- CORS changed: NO
- Bridge Hub touched: NO
- CONTACT_FLOW_EXECUTED=NO
- REAL_CONTACT_DATA_SENT=NO
- LEAD_TASK_CUSTOMER_CREATED=NO

## Expected Department Mapping

| Chatbot label | Expected backend/operator meaning |
| --- | --- |
| მიღება | Admissions |
| პროგრამები | Programs |
| დაფინანსება | Finance |
| საერთ. სტუდენტები | International Admissions |
| მედიცინა / MD | Medicine / MD |
| ბიბლიოთეკა | Library |
| კარიერა | Career |
| IT დახმარება | IT Support |
| ცოცხალი ოპერატორი | Human Operator |

Operator CRM should expose the selected department/routing badge, handover badge when handover is requested or needed, waiting-for-operator status after the wait action, latest visitor question, latest AI answer, timestamp, conversation id, and empty customer/lead sections when no contact form was submitted.

## Static Integration Review

Backend inspected:

- `backend/app/api/routes_chat.py`
- `backend/app/api/routes_inbox.py`
- `backend/app/api/routes_conversations.py`
- `backend/app/services/chat_service.py`
- `backend/app/services/department_routing_service.py`
- `backend/app/services/knowledge_routing_service.py`
- conversation, operator, customer, lead, and task schemas/models

Chatbot frontend inspected:

- `test_site/variants/pro-v2-chat.jsx`
- `test_site/variants/pro-v2-strings.jsx`
- `test_site/alte-ai-chat-widget.js`
- `test_site/alte-ai-chat-widget.html`

Operator CRM inspected:

- `frontend/app.js`
- `frontend/index.html`
- `frontend/styles.css`

Static findings:

- Chatbot sends conversation messages to `/chat/message` with source domain, language, widget variant, selected department, and session identifiers.
- Chatbot wait-for-operator sends `/chat/handover/{conversation_id}` with `mode=waiting_for_operator` and `reason=wait_for_operator`.
- Chatbot contact modal has the question/message textarea and latest-user-message prefill source logic.
- Operator CRM inbox reads `/inbox` and renders latest message snippet, status, selected department, handover badge, waiting badge, and timestamp.
- Operator CRM detail reads `/conversations/{conversation_id}/detail` and renders conversation id, latest status, selected department, handover state, visitor messages, AI messages, customer/lead sections, and reply box.
- Operator CRM can send operator replies through `/conversations/{conversation_id}/messages`.

## Production-Safe API QA

Command:

```text
python -m app.scripts.production_phase_9aq_chat_operator_alignment_qa
```

Result:

```text
Status: FAILED
Scenarios: 8
Checks: 116
Passed: 114
Failed: 2
Operator API auth: AUTH_OK
Contact form submitted: NO
Real contact data sent: NO
Lead/task/customer intentionally created: NO
```

The script used the production backend with Netlify Origin and authenticated only to the Operator API using the existing ignored local credential pattern. Credentials and tokens were not printed.

## Scenario Results

| # | Scenario | Chatbot behavior | Operator CRM/API visibility | Result |
| --- | --- | --- | --- | --- |
| 1 | Official KB answer: Bachelor ECTS | Returned source-backed answer with 240 ECTS | Conversation visible with visitor and AI messages, but incorrectly marked `human_handover=true` / `needs operator` | FAIL |
| 2 | Clarification: `სწავლა მაინტერესებს` | Asked clarification with options | Conversation visible, AI clarification visible, no handover, no customer/lead | PASS |
| 3 | Finance route/handover | Routed Finance and offered handover | Finance badge visible, handover visible, no customer/lead | PASS |
| 4 | Library route | Routed Library and offered operator fallback when source missing | Library badge visible, not International Admissions, no customer/lead | PASS |
| 5 | IT route | Routed IT Support | IT Support badge visible, no customer/lead | PASS |
| 6 | Medicine / MD route | Routed Medicine / MD | Medicine / MD badge visible with expected spacing, no customer/lead | PASS |
| 7 | Unsupported/no hallucination | Did not invent scholarship information; offered operator handover | Conversation visible, handover visible, no customer/lead | PASS |
| 8 | Wait for operator | `/chat/handover` returned `waiting_for_operator` without contact data | Inbox/detail show `waiting_for_operator`, `human_handover=true`, selected department, messages, no customer/lead | PASS |

## Contact Form UI Check

Contact form submission was not executed because contact-flow approval remains NOT_APPROVED.

Verified from frontend source and previous live visual QA evidence:

- `სახელი და გვარი`
- `ტელეფონი`
- `ენა`
- `ელ.ფოსტა`
- `ინტერესის სფერო`
- `თქვენი კითხვა / შეტყობინება`
- consent checkbox
- submit button

The textarea prefill logic prefers the latest visitor question. User can edit the textarea before any submission.

CONTACT_FLOW_EXECUTED=NO

## Wait-For-Operator Result

Wait-for-operator integration passed.

Observed production-safe API result:

- `/chat/handover/{conversation_id}` returned `status=waiting_for_operator`.
- Operator CRM detail returned conversation status `waiting_for_operator`.
- Operator CRM detail returned `human_handover=true`.
- Operator CRM inbox contained the conversation.
- Latest visitor message and AI message were visible in detail.
- No customer, lead, or task was attached by the wait flow.

## Lead Customer Task Safety

Informational, clarification, unsupported, route/handover, and wait-for-operator checks did not create lead/customer/task records.

Observed:

- `created_lead_id=null` in chat responses.
- `created_task_id=null` in chat responses.
- Operator detail `customer=null`.
- Operator detail `lead=null`.
- Wait-for-operator response `task_id=null`.

LEAD_TASK_CUSTOMER_CREATED=NO

## Known Limitation

VISITOR_SIDE_OPERATOR_REPLY_POLLING=NOT_ACTIVE

`pollOperatorMessages()` exists in the final widget path, but the visitor-side live operator reply polling is not active in the final bundle. Operator CRM can write operator replies to the backend, but this QA does not prove that those replies stream back into the visitor widget.

## Bugs Found

### BUG-9AQ-ALIGN-01 - Source-backed informational answer is marked as operator handover

Question:

```text
რამდენი ECTS კრედიტია საჭირო საბაკალავრო პროგრამის დასასრულებლად?
```

Expected:

- Chatbot answers from approved source.
- Answer includes 240 ECTS.
- No contact data requested.
- No lead/task/customer created.
- No operator handover is required for this informational answer.
- Operator CRM may show the conversation as a normal website chat, but should not mark it as `needs operator` unless the visitor asks for operator help.

Observed:

- Answer was source-backed and correct.
- `should_handover=true` in chatbot response metadata.
- Operator CRM detail and inbox showed `human_handover=true`.
- Selected department was `Study Process`, which is not one of the public chatbot sidebar labels in the expected mapping.
- No customer, lead, or task was created.

Impact:

Operator inbox can be polluted by normal informational conversations that do not need an operator. This is an alignment bug between chatbot behavior and Operator CRM triage semantics.

Recommended fix:

- Keep optional handover UI available where appropriate, but do not persist `human_handover=true` for source-backed informational answers unless the visitor explicitly chooses contact/wait/operator or the route genuinely requires operator handling.
- Normalize `Study Process` routing display to an approved public/CRM department label or document it as an internal-only route if it must remain.

## Recommendation

Ready for public launch: NO-GO

Phase 9AQ should remain failed pending fixes because one verified integration bug affects Operator CRM triage accuracy.

Recommended next phase:

Phase 9AR - Fix informational-answer handover metadata and Operator CRM routing label alignment, then rerun the 9AQ production-safe alignment QA.
