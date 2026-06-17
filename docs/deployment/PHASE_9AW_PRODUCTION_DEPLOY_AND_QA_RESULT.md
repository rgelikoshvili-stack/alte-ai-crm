# Phase 9AW Production Deploy and QA Result

`PHASE_9AW_DEPLOY_STATUS=FAILED_PENDING_FIXES`

Decision state:

`BACKEND_DEPLOYED_9AV_FAILURE_TUNING_QA_FAILED_PENDING_FIXES`

Public launch:

`NO-GO`

## Deployment

- Code commit: `a6ed854` (`phase 9aw: tune 9av knowledge coverage failures`)
- Branch pushed: `origin/phase-9s-agent-preview-cors-note`
- Backend image tag: `v0.9-phase-9aw-9av-failure-tuning`
- Backend image: `europe-west1-docker.pkg.dev/project-1e145fd0-c30e-4aac-a34/alte-ai-crm/alte-ai-crm-backend:v0.9-phase-9aw-9av-failure-tuning`
- Cloud Run service: `alte-ai-crm-backend`
- Cloud Run region: `europe-west1`
- New revision: `alte-ai-crm-backend-00043-x9s`
- Traffic split: `alte-ai-crm-backend-00043-x9s` serving 100%
- Production backend URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`

The deploy updated the existing Cloud Run service image only. No migration, seed, schema change, DB import, Secret Manager change, CORS change, Bridge Hub change, frontend change, Netlify deploy, real-site upload, or real-site embed was performed.

## Pre-Commit Verification

- `python -m compileall app`: PASS
- Full backend pytest: PASS, 1006 passed
- Phase 9AW verifier: PASS
- Local Phase 9AW QA: PASS, 19/19
- Final review: No blocking issues found

## Production QA

Focused Phase 9AT knowledge fixes QA:

- Status: PASS
- Passed: 7/7
- Contact flow executed: NO
- Real contact data sent: NO
- Lead/task/customer created: NO

Operator alignment QA:

- Status: PASS
- Passed: 7/7
- Operator API auth: AUTH_OK
- Explicit operator/wait flows preserved: VERIFIED
- Informational answers excluded from handover queue: VERIFIED
- Lead/task/customer created: NO

Full Phase 9AS knowledge coverage QA:

- Status: FAILED
- Total: 53
- Passed: 51
- Failed: 2
- Skipped: 0
- Contact flow executed: NO
- Real contact data sent: NO
- Lead/task/customer created: NO

## Category Results

| Category | Passed | Total |
| --- | ---: | ---: |
| official_academic_facts | 17 | 17 |
| academic_calendar | 9 | 9 |
| admissions | 4 | 6 |
| clarification | 6 | 6 |
| routing | 6 | 6 |
| unsupported | 4 | 4 |
| operator_handover | 5 | 5 |

## Remaining Failures

- `admission_without_exams_ka`: expected admissions source group, observed `exams_and_assessment`.
- `english_program_requirements_en`: expected International Admissions route, observed `programs / Programs`.

These are remaining routing/source-selection bugs, not missing approved-source gaps.

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

Do not approve public launch. Phase 9AW improved full 9AS production coverage from `32/53` to `51/53`, while keeping focused 9AT and operator alignment QA passing, but the two remaining admissions failures require a follow-up fix.
