# Phase 9AT Knowledge Coverage Fix Result

PHASE_9AT_STATUS=CODE_READY_PENDING_BACKEND_DEPLOY

Decision state:
BACKEND_DEPLOYED_FULL_KNOWLEDGE_COVERAGE_CODE_READY_PENDING_BACKEND_DEPLOY

Public launch: NO-GO

## Scope

Phase 9AT addresses Phase 9AS knowledge coverage failures in backend routing, retrieval, source relevance, and handover metadata.

No real Alte site, asset upload, frontend deploy, DB schema change, migration, seed, Secret Manager, CORS, Bridge Hub, contact-flow submission, lead, customer, or task creation was performed.

## 9AS Failure Summary

- Full knowledge QA: 53 questions, 11 passed, 42 failed.
- Operator alignment QA: 7 scenarios, 6 passed, 1 failed.
- Main failures: calendar mapping, admissions mapping, generic AI fallback for source-backed topics, unsupported false positives, and IT/EMIS handover persistence.

Failure matrix:

- `docs/evaluation/PHASE_9AT_9AS_FAILURE_MATRIX.md`

## Fixes Made Locally

- Calendar/admissions/IT/career keyword routing now runs before generic scoring.
- `academic_calendar_2025_2026` is selected for calendar, registration, semester, midterm, final, retake, holiday, and Computer Science spring prompts.
- `admissions_rules` is selected for admission, enrollment, documents, foreign applicant, foreign education recognition, and national exam prompts.
- Empty-source groups such as finance, library, IT support, and career return `no_approved_source_found` instead of matching unrelated approved snippets.
- Routed source groups now trigger knowledge checks even if the AI intent is not one of the older knowledge-required intents.
- Source-backed replies that would otherwise show generic AI-service fallback text now use conservative grounded answers for approved official facts, calendar, admissions, Medicine/Dentistry ECTS, mobility, credit recognition, GPA, FX/F, final exams, and retakes.
- Unsupported fake future/campus/tuition/library/password prompts are blocked from unrelated approved-source matches.
- No-approved-source fallback now persists handover metadata consistently, including IT/EMIS fallback.
- Phase 9AT weak-route extension: finance/grants, library, IT/EMIS/platform support, IRO, EDI, and sustainability selected-document topics now get explicit routing/retrieval aliases.
- Selected-document policy retrieval now searches targeted `alte.edu.ge` categories before broad scoped retrieval only when a precise category is known, preventing broad/unrelated policy snippets from winning.
- Library, IT, and career source groups now have active selected-source file keys and allow exact approved-source answers instead of forcing empty-group fallback.
- IRO selected documents are mapped to the correct production selected-45 source keys and `alte.edu.ge` domain.
- Department routing now handles grants, library, IT policy/platform support, IRO, EDI, and sustainability while preserving Medicine / MD and mixed student-services routing behavior.

## Weak Route Root Causes

- Grants / state grants / Dean's List: finance source group was effectively empty for selected documents, and selected-document retrieval did not target finance/grant categories before broad fallback.
- Library: `library_sources` had no source files and `exact_answer_allowed=false`, so approved selected library documents could not be used.
- IT / EMIS / platform support: `it_support_sources` had no source files and `exact_answer_allowed=false`; EMIS/platform terms were under-scored outside narrow login wording.
- IRO: international-admissions selected sources referenced stale/wrong selected source keys and the group pointed at `official_academic_rules` instead of selected `alte.edu.ge` policy documents.
- EDI / sustainability: policy topics had no precise selected-document category routing, so they could fall through to broad admissions/academic retrieval or no-source.
- Policy-topic relevance: selected-document searches could use broad `alte.edu.ge` retrieval when no precise category was known; this allowed unrelated policy/marketing snippets to match. The new path requires a precise selected category before `alte.edu.ge` selected-source retrieval.

## Calendar Coverage Result

Local regression coverage: PASS

- Computer Science spring registration returns 9-14 March.
- Computer Science semester start returns 30 March.
- Calendar prompts route to `academic_calendar_2025_2026`.

Production coverage: PENDING_BACKEND_DEPLOY

The production backend still runs the pre-9AT revision until deployment is approved.

## Admissions Coverage Result

Local regression coverage: PASS

- Bachelor admission document prompts route to `admissions_rules`.
- Master admission document prompts route to `admissions_rules`.
- Master document answer no longer falls back to generic AI-service text when an approved source is found.

Production coverage: PENDING_BACKEND_DEPLOY

## Unsupported False-Positive Result

Local regression coverage: PASS

- Future fake scholarship returns `no_approved_source_found`.
- Unsupported exact tuition for a fake 2031 AI space program returns `no_approved_source_found`.
- Unsupported prompts do not create lead/task/customer.

Production coverage: PENDING_BACKEND_DEPLOY

