# Phase 9AY Production Deploy And QA Result

Date: 2026-06-02

PHASE_9AY_DEPLOY_STATUS=PASSED_PENDING_APPROVALS

Decision state: `BACKEND_DEPLOYED_PROGRAM_CATALOG_SOURCE_QA_PASSED_PENDING_APPROVALS`

Public launch: `NO-GO`

## Backend Deploy

- Service: `alte-ai-crm-backend`
- Region: `europe-west1`
- Final Cloud Run revision: `alte-ai-crm-backend-00048-zk8`
- Final image tag: `v0.9-phase-9ay-program-catalog-source-routing3`
- Traffic: 100%
- Backend URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`

## Commits

- `4765680` - `phase 9ay: route program catalog questions to catalog source`
- `354507e` - `phase 9ay: preserve academic routing controls`
- `09d8a75` - `phase 9ay: add catalog grounded answer fallback`

## Production QA

- Program Catalog QA: 10/10 PASS
- Focused 9AT QA: 7/7 PASS
- Full 9AS QA: 53/53 PASS
- Operator alignment QA: 7/7 PASS

## Source-Backed Verification

- Program Catalog source group: `program_catalog_sources`
- Program Catalog source: `01_program_catalog.pdf` / Higher Education Program Catalog
- Program Catalog source metadata exposed in production responses: YES
- `official_academic_rules` is not the primary source group for Program Catalog questions.
- Library catalog and non-program list prompt disambiguation remain protected by local tests.
- Tuition question did not hallucinate a tuition amount.
- Remaining failures/gaps: none

## Post-Deploy Checks

- Compileall: PASS
- Backend pytest: `1029 passed`
- Phase 9AY verifier: PASS

## Safety Confirmation

- Real site modified: NO
- Upload/embed performed: NO
- Frontend/Netlify changed: NO
- Contact flow submitted: NO
- Real contact data sent: NO
- Lead/customer/task created: NO
- DB schema/migration/seed/import: NO
- Secret Manager/CORS/Bridge Hub changed: NO
- Public launch remains: NO-GO

## Remaining Blockers

- Privacy URL
- Contact-flow approval
- Asset upload approval
- Staged real-site embed approval
- Real-domain smoke
- Dirty tree reconciliation
- Final public launch approval
