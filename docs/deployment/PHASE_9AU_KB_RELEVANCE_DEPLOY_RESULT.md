# Phase 9AU KB Relevance Deploy Result

PHASE_9AU_DEPLOY_STATUS=FAILED_PENDING_FURTHER_FIXES

Decision state:
BACKEND_DEPLOYED_9AS_KB_RELEVANCE_STILL_FAILING_PENDING_FIXES

Public launch:
NO-GO

## Summary

Phase 9AU committed and deployed the follow-up KB relevance fixes that were verified locally after Phase 9AT. The backend deployment succeeded and production QA improved, but full 9AS still has remaining failures that require another follow-up pass before knowledge QA can be considered complete.

## Code Commit

- Commit: `0ece355`
- Commit message: `phase 9au: fix remaining knowledge relevance gaps`
- Pushed branch: `origin/phase-9s-agent-preview-cors-note`

## Committed Files

- `backend/app/services/chat_service.py`
- `backend/app/services/department_routing_service.py`
- `backend/app/services/knowledge_routing_service.py`
- `backend/app/tests/test_phase_9at_knowledge_coverage_fixes.py`
- `backend/app/data/evaluation/phase_9as_full_knowledge_qa.json`
- `backend/app/scripts/production_phase_9as_full_knowledge_coverage_qa.py`
- `backend/app/scripts/production_phase_9as_operator_alignment_qa.py`
- `docs/evaluation/PHASE_9AT_FOLLOWUP_9AS_FAILURE_TABLE.md`
- `docs/evaluation/PHASE_9AT_KNOWLEDGE_FIXES_QA_RESULT.md`
- `docs/evaluation/PHASE_9AS_FULL_KNOWLEDGE_COVERAGE_QA_RESULT.md`
- `docs/evaluation/PHASE_9AS_OPERATOR_CRM_ALIGNMENT_QA_RESULT.md`

## Backend Deploy

- Image tag: `v0.9-phase-9au-kb-relevance-followup`
- Image: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9au-kb-relevance-followup`
- Cloud Build status: SUCCESS
- Cloud Run service: `alte-ai-crm-backend`
- Region: `europe-west1`
- New revision: `alte-ai-crm-backend-00041-qxn`
- Traffic split: `alte-ai-crm-backend-00041-qxn=100%`

## Production QA Results

### Focused 9AT

- Script: `python -m app.scripts.production_phase_9at_knowledge_fixes_qa`
- Result: PASS
- Passed: 7/7
- Failed: 0

### Operator Alignment

- Script: `python -m app.scripts.production_phase_9as_operator_alignment_qa`
- Result: PASS
- Passed: 7/7
- Failed: 0
- Operator API auth/checks: AUTH_OK

### Full 9AS Knowledge Coverage

- Script: `python -m app.scripts.production_phase_9as_full_knowledge_coverage_qa`
- Result: FAILED
- Previous production baseline before 9AU deploy: 37/53 passed, 16 failed
- Current production result after 9AU deploy: 41/53 passed, 12 failed

Per-category result:

| Category | Total | Passed | Failed |
| --- | ---: | ---: | ---: |
| official_academic_facts | 17 | 15 | 2 |
| academic_calendar | 9 | 8 | 1 |
| admissions | 6 | 5 | 1 |
| clarification | 6 | 6 | 0 |
| routing | 6 | 4 | 2 |
| unsupported | 4 | 2 | 2 |
| operator_handover | 5 | 1 | 4 |

## Remaining Failures

| QA id | Classification | Notes |
| --- | --- | --- |
| `status_suspension_ka` | stale_expectation | Answer contains correct 5-year fact. The failure is caused by `10` appearing in source citation/page metadata. |
| `credit_recognition_ka` | retrieval_bug | Still retrieves foreign education recognition/admissions text instead of credit-recognition study-process text. |
| `calendar_retakes_ka` | stale_expectation | Calendar answer is source-backed but does not include the exact expected exam token. |
| `english_program_requirements_en` | retrieval_bug | Still routes to Programs / official_academic_rules instead of International Admissions sources. |
| `routing_finance_operator_ka` | operator_metadata_bug | Handover works, but the AI fallback text does not include the expected Finance wording. |
| `routing_international_medicine_en` | stale_expectation | Public workflow keeps international Medicine in Medicine / MD lane; dataset/source expectation still needs review. |
| `unsupported_tuition_price_ka` | unsupported_false_positive | Fake 2031 tuition/program prompt still exposes `admissions_rules` as source group. |
| `unsupported_library_rules_en` | stale_expectation | No-source fallback is correct, but expected wording requires `approved source` instead of `approved official sources`. |
| `operator_explicit_ka` | operator_metadata_bug | Explicit operator request sets handover, but fallback text does not include expected operator token. |
| `operator_wait_ka` | operator_metadata_bug | Wait action endpoint is correct, but message-path fallback text does not include expected operator token. |
| `operator_contact_form_open_ka` | operator_metadata_bug | Contact-form UI is covered separately, but message-path fallback text does not include expected contact token. |
| `operator_finance_handover_en` | operator_metadata_bug | English Finance handover routes, but fallback text does not include expected `Finance` token. |

## Safety Confirmations

- Real Alte site modified: NO
- Asset upload/embed executed: NO
- Frontend/Netlify changed: NO
- DB schema changed: NO
- Migration run: NO
- Seed run: NO
- Production DB import executed: NO
- Secret Manager changed: NO
- CORS changed: NO
- Bridge Hub touched: NO
- Contact flow with real data executed: NO
- Lead/task/customer intentionally created: NO
- Public launch remains: NO-GO

## Final Recommendation

Knowledge QA remains NO-GO. Production improved after deploying 9AU, but the remaining 12 full 9AS failures should be fixed or reclassified before owner approval or public launch review.

