# Phase 9AT - Phase 9AS Failure Matrix

Matrix date: 2026-05-31

Source evidence:

- `docs/evaluation/PHASE_9AS_FULL_KNOWLEDGE_COVERAGE_QA_RESULT.md`
- `docs/evaluation/PHASE_9AS_OPERATOR_CRM_ALIGNMENT_QA_RESULT.md`
- `backend/app/data/evaluation/phase_9as_full_knowledge_qa.json`

Public launch: NO-GO

## Summary

Phase 9AS found 42 failed full-knowledge QA items and 1 failed Operator CRM alignment scenario.

Root cause groups:

- `calendar_mapping`: calendar prompts did not consistently route to `academic_calendar_2025_2026`.
- `admissions_mapping`: admissions prompts did not consistently route to `admissions_rules`.
- `source_missing`: configured source group is intentionally empty or expected source is not loaded.
- `unsupported_false_positive`: unsupported prompt matched unrelated approved snippets.
- `generic_ai_fallback`: retrieval found sources but visible answer remained generic AI fallback text.
- `handover_persistence`: bot offered an operator path but Operator CRM did not persist `human_handover=true`.
- `test_expectation_issue`: QA expected an answer even though approved source availability is uncertain.

## Failure Matrix

| QA item | Expected | Observed | Expected source | Observed route/source | Root cause | Required fix | Blocker |
| --- | --- | --- | --- | --- | --- | --- | --- |
| academic_medicine_ects_en | ANSWERABLE | generic AI fallback with sources | official_academic_rules | Medicine / MD, source-backed fallback text | generic_ai_fallback | grounded source-backed program-volume reply | Yes |
| academic_dentistry_ects_en | ANSWERABLE | generic AI fallback, Medicine route | official_academic_rules | Medicine / MD, calendar-like source titles | generic_ai_fallback | grounded Dentistry ECTS reply or mark unsupported if missing | Yes |
| academic_teaching_language_ka | ANSWERABLE | wrong source group | official_academic_rules | admissions_rules | admissions_mapping | route teaching-language to official academic rules | No |
| status_suspension_ka | ANSWERABLE | answer correct but strict must-not check matched source text | student_status_and_mobility | source-backed | test_expectation_issue | relax QA forbidden token for source citations | No |
| mobility_ka | ANSWERABLE | generic AI fallback | student_status_and_mobility | official source snippets | generic_ai_fallback | grounded mobility answer | Yes |
| internal_mobility_ka | ANSWERABLE | generic AI fallback | student_status_and_mobility | official source snippets | generic_ai_fallback | grounded internal mobility answer | Yes |
| credit_recognition_ka | ANSWERABLE | generic AI fallback | student_status_and_mobility | official source snippets | generic_ai_fallback | grounded credit-recognition answer | Yes |
| gpa_en | ANSWERABLE | generic AI fallback | exams_and_assessment | calendar/admin source titles | generic_ai_fallback | grounded GPA answer | Yes |
| fx_f_ka | ANSWERABLE | generic AI fallback | exams_and_assessment | unrelated source text | generic_ai_fallback | grounded FX/F answer | Yes |
| final_exam_admission_ka | ANSWERABLE | generic AI fallback | exams_and_assessment | official source snippets | generic_ai_fallback | grounded final-exam admission answer | Yes |
| retake_exam_ka | ANSWERABLE | generic AI fallback and handover | exams_and_assessment | not_required/no exact answer | generic_ai_fallback | grounded retake answer from rules/calendar | Yes |
| calendar_bachelor_fall_registration_ka | ANSWERABLE | Programs route, generic fallback | academic_calendar_2025_2026 | Programs | calendar_mapping | calendar route/source selection | Yes |
| calendar_bachelor_spring_registration_ka | ANSWERABLE | Programs route, generic fallback | academic_calendar_2025_2026 | Programs | calendar_mapping | calendar route/source selection | Yes |
| calendar_cs_spring_registration_ka | ANSWERABLE | route Admissions | academic_calendar_2025_2026 | Admissions | calendar_mapping | prioritize CS spring calendar route | Yes |
| calendar_cs_semester_start_ka | ANSWERABLE | General / Operator, generic fallback | academic_calendar_2025_2026 | General | calendar_mapping | add CS semester-start mapping and grounded answer | Yes |
| calendar_master_spring_start_en | ANSWERABLE | generic AI fallback | academic_calendar_2025_2026 | calendar source snippets | generic_ai_fallback | grounded master spring date answer | Yes |
| calendar_one_cycle_finals_ka | ANSWERABLE | official_academic_rules instead of calendar | academic_calendar_2025_2026 | official_academic_rules | calendar_mapping | final-exam calendar route/source selection | Yes |
| calendar_midterms_ka | ANSWERABLE | admissions_rules, generic fallback | academic_calendar_2025_2026 | admissions_rules | calendar_mapping | midterm calendar route/source selection | Yes |
| calendar_retakes_ka | ANSWERABLE | admissions_rules/general route | academic_calendar_2025_2026 | admissions_rules | calendar_mapping | retake calendar route/source selection | Yes |
| calendar_holidays_en | ANSWERABLE | generic AI fallback | academic_calendar_2025_2026 | calendar/admin source titles | generic_ai_fallback | grounded holiday fallback or unsupported if exact rows missing | No |
| admission_bachelor_documents_ka | ANSWERABLE | Programs route, generic fallback | admissions_rules | Programs | admissions_mapping | admissions document routing and grounded answer | Yes |
| admission_master_documents_ka | ANSWERABLE | General / Operator route | admissions_rules | General | admissions_mapping | master documents route/answer | Yes |
| admission_without_exams_ka | ANSWERABLE | generic AI fallback | admissions_rules | official source snippets | generic_ai_fallback | grounded admission-without-exams answer | Yes |
| foreign_education_recognition_en | ANSWERABLE | generic AI fallback/handover | admissions_rules | source-backed fallback text | generic_ai_fallback | grounded recognition answer or mark unsupported | Yes |
| foreign_applicant_en | ANSWERABLE | generic AI fallback/handover | admissions_rules | source-backed fallback text | generic_ai_fallback | grounded foreign-applicant answer or mark unsupported | Yes |
| english_program_requirements_en | ANSWERABLE | wrong source/route | international_admissions_sources | Programs/official_academic_rules | source_missing | mark unsupported unless approved international source exists | No |
| clarification_admissions_ka | CLARIFICATION_REQUIRED | generic fallback | none | handover/fallback | admissions_mapping | broad admissions clarification route | No |
| clarification_help_ka | CLARIFICATION_REQUIRED | answer did clarify but token expectation too narrow | none | clarification | test_expectation_issue | relax QA include token | No |
| routing_finance_operator_ka | ROUTE_ONLY | generic fallback text missing expected Finance wording | finance_sources | Finance | generic_ai_fallback | preserve finance operator wording | No |
| routing_library_ka | UNSUPPORTED_OPERATOR | correct no-source fallback but QA token too strict | library_sources | Library | test_expectation_issue | relax include token for Georgian fallback | No |
| routing_it_emis_ka | UNSUPPORTED_OPERATOR | IT route but Operator CRM handover false | it_support_sources | IT Support | handover_persistence | persist no-source IT handover metadata | Yes |
| routing_medicine_md_ka | ANSWERABLE | generic fallback | official_academic_rules | Medicine / MD | generic_ai_fallback | grounded Medicine / MD answer | Yes |
| routing_international_medicine_en | ROUTE_ONLY | routed Medicine, not international | international_admissions_sources | Medicine/admissions_rules | admissions_mapping | preserve international context in medicine route | No |
| routing_career_ka | UNSUPPORTED_OPERATOR | General/admissions source fallback | career_sources | General/admissions_rules | unsupported_false_positive | route career to empty-source career fallback | Yes |
| unsupported_tuition_price_ka | UNSUPPORTED_OPERATOR | matched unrelated approved source | finance_sources | admissions_rules/source-backed | unsupported_false_positive | strengthen fake/future tuition unsupported detection | Yes |
| unsupported_library_rules_en | UNSUPPORTED_OPERATOR | correct fallback but QA token too strict | library_sources | Library/no source | test_expectation_issue | relax English include phrase | No |
| unsupported_it_details_en | UNSUPPORTED_OPERATOR | Operator CRM handover false | it_support_sources | IT Support/no source | handover_persistence | persist no-source IT handover metadata | Yes |
| operator_explicit_ka | ROUTE_ONLY | generic fallback text | none | General | generic_ai_fallback | preserve operator handover wording | No |
| operator_wait_ka | ROUTE_ONLY | generic fallback text before wait action | none | General | generic_ai_fallback | test wait via handover endpoint, not chat prompt alone | No |
| operator_contact_form_open_ka | ROUTE_ONLY | chat prompt cannot verify UI form | none | General | test_expectation_issue | verify contact form in browser/visual QA only | No |
| operator_unsupported_handover_ka | UNSUPPORTED_OPERATOR | matched unrelated approved source | none | source-backed official snippets | unsupported_false_positive | strengthen unsupported/fake-program detection | Yes |
| operator_finance_handover_en | ROUTE_ONLY | General route, generic fallback | finance_sources | General | admissions_mapping | explicit finance operator route in EN | No |
| 9AS operator it_operator_fallback | Operator CRM handover true | `human_handover=false` | it_support_sources | IT Support | handover_persistence | set no-source IT fallback as human handover | Yes |

## Required Fix Set

Implemented locally in Phase 9AT:

- Calendar/admissions/IT/career keyword routing before generic scoring.
- Empty-source source groups return `no_approved_source_found` instead of matching unrelated snippets.
- Routed source groups trigger knowledge checks even when the AI intent is not one of the legacy knowledge intents.
- Source-backed answers with AI-service fallback get conservative grounded replies for official facts, calendar, admissions, and program-volume questions.
- No-approved-source fallback now persists handover metadata consistently, including IT/EMIS.
- Unsupported fake future/campus/tuition/library/password prompts are blocked from unrelated approved-source matches.

## Status

Local code is ready for verification. Production verification requires backend deploy approval because the live Cloud Run revision still runs the pre-9AT code.
