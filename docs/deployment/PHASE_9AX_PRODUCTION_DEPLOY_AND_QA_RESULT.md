# Phase 9AX / 9AY Production Deploy and QA Result

`PHASE_9AX_9AY_DEPLOY_STATUS=PASSED_PENDING_APPROVALS`

Decision state:

`BACKEND_DEPLOYED_FULL_KNOWLEDGE_AND_PUBLIC_ANSWER_CLEANUP_VERIFIED_PENDING_APPROVALS`

Public launch:

`NO-GO`

## Deployment

- Branch pushed: `origin/phase-9s-agent-preview-cors-note`
- 9AX code commit: `5638944` (`phase 9ax: fix final full knowledge routing failures`)
- 9AX follow-up routing commit: `4d1942c` (`phase 9ax: fix final department routing failure`)
- 9AY cleanup commit: `7f0bff1` (`phase 9ay: clean public answers and source labels`)
- 9AY admissions wording hotfix: `170de19` (`phase 9ay: preserve admissions document wording`)
- 9AY status grounds hotfix: `2342dda` (`phase 9ay: preserve status suspension grounds answer`)
- Backend image tag: `v0.9-phase-9ax-9ay-final-routing-cleanup3`
- Image digest: `sha256:a2680fc7fb440b1b7f4dcad2b856bf63dd7c86aca82e4498c1e3171825a7c17f`
- Cloud Run revision: `alte-ai-crm-backend-00051-btg`
- Traffic split: `alte-ai-crm-backend-00051-btg` serving 100%
- Production backend URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`

The deploy updated the existing Cloud Run service image only. It used the same service, region, DB attachment, Secret Manager mappings, and CORS configuration.

## Production QA

- Focused Phase 9AT knowledge fixes QA: `7/7 PASS`
- Full Phase 9AS knowledge coverage QA: `53/53 PASS`
- Operator alignment QA: `7/7 PASS`
- Browser/API answer-cleanliness QA: `7/7 PASS`
- Remaining failures/gaps: none

## Full 9AS Category Results

| Category | Passed | Total |
| --- | ---: | ---: |
| official_academic_facts | 17 | 17 |
| academic_calendar | 9 | 9 |
| admissions | 6 | 6 |
| clarification | 6 | 6 |
| routing | 6 | 6 |
| unsupported | 4 | 4 |
| operator_handover | 5 | 5 |

## Verified Fixes

- `admission_without_exams_ka`: routes to Admissions / `admissions_rules`.
- `english_program_requirements_en`: routes to International Admissions / `international_admissions_sources`.
- Bachelor admission documents answer includes the expected Georgian `საბუთ` wording.
- Student status suspension duration and suspension grounds now produce distinct public answers.
- Public answers do not expose internal source IDs, source-group IDs, page/chunk labels, or prompt-control text.

## Post-Deploy Checks

- Compileall: PASS
- Backend pytest: `1046 passed`
- Phase 9AX verifier: PASS
- Phase 9AY cleanup tests: `15 passed`

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

## Remaining Blockers

- Privacy URL
- Contact-flow approval
- Asset upload approval
- Staged real-site embed approval
- Real-domain smoke
- Dirty tree reconciliation
- Final public launch approval
