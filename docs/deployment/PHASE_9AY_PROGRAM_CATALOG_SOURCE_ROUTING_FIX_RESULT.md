# Phase 9AY Program Catalog Source Routing Fix Result

Date: 2026-06-01

PHASE_9AY_STATUS=CODE_READY_PENDING_BACKEND_DEPLOY

Decision state: `BACKEND_CODE_PROGRAM_CATALOG_SOURCE_ROUTING_READY_PENDING_DEPLOY`

Public launch: NO-GO

Deploy status: `NOT_DEPLOYED_PENDING_APPROVAL`

Production retest status: `PENDING_BACKEND_DEPLOY`

## Problem Summary

Manual and scripted production QA showed that Program Catalog questions were answered from `official_academic_rules` sources instead of the intended source:

- `01_program_catalog.pdf`
- Higher Education Program Catalog

Example finding:

- Question: `რამდენი საგანმანათლებლო პროგრამა აქვს ალტე უნივერსიტეტს სულ?`
- Observed source group: `official_academic_rules`
- Observed source keys: `official_academic_rules_full_*`
- Expected source group: `program_catalog_sources`

## Root Cause

The Programs department configuration still referenced an obsolete/nonexistent catalog group name, `approved_program_catalog_sources`, and no valid strict source group existed for the uploaded Program Catalog. As a result, Claude/deterministic routing could select `official_academic_rules` for program-list and catalog-detail questions.

Review follow-up: the first local matcher also treated bare Georgian `კატალოგ` as Program Catalog. That could misroute Library catalog questions such as `ბიბლიოთეკის კატალოგი როგორ გამოვიყენო?` to `program_catalog_sources`.

## Fixes Made

- Added strict source group: `program_catalog_sources`.
- Scoped that group to `official_alte_pdf_kb` and the Program Catalog identities:
  - `01_program_catalog.pdf`
  - `Higher Education Program Catalog`
  - `official_alte_8_pdf_kb_01_01_program_catalog`
  - `program_catalog`
- Updated source group descriptions so Claude can distinguish Program Catalog facts from academic rules.
- Updated Programs department source mapping to prefer `program_catalog_sources` before `official_academic_rules`.
- Added deterministic routing markers for:
  - `პროგრამების კატალოგი`
  - `საგანმანათლებლო პროგრამა`
  - `რამდენი პროგრამა`
  - `საბაკალავრო პროგრამები`
  - `სამაგისტრო პროგრამები`
  - `ერთსაფეხურიანი პროგრამები`
  - `სამართლის საბაკალავრო`
  - `სამართლის სამაგისტრო`
  - `კომპიუტერული მეცნიერების პროგრამა`
  - `program catalog`
  - `Higher Education Program Catalog`
  - `bachelor programs`
  - `master programs`
  - `one-cycle programs`
  - `qualification`
- Preserved official academic rules routing for ECTS/rules/status questions.
- Removed bare `კატალოგ` as a sufficient Program Catalog marker.
- Added a Library-context guard so `ბიბლიოთეკის კატალოგი`, `library catalog`, books, databases, and electronic-resource questions remain on `library_sources`.

## Regression Protection

Added tests in `backend/app/tests/test_phase_9ay_program_catalog_source_routing.py` covering:

- All 10 Program Catalog QA questions route to `program_catalog_sources`.
- `official_academic_rules` is not primary for catalog questions.
- Strict source membership accepts `official_alte_8_pdf_kb_01_01_program_catalog*`.
- Strict source membership rejects `official_academic_rules_full_*`.
- Bachelor ECTS remains `official_academic_rules`.
- Admission without exams remains `admissions_rules`.
- English program requirements remain `international_admissions_sources`.
- Georgian exam-rule prompts remain `exams_and_assessment`.
- Exam date prompt remains `academic_calendar_2025_2026`.
- Informational catalog routes do not request handover.
- Library catalog questions route to `library_sources`, not `program_catalog_sources`.
- Public launch remains NO-GO.

## Local Verification

- Compileall: PASS
- Focused Phase 9AY route tests: PASS
- Full backend pytest: `1024 passed`
- Phase 9AY verifier: PASS
- Production QA against current backend: `0/10 PASS`, expected pre-deploy failure because current production is still revision `alte-ai-crm-backend-00045-dg2`.

Current production baseline:

- QA script: `backend/app/scripts/production_phase_9ay_program_catalog_source_qa.py`
- Result doc: `docs/evaluation/PHASE_9AY_PROGRAM_CATALOG_SOURCE_QA_RESULT.md`
- Status: `FAILED_PENDING_FIXES`
- Observed: Program Catalog questions still use `official_academic_rules` / `official_academic_rules_full_*`.
- Expected after deploy: Program Catalog questions use `program_catalog_sources` / `official_alte_8_pdf_kb_01_01_program_catalog*`.

## Expected Production Result After Deploy

After approved backend deploy, Program Catalog questions should:

- Use `program_catalog_sources`.
- Expose source metadata referencing `program_catalog_sources`, `01_program_catalog.pdf`, `Higher Education Program Catalog`, or `official_alte_8_pdf_kb_01_01_program_catalog`.
- Avoid `official_academic_rules` as the primary source group for catalog questions.
- Keep informational answers out of the handover lane.
- Avoid inventing tuition amounts if the catalog does not contain exact tuition information.

Expected Phase 9AY production QA status after deploy: PASS or PASS_WITH_SOURCE_METADATA_NOTES.

## Safety Confirmation

- Real site modified: NO
- Asset upload/embed: NO
- Frontend/Netlify changed: NO
- Contact flow executed: NO
- Lead/customer/task created: NO
- DB migration/seed/import: NO
- DB schema change: NO
- Secret Manager/CORS/Bridge Hub changes: NO
- Public launch: NO-GO

## Review Fix 2: Program List Prompt Disambiguation

Final local review found that bare Georgian `ჩამომითვალე` was still too broad as a Program Catalog marker. This could route non-program list prompts to `program_catalog_sources`.

Fix applied:

- Bare `ჩამომითვალე` is no longer sufficient for Program Catalog routing.
- Georgian list prompts now require program context such as `პროგრამ`, `საბაკალავრო`, `სამაგისტრო`, `ერთსაფეხურიანი`, `კვალიფიკაცია`, Law program, or Computer Science program wording.
- Admissions, finance, Library, and IT list prompts are guarded so they do not route to `program_catalog_sources`.

Regression coverage added:

- `ჩამომითვალე მიღებისთვის საჭირო საბუთები` stays out of Program Catalog and routes to Admissions.
- `ჩამომითვალე გრანტები` stays out of Program Catalog and routes to Finance.
- `ჩამომითვალე ბიბლიოთეკის რესურსები` stays out of Program Catalog and routes to Library.
- `ჩამომითვალე IT დახმარების გზები` stays out of Program Catalog and routes to IT Support.
- Bachelor, master, and one-cycle program list prompts still route to `program_catalog_sources`.

Production retest status remains `PENDING_BACKEND_DEPLOY`.

Public launch remains `NO-GO`.
