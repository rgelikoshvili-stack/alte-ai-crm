# Phase 9AW - 9AV Production Failure Triage

Date: 2026-06-01

Decision state before tuning: `BACKEND_DEPLOYED_CLAUDE_INTENT_ROUTER_QA_FAILED_PENDING_FIXES`

Production baseline reviewed: full 9AS knowledge QA after 9AV deploy, `32/53 PASS`, `21 FAIL`.

This table documents the 21 failing 9AS cases. Failures are not hidden by weakening safety checks. Expectations are changed only where the production behavior is correct under the Phase 9AV source-grounded policy or where the approved source evidence shows the old expected source group was stale.

| QA id | Question summary | Expected/observed issue | Claude/router/retrieval finding | Root cause | Fix / classification | Blocker |
|---|---|---|---|---|---|---|
| `status_suspension_ka` | Student status suspension duration | Answer contained 5 years but failed source group and `must_not_include=10` | Router used broad `official_academic_rules`; source citation text added page 10 token | `router_selection_bug`, `qa_script_expectation_bug` | Specialize status prompts to `student_status_and_mobility`; strip clean Georgian source marker before token checks | Yes, fixed locally |
| `status_restoration_ka` | Student status restoration | Source-backed answer but wrong source group | Router kept `official_academic_rules` | `router_selection_bug` | Specialize status/restoration prompts to `student_status_and_mobility` | Yes, fixed locally |
| `status_termination_ka` | Student status termination | Source-backed answer but wrong source group | Router kept `official_academic_rules` | `router_selection_bug` | Specialize termination prompts to `student_status_and_mobility` | Yes, fixed locally |
| `mobility_ka` | Mobility | Source-backed answer but wrong source group | Router kept `official_academic_rules` | `router_selection_bug` | Specialize mobility prompts to `student_status_and_mobility` | Yes, fixed locally |
| `internal_mobility_ka` | Internal mobility | Source-backed answer but wrong source group | Router kept `official_academic_rules` | `router_selection_bug` | Specialize internal mobility prompts to `student_status_and_mobility` | Yes, fixed locally |
| `credit_recognition_ka` | Credit recognition | Source-backed but answer was foreign-education recognition style and missed credit token | Admissions-like recognition wording beat study-process topic | `router_selection_bug`, `answer_generation_issue` | Specialize credit-recognition prompts to `student_status_and_mobility`; add student-status grounded reply path | Yes, fixed locally |
| `gpa_en` | GPA | Source-backed answer but wrong source group | Router kept `official_academic_rules` | `router_selection_bug` | Specialize GPA prompts to `exams_and_assessment` | Yes, fixed locally |
| `fx_f_ka` | FX/F grading | Source-backed answer but wrong source group | Router kept `official_academic_rules` | `router_selection_bug` | Specialize FX/F prompts to `exams_and_assessment` | Yes, fixed locally |
| `final_exam_admission_ka` | Final exam admission | Source-backed answer but wrong source group | Router kept `official_academic_rules` | `router_selection_bug` | Specialize final-exam admission prompts to `exams_and_assessment` | Yes, fixed locally |
| `retake_exam_ka` | Retake/make-up exam rules | Source-backed answer but wrong source group | Router kept `official_academic_rules` | `router_selection_bug` | Specialize retake/make-up prompts to `exams_and_assessment` | Yes, fixed locally |
| `calendar_retakes_ka` | Calendar retake dates | Correct calendar group but answer did not include expected Georgian exam token | Calendar deterministic answer used "retake periods" wording | `answer_generation_issue` | Include exam/`გამოცდ` wording in retake calendar reply | Yes, fixed locally |
| `foreign_education_recognition_en` | Foreign education recognition | Answer was source-backed from international source but dataset expected admissions source | `international_admissions_sources` is the correct 9AV source group for foreign education recognition | `stale_test_expectation` | Update expected source group to `international_admissions_sources` | No, expectation fixed |
| `foreign_applicant_en` | Foreign applicant route | Answer was source-backed from international source but dataset expected admissions source | `international_admissions_sources` is the correct 9AV source group for foreign applicants | `stale_test_expectation` | Update expected source group to `international_admissions_sources` | No, expectation fixed |
| `english_program_requirements_en` | English-language program requirements | Routed to official academic rules/programs instead of international admissions | Claude selected broad rules for language/program wording | `router_selection_bug` | Specialize English-language international program requirements to `international_admissions_sources` | Yes, fixed locally |
| `clarification_help_ka` | "დახმარება მინდა" | Clarification worked but expected token `რომ` missing | Broad-question response was valid but wording missed expected token | `answer_generation_issue` | Update help clarification wording to include `ზუსტად რომ გიპასუხოთ` | No, fixed locally |
| `routing_finance_operator_ka` | Finance department handover | Handover worked but expected source group `finance_sources`; Georgian answer lacked `ფინანს` token | Explicit operator requests intentionally do not retrieve source groups under 9AV | `stale_test_expectation`, `answer_generation_issue` | Set expected source group to null; localize Finance label in Georgian operator reply | No, expectation/wording fixed |
| `routing_international_medicine_en` | International student applying to Medicine | Source-backed answer, Medicine department, but dataset expected handover=true | Source-backed informational routing should not create handover pollution under 9AV | `stale_test_expectation`, `answer_generation_issue` | Set handover expectations false; include "International" wording in foreign applicant reply | No, expectation/wording fixed |
| `unsupported_tuition_price_ka` | Unsupported fake tuition price | Correct no-approved-source fallback but dataset expected `finance_sources` | Unsupported no-source path intentionally has no source group | `stale_test_expectation` | Set expected source group to null | No, expectation fixed |
| `unsupported_library_rules_en` | Rare manuscript library rule | Correct no-approved-source fallback but dataset expected `library_sources` and exact "approved source" phrase | Unsupported no-source path intentionally has no source group; wording says "approved official sources" | `stale_test_expectation` | Set expected source group to null and require broader `approved` token | No, expectation fixed |
| `unsupported_it_details_en` | EMIS password reset details | Correct no-approved-source fallback but dataset expected `it_support_sources` | Unsupported no-source path intentionally has no source group | `stale_test_expectation` | Set expected source group to null | No, expectation fixed |
| `operator_finance_handover_en` | Finance operator handover | Handover worked but dataset expected `finance_sources` | Explicit operator path should not retrieve source groups | `stale_test_expectation` | Set expected source group to null | No, expectation fixed |

## Root Cause Summary

- Router/source specialization gaps: `11`
- Answer wording/generation issues: `5`
- QA script expectation bug: `1`
- Stale test expectations under 9AV policy: `8`
- Missing approved source: `0`
- Unsupported false positive requiring new retrieval broadening: `0`

## Safety Notes

- No broad retrieval was reintroduced.
- Invalid Claude source groups still do not get filled by deterministic specialization.
- Georgian exam-rule prompts such as final-exam admission and retake rules now specialize to `exams_and_assessment` in both validated Claude routes and deterministic fallback routes, while exam date/schedule prompts remain calendar-routed.
- Explicit operator/contact and broad-question deterministic overrides remain unchanged.
- Informational source-backed answers remain outside the handover lane.
- Production retest is `PENDING_BACKEND_DEPLOY`.
