# Phase 9AX Production Deploy and QA Result

`PHASE_9AX_DEPLOY_STATUS=PASSED_PENDING_APPROVALS`

Decision state:

`BACKEND_DEPLOYED_FULL_KNOWLEDGE_QA_PASSED_PENDING_APPROVALS`

Public launch:

`NO-GO`

## Deployment

- Code commit: `5638944` (`phase 9ax: fix final full knowledge routing failures`)
- Follow-up routing commit: `4d1942c` (`phase 9ax: fix final department routing failure`)
- Branch pushed: `origin/phase-9s-agent-preview-cors-note`
- First backend image tag: `v0.9-phase-9ax-final-knowledge-routing-fix`
- First Cloud Run revision: `alte-ai-crm-backend-00044-wlp`
- Final backend image tag: `v0.9-phase-9ax-final-knowledge-routing-fix2`
- Final Cloud Run revision: `alte-ai-crm-backend-00045-dg2`
- Traffic split: `alte-ai-crm-backend-00045-dg2` serving 100%
- Production backend URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`

The deploy updated the existing Cloud Run service image only. No migration, seed, schema change, DB import, Secret Manager change, CORS change, Bridge Hub change, frontend change, Netlify deploy, real-site upload, or real-site embed was performed.

## Production QA

Focused Phase 9AT knowledge fixes QA:

- Status: PASS
- Passed: 7/7
- Contact flow executed: NO
- Real contact data sent: NO
- Lead/task/customer created: NO

Full Phase 9AS knowledge coverage QA:

- Status: PASS
- Total: 53
- Passed: 53
- Failed: 0
- Skipped: 0
- Contact flow executed: NO
- Real contact data sent: NO
- Lead/task/customer created: NO

Operator alignment QA:

- Status: PASS
- Passed: 7/7
- Operator API auth: AUTH_OK
- Contact flow executed: NO
- Real contact data sent: NO
- Lead/task/customer created: NO

## Category Results

| Category | Passed | Total |
| --- | ---: | ---: |
| official_academic_facts | 17 | 17 |
| academic_calendar | 9 | 9 |
| admissions | 6 | 6 |
| clarification | 6 | 6 |
| routing | 6 | 6 |
| unsupported | 4 | 4 |
| operator_handover | 5 | 5 |

## Fixed Failures

- `admission_without_exams_ka`: now routes to Admissions / `admissions_rules`.
- `english_program_requirements_en`: now routes to International Admissions / `international_admissions_sources`.

## Safety Confirmations

- Real Alte site modified: NO
- Assets uploaded or embedded: NO
- Frontend/Netlify changed: NO
- Contact creation flow executed: NO
- Real contact data sent: NO
- Lead/customer/task created: NO
- DB schema changed: NO
- Migration run: NO
- Seed/import run: NO
- Secret Manager changed: NO
- CORS changed: NO
- Bridge Hub touched: NO
- Public launch: NO-GO

## Recommendation

Phase 9AX production QA passed all critical knowledge and operator checks. Public launch still remains NO-GO pending non-QA approvals and launch governance.
