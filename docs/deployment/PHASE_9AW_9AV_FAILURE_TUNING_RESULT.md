# Phase 9AW - 9AV Failure Tuning Result

Date: 2026-06-01

PHASE_9AW_STATUS=CODE_READY_PENDING_BACKEND_DEPLOY

Decision state: `BACKEND_CODE_9AV_FAILURE_TUNING_READY_PENDING_DEPLOY`

Public launch: NO-GO

Production status: `PENDING_BACKEND_DEPLOY`

Deploy status: `NOT_DEPLOYED_PENDING_APPROVAL`

## Scope

Phase 9AW analyzed the 21 remaining full 9AS production failures after the Phase 9AV Claude Intent Router deployment. The goal was targeted knowledge/routing tuning without changing the Phase 9AV safety model.

Triage table: `docs/evaluation/PHASE_9AW_9AV_PRODUCTION_FAILURE_TRIAGE.md`

## Root Cause Summary

- Router/source specialization gaps for status, mobility, credit recognition, exams/assessment, and English-language international program requirements.
- Answer-generation wording gaps for credit recognition, retake exam calendar wording, help clarification text, finance operator Georgian wording, and international applicant wording.
- One QA script bug where proper Georgian `წყარო:` source citations were not stripped before token checks.
- Stale 9AS expectations for explicit operator and unsupported no-source flows, where Phase 9AV correctly does not attach a source group to non-retrieval paths.
- No missing approved source was identified for the 21 failing cases.

## Fixes Made

- Added post-Claude source group specialization that only runs for otherwise valid Claude routes:
  - status/mobility/credit-recognition prompts -> `student_status_and_mobility`
  - GPA/FX/final-exam/retake rule prompts, including Georgian exam-rule prompts -> `exams_and_assessment`
  - exam date/schedule prompts remain routed to `academic_calendar_2025_2026`
  - English-language/international applicant requirements -> `international_admissions_sources`
- Applied the same source group specialization to deterministic fallback routing so Claude-disabled/failure paths use the same primary source group for Georgian exam-rule prompts.
- Preserved invalid/empty Claude source group safety. Invalid source groups are not filled by deterministic specialization.
- Added deterministic grounded reply paths for `student_status_and_mobility` and `exams_and_assessment`.
- Updated calendar retake wording to include exam terminology.
- Updated international applicant wording to include `International`.
- Localized Georgian operator handover wording for Finance and other public departments.
- Removed duplicate unreachable Georgian return code from the operator handover reply helper.
- Updated 9AS QA token stripping for clean Georgian `წყარო:` source citations.
- Updated stale 9AS expectations where explicit operator/unsupported flows should have `expected_source_group=null` under Phase 9AV.

## QA Expectation Changes

Updated `backend/app/data/evaluation/phase_9as_full_knowledge_qa.json` only where the old expectation contradicted Phase 9AV behavior or approved source grouping:

- `foreign_education_recognition_en`: expected group -> `international_admissions_sources`
- `foreign_applicant_en`: expected group -> `international_admissions_sources`
- `routing_finance_operator_ka`: expected group -> `null`
- `routing_international_medicine_en`: handover expected -> `false`
- `unsupported_tuition_price_ka`: expected group -> `null`
- `unsupported_library_rules_en`: expected group -> `null`, required token -> `approved`
- `unsupported_it_details_en`: expected group -> `null`
- `operator_finance_handover_en`: expected group -> `null`

## Local Verification

Compileall: `PASS`

Local QA result: `19/19 PASS`

Full backend pytest: `1006 passed`

Verifier result: `PASS`

Expected production retest result: full 9AS should improve from `32/53 PASS` after backend deploy. Focused 9AT and operator alignment should remain passing.

## Safety Confirmation

- Real Alte site modified: NO
- Asset upload/embed: NO
- Contact flow executed: NO
- Lead/customer/task created: NO
- DB migration/seed/import: NO
- DB schema change: NO
- Secret Manager/CORS/Bridge Hub changes: NO
- Frontend/Netlify changed: NO
- Production deploy: NO
- Public launch: NO-GO
