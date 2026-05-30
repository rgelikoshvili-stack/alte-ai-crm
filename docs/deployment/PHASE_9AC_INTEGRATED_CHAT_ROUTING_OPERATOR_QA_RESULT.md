# Phase 9AC Integrated Chat Routing Operator QA Result

PHASE_9AC_INTEGRATED_QA_STATUS=FAILED_PENDING_ROUTING_OR_KB_FIX

Decision state:

```text
BACKEND_DEPLOYED_INTEGRATED_CHAT_ROUTING_QA_FAILED_PENDING_FIX
```

## Scope

- Backend URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Netlify chatbot URL: `https://nimble-croissant-2f66e8.netlify.app/join.html`
- Operator CRM URL: `http://127.0.0.1:5173`
- Production backend revision expected from audit: `alte-ai-crm-backend-00030-td7`
- Origin used for chat QA: `https://nimble-croissant-2f66e8.netlify.app`
- Real Alte site modified: NO
- Real `join.alte.edu.ge` modified: NO
- Backend behavior changed: NO
- CORS changed: NO
- Production migrations run: NO
- Production seed run: NO
- Contact details sent: NO
- Intentional lead/task/customer creation: NO
- Public launch: NO-GO

## Baseline Service Results

| Check | Result |
| --- | --- |
| Backend `GET /health` | 200 PASS |
| Backend `GET /version` | 200 PASS |
| Backend `GET /diagnostics/ai` | 200 PASS |
| Backend `GET /dashboard/overview` without auth | 401 PASS |
| Netlify `GET /join.html` | 200 PASS |
| Local Operator CRM static UI | 200 PASS |
| Operator production login using ignored local credential file | PASS |
| Operator dashboard after login | 200 PASS |
| Operator inbox/conversations after login | 200 PASS |

Operator CRM visibility observation:

- Dashboard reported existing conversations.
- Dashboard latest conversations returned rows.
- Inbox returned rows.
- Recent anonymous/chat sessions are visible through the operator surfaces if they are included in the backend inbox/dashboard query.
- No contact details were submitted and no new production lead/task/customer was intentionally created.

## Integrated QA Summary

Script:

```text
python -m app.scripts.production_integrated_chat_routing_operator_qa
```

Sanitized JSON artifact:

```text
docs/deployment/PHASE_9AC_INTEGRATED_CHAT_ROUTING_OPERATOR_QA_RESULT.json
```

Result:

- Total cases: 18
- Passed: 15
- Failed: 3
- Official KB answer cases: 6/6 passed
- Auto-routing cases: 8/10 passed
- Handover/contact-safety cases: 1/2 passed
- Any direct request for contact details: NO
- Any lead/task/customer created: NO

## Official KB Answer QA

All source-backed official KB checks passed.

| Case | Expected | Result |
| --- | --- | --- |
| Bachelor ECTS | `240`, not `180`, source-backed | PASS |
| Master ECTS | `120`, source-backed | PASS |
| Teaching language | Georgian plus some English programs, no invented planned list | PASS |
| Student status suspension | max total `5` years, source-backed | PASS |
| Computer Science spring registration | `9-14 March`, semester starts `30 March` | PASS |
| Master admission documents | ID copy, CV, 3x4 photo, military registration copy for male applicants, notarized diploma copy, diploma supplement copy | PASS |

Official facts remain intact:

- Bachelor completion: `240 ECTS`, not `180`.
- Master program: `120 ECTS`.
- Student status suspension: maximum total `5 years`.
- Computer Science spring registration: `9-14 March`; semester starts `30 March`.
- Unsupported questions must return no approved source or conservative operator confirmation.

## Auto-Routing QA

| Case | Expected Route | Result |
| --- | --- | --- |
| Admissions: bachelor enrollment | Admissions / Registration / Student services | FAIL: routed to `Programs` / `programs` |
| Programs broad question | Programs / Admissions or clarification | PASS |
| Finance payment schedule | Finance / Tuition | PASS |
| Student status pause | Study process / Student status / Registrar | PASS |
| Exam absence with valid reason | Exams / Study process | PASS |
| Mobility and credit recognition | Mobility / ECTS / Study process | PASS |
| International student Medicine | International admissions / Medicine / MD | PASS |
| IT help for `emis.alte.edu.ge` | IT help / Student support | PASS |
| Library resources | Library | FAIL: routed to `International Admissions` / `international` |
| Unsupported 2031 scholarship | `no_approved_source_found`, no hallucination | PASS |

Failures are routing/department inference failures, not contact-safety failures.

## Handover And Contact-Safety QA

| Case | Expected | Result |
| --- | --- | --- |
| General operator request | handover intent true, no direct contact details request | PASS |
| Finance department handover for tuition | finance route plus handover/conservative operator recommendation | FAIL: handover true but routed to `International Admissions` / `international` |

Contact-safety checks:

- No assistant answer asked the user to type phone, email, full name, or WhatsApp.
- No contact details were sent.
- No approved contact-flow was executed.
- No lead/task/customer was intentionally created.

## Weak Areas / Required Fix

Three integrated QA failures require routing inference adjustment:

1. Bachelor enrollment wording should route to Admissions or Registration, not Programs.
2. Library resource wording should route to Library, not International Admissions.
3. Finance department handover about tuition should route to Finance, not International Admissions.

The official KB answer layer is passing; the failing area is department inference/routing for selected phrases.

## Production DB Write Status

No production migrations were run.  
No production seed was run.  
No contact details were sent.  
No intentional lead/task/customer creation occurred.

Chat session/message rows may be created by normal `/chat/session/start` and `/chat/message` smoke behavior. No contact or CRM lead/task/customer creation flow was executed.

## Final Recommendation

Public launch remains blocked:

```text
PUBLIC_LAUNCH_RECOMMENDATION=NO_GO_PENDING_ROUTING_FIX_MOBILE_VISUAL_QA_PRIVACY_URL_FINAL_SITE_EMBED_APPROVAL_REAL_DOMAIN_SMOKE
```

Remaining blockers:

- Fix the three routing failures above.
- Re-run Phase 9AC integrated QA.
- Netlify redeploy and mobile visual QA after Phase 9AB responsive fix.
- Official privacy URL.
- Contact-flow approval.
- Final asset URL.
- Staged real-site embed approval.
- Real-domain smoke after approved embed.
- Dirty working tree reconciliation.
- Final public launch GO.
