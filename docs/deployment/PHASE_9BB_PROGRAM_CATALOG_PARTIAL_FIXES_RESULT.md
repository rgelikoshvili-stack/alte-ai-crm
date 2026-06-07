# Phase 9BB Program Catalog Partial Fixes Result

`PHASE_9BB_STATUS=CODE_READY_PENDING_BACKEND_DEPLOY`

Decision state:

`BACKEND_CODE_PROGRAM_CATALOG_PARTIAL_FIXES_READY_PENDING_DEPLOY`

Public launch: NO-GO

Deploy status: NOT_DEPLOYED_PENDING_APPROVAL

## Baseline

- Source QA baseline: Phase 9BA Program Catalog file-by-file QA
- File: `01_program_catalog.pdf`
- Source: Higher Education Program Catalog
- Phase 9BA result: 11 PASS / 9 PARTIAL / 0 FAIL
- Partial root causes:
  - wrong source
  - incomplete answer
  - clarification missing

## Triage

Full triage table:

`docs/evaluation/PHASE_9BB_PROGRAM_CATALOG_PARTIAL_TRIAGE.md`

All 9 PARTIAL cases are documented with question, expected answer, observed route/source, root cause, proposed fix, regression risk, and test coverage.

## Fixes Made

- Added catalog-scope priority for explicit Program Catalog ECTS and teaching-language prompts.
- Preserved generic academic-rule routing for non-catalog ECTS and teaching-language questions.
- Added punctuation-tolerant clarification for:
  - `კრედიტები მაინტერესებს.`
  - `პროგრამები მაინტერესებს.`
  - `კატალოგში პროგრამაზე ინფორმაცია მაინტერესებს.`
- Added deterministic Program Catalog answers for:
  - bachelor credits: 240 ECTS
  - master credits: 120 ECTS
  - Law bachelor teaching language: Georgian
  - English-language catalog program versions
  - AI/Data Analytics Georgian and English-language versions
- Treated consultant phone number requests as unsupported/no approved source, preventing phone-number hallucination and avoiding source-backed retrieval.

## Local QA

- Compileall: PASS
- Focused Phase 9BB regression tests: 11 passed
- Local Phase 9BB QA script: PASS
- Full backend pytest: 1070 passed
- Phase 9BB verifier: PASS

## Expected Production Result

After an approved backend deploy, the 9 Phase 9BA PARTIAL rows are expected to become PASS:

- Program Catalog QA expected result: 20/20 PASS
- Full 9AS expected result: remains 53/53 PASS
- Focused 9AT expected result: remains 7/7 PASS
- Operator alignment expected result: remains 7/7 PASS
- Answer-cleanliness expected result: remains PASS

Production retest remains PENDING_BACKEND_DEPLOY.

## Safety Confirmation

- Real site modified: NO
- Assets uploaded or embedded: NO
- Frontend/Netlify changed: NO
- Contact flow executed: NO
- Real contact data sent: NO
- Lead/customer/task created: NO
- DB schema/migration/seed/import: NO
- Secret Manager/CORS/Bridge Hub changes: NO
- Public launch remains NO-GO

## Recommendation

Ready for review and owner-approved backend deployment after local checks pass.