## IT/EMIS Handover Persistence Result

Local regression coverage: PASS

- EMIS login failure routes to IT Support.
- Empty IT source group returns `no_approved_source_found`.
- Chat response sets `should_handover=true`.
- Conversation persists `human_handover=true`.
- No lead/customer/task is created.

Production coverage: PENDING_BACKEND_DEPLOY

## Tests Run

```text
python -m compileall app
PASS

python -m pytest app/tests/test_ai_provider_failure_fallback.py app/tests/test_chat_source_conflicts_and_aliases.py::test_master_documents_financial_support_and_ai_policy_aliases app/tests/test_department_routing_service.py::test_spec_medicine_md_route app/tests/test_phase_9ai_chatgpt_style_kb_clarification_operator.py::test_phase_9ai_chatgpt_style_routing_guards app/tests/test_phase_9ai_knowledge_source_routing_clarification.py::test_phase_9ai_international_medicine_requires_explicit_international_context app/tests/test_phase_9at_knowledge_coverage_fixes.py -q
15 passed

python -m pytest app/tests/test_phase_9at_knowledge_coverage_fixes.py -q
8 passed

python -m pytest --basetemp .pytest_tmp_9at_knowledge_fixes_rerun
940 passed

python -m pytest app\tests\test_phase_9at_knowledge_coverage_fixes.py -q
9 passed

python -m pytest app\tests\test_chat_source_conflicts_and_aliases.py::test_master_documents_financial_support_and_ai_policy_aliases app\tests\test_chat_source_conflicts_and_aliases.py::test_selected_official_doc_question_does_not_fall_back_to_marketing_or_local_kb app\tests\test_department_routing_service.py::test_student_services_question_routes_to_student_services app\tests\test_department_routing_service.py::test_spec_medicine_md_route app\tests\test_phase_9at_knowledge_coverage_fixes.py -q
13 passed

python -m pytest --basetemp .pytest_tmp_9at_weak_routes_rerun
941 passed

python -m app.scripts.verify_phase_9at_knowledge_coverage_fixes
PASS

python -m app.scripts.production_phase_9at_knowledge_fixes_qa
7 checks: 2 passed, 5 failed against the current live pre-9AT backend

python -m app.scripts.production_phase_9as_full_knowledge_coverage_qa
53 questions: 11 passed, 42 failed against the current live pre-9AT backend

python -m app.scripts.production_phase_9as_operator_alignment_qa
7 scenarios: 6 passed, 1 failed against the current live pre-9AT backend
```

The first full pytest attempt hit Windows temp-directory cleanup errors against `.pytest_tmp_9at_knowledge_fixes` after 894 tests had passed. The temp directory was removed inside the backend workspace and pytest was rerun with `.pytest_tmp_9at_knowledge_fixes_rerun`, which passed 940/940.

Focused production QA still reflects the old live backend because Phase 9AT has not been deployed. No production deploy was performed in this phase.

## Safety

- Real Alte site modified: NO
- REAL_ALTE_SITE_MODIFIED=NO
- Asset upload executed: NO
- Real-site embed executed: NO
- Production DB schema changed: NO
- Production DB migration run: NO
- Production seed run: NO
- Secret Manager changed: NO
- CORS changed: NO
- Bridge Hub touched: NO
- CONTACT_FLOW_EXECUTED=NO
- REAL_CONTACT_DATA_SENT=NO
- LEAD_TASK_CUSTOMER_CREATED=NO
- Public launch: NO-GO

## Remaining Gaps

- Production Cloud Run has not been redeployed with 9AT code.
- Production KB weak-route retest is pending deploy approval for grants/library/IT/IRO/EDI/sustainability and policy-topic relevance.
- Focused production 9AT QA still fails 5/7 checks on the current live backend because it has not received the 9AT backend changes.
- Full Phase 9AS production rerun still reports the pre-9AT baseline of 11/53 passed because the live backend has not received the local fix.
- Operator alignment production rerun still reports the pre-9AT baseline of 6/7 passed because the live backend has not received the local fix.
- Some broad QA expectations may still require tuning after production rerun, especially contact-form-open prompts that are better validated by browser UI QA than `/chat/message`.

## Final Recommendation

Phase 9AT code status: CODE_READY_PENDING_BACKEND_DEPLOY

Recommended next action:

Request explicit approval to deploy the 9AT backend fix to Cloud Run. After deploy, rerun:

- `python -m app.scripts.production_phase_9at_knowledge_fixes_qa`
- `python -m app.scripts.production_phase_9as_full_knowledge_coverage_qa`
- `python -m app.scripts.production_phase_9as_operator_alignment_qa`
- Retest live weak-route cases: Dean's List/state grants, library resources, EMIS/platform support, IRO Policy, EDI Policy, sustainability strategy/report, AI/policy-topic false positives, and unsupported future/fake scholarship.
