# Phase 9AT Knowledge Coverage Fix Result

PHASE_9AT_STATUS=FAILED_PENDING_FURTHER_KB_FIXES

Decision state:
BACKEND_DEPLOYED_FULL_KNOWLEDGE_COVERAGE_STILL_FAILING_PENDING_FIXES

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

Production coverage after deploy: IMPROVED, 8/9 calendar checks passed in full 9AS rerun.

## Admissions Coverage Result

Local regression coverage: PASS

- Bachelor admission document prompts route to `admissions_rules`.
- Master admission document prompts route to `admissions_rules`.
- Master document answer no longer falls back to generic AI-service text when an approved source is found.

Production coverage after deploy: IMPROVED, 5/6 admissions checks passed in full 9AS rerun.

## Unsupported False-Positive Result

Local regression coverage: PASS

- Future fake scholarship returns `no_approved_source_found`.
- Unsupported exact tuition for a fake 2031 AI space program returns `no_approved_source_found`.
- Unsupported prompts do not create lead/task/customer.

Production coverage after deploy: IMPROVED, focused 9AT false-positive checks passed; full 9AS still has 2 unsupported-category failures needing follow-up.

## IT/EMIS Handover Persistence Result

Local regression coverage: PASS

- EMIS login failure routes to IT Support.
- Empty IT source group returns `no_approved_source_found`.
- Chat response sets `should_handover=true`.
- Conversation persists `human_handover=true`.
- No lead/customer/task is created.

Production coverage after deploy: PASS in focused 9AT QA. EMIS/IT access routes to IT Support and persists `human_handover=true` without lead/customer/task creation.

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

Pre-deploy gate:
python -m compileall app
PASS

python -m pytest --basetemp .pytest_tmp_9at_predeploy
941 passed

python -m app.scripts.verify_phase_9at_knowledge_coverage_fixes
PASS

Code commit:
dc54c7a phase 9at: fix knowledge coverage routing

Follow-up production patches:
1026e62 phase 9at: tighten production knowledge qa routing
060ac27 phase 9at: persist it access handover

Backend image tag:
v0.9-phase-9at-knowledge-coverage-fix

Final Cloud Run revision:
alte-ai-crm-backend-00040-8qr

python -m app.scripts.production_phase_9at_knowledge_fixes_qa
7 checks: 7 passed, 0 failed

python -m app.scripts.production_phase_9as_full_knowledge_coverage_qa
53 questions: 33 passed, 20 failed
Calendar: 8 passed, 1 failed
Admissions: 5 passed, 1 failed

python -m app.scripts.production_phase_9as_operator_alignment_qa
7 scenarios: 6 passed, 1 failed
```

The first full pytest attempt hit Windows temp-directory cleanup errors against `.pytest_tmp_9at_knowledge_fixes` after 894 tests had passed. The temp directory was removed inside the backend workspace and pytest was rerun with `.pytest_tmp_9at_knowledge_fixes_rerun`, which passed 940/940.

Production deploy was performed for Phase 9AT only. No DB schema change, migration, seed, Secret Manager change, CORS change, real-site change, asset upload, or contact-flow execution was performed.

## Production Verification Summary

- Commit SHA for deployed code path: `060ac27`
- Image tag: `v0.9-phase-9at-knowledge-coverage-fix`
- Cloud Run revision: `alte-ai-crm-backend-00040-8qr`
- Focused 9AT production QA: PASS, 7/7.
- Full 9AS production QA: IMPROVED but FAILED, 33/53 passed.
- Operator alignment QA: IMPROVED/UNCHANGED but FAILED, 6/7 passed.
- Calendar coverage: 8/9 passed, improved from 0/9.
- Admissions coverage: 5/6 passed, improved from 0/6.
- Unsupported false positives: focused 9AT checks passed; full 9AS still reports 2 unsupported failures.
- IT/EMIS handover: PASS in focused 9AT QA, `human_handover=true` persisted with no lead/customer/task.

## Remaining Production Failures

Full 9AS still reports 20 failures after deployment. The main remaining buckets are:

- Some official academic fact expectations still fail due source group/routing mismatch or strict token checks.
- Some clarification/operator-handover scenarios still rely on `/chat/message` prompts that behave differently from widget button flows.
- Library and career now retrieve approved selected sources, so older fallback expectations need review.
- International Medicine and a few policy-adjacent questions still need tighter relevance controls to avoid unrelated selected-policy snippets.
- Unsupported tuition/library cases still need another relevance pass or expectation correction depending on approved-source availability.

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

- Production is deployed with 9AT code, but full 9AS remains failed at 33/53.
- Focused weak-route checks pass, but broad full-coverage QA still shows 20 remaining failures.
- Operator alignment still has one failed scenario: `library_operator_fallback`, likely because library now has approved selected sources and no longer follows the old empty-source fallback expectation.
- Some broad QA expectations still require tuning, especially contact-form-open and wait/operator prompts that are better validated by browser UI actions than `/chat/message`.
- Further KB relevance work is needed for remaining official academic facts, international medicine routing, unsupported tuition/library cases, and policy-adjacent source selection.

## Final Recommendation

Phase 9AT production status: FAILED_PENDING_FURTHER_KB_FIXES

Recommended next action:

Start a follow-up KB relevance phase focused on the 20 remaining full 9AS failures. Keep public launch blocked.
