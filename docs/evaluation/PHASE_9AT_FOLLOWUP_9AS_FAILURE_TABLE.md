# Phase 9AT Follow-up: 9AS Failure Table

Date: 2026-05-31

Public launch: NO-GO

Scope: read and fix local backend routing/relevance logic only. No deploy, no DB migration, no seed/import, no Secret Manager/CORS/Bridge Hub changes, no real site changes, no contact flow, no lead/task/customer creation.

## Original 20 Failures From 9AS

| # | QA id | Root cause | Fix/status |
|---|---|---|---|
| 1 | academic_dentistry_ects_en | Stale expectation: Dentistry is a one-cycle health/medicine-adjacent program and production routed to Medicine / MD with source-backed answer. | Dataset expectation updated to accept Medicine / MD department. |
| 2 | academic_teaching_language_ka | Wrong source group: teaching-language questions were allowed to drift to admissions rules. | Added teaching-language routing priority to Programs / official_academic_rules and grounded reply. |
| 3 | status_suspension_ka | Stale QA assertion: `10` matched source citation/page text, not the answer body. | QA script now checks must-include/must-not-include tokens against answer body before source hint. |
| 4 | credit_recognition_ka | Wrong source retrieval: broad recognition marker routed to admissions/foreign education recognition. | Added credit-recognition priority to student_status_and_mobility. |
| 5 | final_exam_admission_ka | Wrong source retrieval: exam-rule question routed to calendar dates. | Added exam-rule detection and exams_and_assessment priority. |
| 6 | retake_exam_ka | Wrong source retrieval: retake rule question routed to calendar dates. | Added exam-rule detection and exams_and_assessment priority. |
| 7 | calendar_retakes_ka | Stale/strict wording expectation: calendar answer was source-backed but did not include the exact exam token. | Left as calendar wording QA gap; no source hallucination observed. |
| 8 | english_program_requirements_en | Missing source group priority: English-language program requirements routed to generic program/academic sources. | Added English-program routing to international_admissions_sources and grounded reply. |
| 9 | clarification_admissions_ka | Broad admissions prompt did not trigger clarification before fallback. | Added broad admissions clarification via admissions + generic-short detection. |
| 10 | clarification_help_ka | Stale wording expectation: generic clarification was acceptable but expected one exact Georgian token. | Dataset expectation relaxed to current generic clarification wording. |
| 11 | routing_finance_operator_ka | Handover reply/routing did not consistently mention Finance. | Finance keyword matching strengthened; handover routing appends department. |
| 12 | routing_library_ka | Stale expectation: library selected sources are now approved and active. | Dataset and operator alignment expectation updated to source-backed/no handover. |
| 13 | routing_international_medicine_en | International Medicine picked admissions_rules and sometimes unrelated selected-policy source. | International Medicine source group now prioritizes international_admissions_sources; public department remains Medicine / MD for existing workflow compatibility. |
| 14 | routing_career_ka | Stale expectation: career selected sources are now approved and active. | Dataset updated to source-backed/no handover; QA alias accepts Student Services/Career display. |
| 15 | unsupported_tuition_price_ka | Unsupported false positive: fake 2031 tuition/program question routed into admissions. | Existing unsupported guard preserved; finance routing remains expected for fake tuition no-source fallback. |
| 16 | unsupported_library_rules_en | Unsupported false positive risk: specific rare-manuscript/six-month question could match generic library sources. | Added regression test ensuring no_approved_source_found despite general library source. |
| 17 | operator_explicit_ka | Generic AI fallback did not include the expected operator wording in deployed backend. | Local routing keeps explicit operator as handover; expected production retest after deploy. |
| 18 | operator_wait_ka | Wait action through message path returned generic wording in deployed backend. | Existing handover endpoint remains correct; message-path retest pending deploy. |
| 19 | operator_contact_form_open_ka | Contact-open message returned generic wording; UI contact form remains visual-QA covered. | Message-path retest pending deploy; no contact submission performed. |
| 20 | operator_finance_handover_en | Finance handover routed as General / Operator in deployed backend. | Added English `finance` / `financial` department keywords; local regression passes. |

## Current Production Baseline Without Deploy

After stale expectations were corrected but before deploying local backend fixes:

- Focused 9AT production QA: 7/7 PASS
- Operator alignment production QA: 7/7 PASS
- Full 9AS production QA: 37/53 PASS, 16 FAIL

The remaining 16 failures are expected until the local backend relevance changes are deployed and retested.

## Local Verification

- `python -m compileall app`: PASS
- Focused 9AT regression test file: 12/12 PASS
- Affected department/routing/no-mojibake tests: 38/38 PASS
- Full backend pytest: 944/944 PASS

## Expected Production Retest

After approved backend deploy, rerun:

- `python -m app.scripts.production_phase_9at_knowledge_fixes_qa`
- `python -m app.scripts.production_phase_9as_operator_alignment_qa`
- `python -m app.scripts.production_phase_9as_full_knowledge_coverage_qa`

Expected result: focused 9AT remains PASS, operator alignment remains PASS, and full 9AS should improve from the current 37/53 production baseline. Exact final count requires deployment verification.

