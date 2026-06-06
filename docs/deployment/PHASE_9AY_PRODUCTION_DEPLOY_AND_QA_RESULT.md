# Phase 9AY Production Deploy and QA Result

`PHASE_9AY_DEPLOY_STATUS=PASSED_PENDING_APPROVALS`

Decision state:

`BACKEND_DEPLOYED_FULL_KNOWLEDGE_AND_PUBLIC_ANSWER_CLEANUP_VERIFIED_PENDING_APPROVALS`

Public launch:

`NO-GO`

## Backend Deploy

- Service: `alte-ai-crm-backend`
- Region: `europe-west1`
- Cloud Run revision: `alte-ai-crm-backend-00051-btg`
- Image tag: `v0.9-phase-9ax-9ay-final-routing-cleanup3`
- Image digest: `sha256:a2680fc7fb440b1b7f4dcad2b856bf63dd7c86aca82e4498c1e3171825a7c17f`
- Traffic: 100%
- Backend URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`

## Commits

- `7f0bff1` - `phase 9ay: clean public answers and source labels`
- `170de19` - `phase 9ay: preserve admissions document wording`
- `2342dda` - `phase 9ay: preserve status suspension grounds answer`

## Production QA

- Focused 9AT QA: `7/7 PASS`
- Full 9AS QA: `53/53 PASS`
- Operator alignment QA: `7/7 PASS`
- Browser/API answer-cleanliness QA: `7/7 PASS`
- Remaining failures/gaps: none

## Answer-Cleanliness Verification

Representative production answers were checked through the same `/chat/session/start` and `/chat/message` widget API path with the Netlify test origin.

Verified clean answers:

- Bachelor ECTS answer includes `240 ECTS`.
- Master ECTS answer includes `120 ECTS`.
- Student status suspension duration answer includes the 5-year maximum.
- Student status suspension grounds answer lists grounds and is not the duration-only answer.
- Computer Science spring calendar answer includes `9-14 March` and `30 March`.
- Admission without national exams routes to the admissions answer.
- English-language program requirements route to International Admissions.

No checked public answer contained:

- `official_academic_rules`
- `chunk`
- `page 22`
- `p022_c050`
- `Policy:`
- `Reference:`
- `Official source:`
- `answer only from`
- `handover if`
- `source_group`

No checked informational answer set handover metadata.

## Program Catalog Status

- Program Catalog QA remains previously verified at `10/10 PASS`.
- Program Catalog source: `01_program_catalog.pdf` / Higher Education Program Catalog.
- No hallucinated tuition amount was observed in Program Catalog QA.

## Post-Deploy Checks

- Compileall: PASS
- Backend pytest: `1046 passed`
- Phase 9AX verifier: PASS
- Phase 9AY cleanup tests: `15 passed`

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
