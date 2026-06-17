# Phase 9AX - Final Two 9AS Failures Result

Date: 2026-06-01

PHASE_9AX_STATUS=DEPLOYED_PRODUCTION_QA_PASSED

Decision state: `BACKEND_DEPLOYED_FULL_KNOWLEDGE_QA_PASSED_PENDING_APPROVALS`

Public launch: NO-GO

Deploy status: `DEPLOYED`

Production status: `VERIFIED`

## Summary

Phase 9AX fixed the two remaining full 9AS production failures from Phase 9AW:

- `admission_without_exams_ka`
- `english_program_requirements_en`

Triage table: `docs/evaluation/PHASE_9AX_FINAL_TWO_FAILURES_TRIAGE.md`

## Pre-Deploy Audit State

Before deployment approval and production verification, this phase was recorded as:

- `PHASE_9AX_STATUS=CODE_READY_PENDING_BACKEND_DEPLOY`
- Decision state: `BACKEND_CODE_FINAL_9AS_FAILURES_FIXED_PENDING_DEPLOY`
- Deploy status: `NOT_DEPLOYED_PENDING_APPROVAL`
- Production retest: `PENDING_BACKEND_DEPLOY`

## Root Causes

- `admission_without_exams_ka`: the Georgian word for exams in `ეროვნული გამოცდების გარეშე` was caught by exam-rule routing before the phrase was recognized as admissions without national exams.
- `english_program_requirements_en`: English-language requirement prompts were treated as generic Programs unless they also included international/applicant terms. The first 9AX production deploy fixed source selection but still left final department routing as Programs, so the final department resolver also needed the same targeted rule.

## Fixes Made

- Added priority detection for admission-without-exams phrases:
  - `გამოცდების გარეშე`
  - `ეროვნული გამოცდების გარეშე`
  - `ჩაბარება გამოცდების გარეშე`
  - `მიღება გამოცდების გარეშე`
  - `ჩარიცხვა გამოცდების გარეშე`
  - `admission without exams`
  - `without national exams`
  - `apply without exams`
- Routed these prompts to `admissions_rules` / Admissions before exam-rule specialization.
- Added priority detection for English-language program requirement prompts:
  - English-language program requirements
  - English-taught program admission
  - English proficiency proof
  - IELTS / TOEFL
  - international/foreign applicant English requirements
- Routed these prompts to `international_admissions_sources` / International Admissions.
- Added the same targeted English-language requirements rule to the final department resolver so the production response department is International Admissions, not Programs.
- Preserved exam-rule routing to `exams_and_assessment`.
- Preserved exam date/schedule routing to `academic_calendar_2025_2026`.
- Preserved generic Programs routing/clarification for generic program questions.

## Local Verification

Local QA script: `backend/app/scripts/local_phase_9ax_final_two_9as_failures_qa.py`

Tests: `backend/app/tests/test_phase_9ax_final_two_9as_failures.py`

Expected production result after backend deploy:

- Focused 9AT QA remains `7/7 PASS`.
- Operator alignment QA remains `7/7 PASS`.
- Full 9AS should improve from `51/53 PASS` to `53/53 PASS` if production behavior matches local routing.

## Production Deploy

- Code commit: `5638944` (`phase 9ax: fix final full knowledge routing failures`)
- Follow-up routing commit: `4d1942c` (`phase 9ax: fix final department routing failure`)
- Branch pushed: `origin/phase-9s-agent-preview-cors-note`
- First image tag: `v0.9-phase-9ax-final-knowledge-routing-fix`
- Final image tag: `v0.9-phase-9ax-final-knowledge-routing-fix2`
- Final Cloud Run revision: `alte-ai-crm-backend-00045-dg2`
- Traffic split: `alte-ai-crm-backend-00045-dg2=100%`

The deploy changed the backend container image only. No DB schema change, migration, seed, DB import, Secret Manager change, CORS change, Bridge Hub change, frontend/Netlify change, real-site upload, or real-site embed was performed.

## Production Verification

Focused Phase 9AT production QA:

- Status: `PASSED`
- Result: `7/7 PASS`

Full Phase 9AS production QA:

- Status: `PASSED`
- Result: `53/53 PASS`
- Official academic facts: `17/17 PASS`
- Academic calendar: `9/9 PASS`
- Admissions: `6/6 PASS`
- Clarification: `6/6 PASS`
- Routing: `6/6 PASS`
- Unsupported: `4/4 PASS`
- Operator handover: `5/5 PASS`

Operator alignment production QA:

- Status: `PASSED`
- Result: `7/7 PASS`
- Operator API auth: `AUTH_OK`

Remaining failures/gaps: NONE in the Phase 9AS production QA suite.

## Production Decision

`PHASE_9AX_DEPLOY_STATUS=PASSED_PENDING_APPROVALS`

Decision state: `BACKEND_DEPLOYED_FULL_KNOWLEDGE_QA_PASSED_PENDING_APPROVALS`

Public launch remains `NO-GO`.

## Safety Confirmation

- Real Alte site modified: NO
- Asset upload/embed: NO
- Frontend/Netlify changed: NO
- Contact flow executed: NO
- Lead/customer/task created: NO
- DB migration/seed/import: NO
- DB schema change: NO
- Secret Manager/CORS/Bridge Hub changes: NO
- Public launch: NO-GO
