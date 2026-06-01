# Phase 9AX - Final Two 9AS Failures Result

Date: 2026-06-01

PHASE_9AX_STATUS=CODE_READY_PENDING_BACKEND_DEPLOY

Decision state: `BACKEND_CODE_FINAL_9AS_FAILURES_FIXED_PENDING_DEPLOY`

Public launch: NO-GO

Deploy status: `NOT_DEPLOYED_PENDING_APPROVAL`

Production status: `PENDING_BACKEND_DEPLOY`

## Summary

Phase 9AX fixed the two remaining full 9AS production failures from Phase 9AW:

- `admission_without_exams_ka`
- `english_program_requirements_en`

Triage table: `docs/evaluation/PHASE_9AX_FINAL_TWO_FAILURES_TRIAGE.md`

## Root Causes

- `admission_without_exams_ka`: the Georgian word for exams in `ეროვნული გამოცდების გარეშე` was caught by exam-rule routing before the phrase was recognized as admissions without national exams.
- `english_program_requirements_en`: English-language requirement prompts were treated as generic Programs unless they also included international/applicant terms.

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
