# Phase 9AS Full Knowledge Coverage QA Result

PHASE_9AS_FULL_KNOWLEDGE_QA_STATUS=FAILED

Test time UTC: 2026-05-31T16:59:45.867740+00:00
Backend URL: https://alte-ai-crm-backend-226875230147.europe-west1.run.app
Netlify Origin: https://nimble-croissant-2f66e8.netlify.app
Dataset: `backend\app\data\evaluation\phase_9as_full_knowledge_qa.json`
Operator API auth: AUTH_OK

## Summary

- Total questions: 53
- Passed: 37
- Failed: 16
- Skipped: 0
- Contact flow executed: NO
- Real contact data sent: NO
- Lead/task/customer created: NO
- Public launch: NO-GO

## Per-Category Results

| Category | Total | Passed | Failed |
| --- | ---: | ---: | ---: |
| academic_calendar | 9 | 8 | 1 |
| admissions | 6 | 5 | 1 |
| clarification | 6 | 5 | 1 |
| official_academic_facts | 17 | 12 | 5 |
| operator_handover | 5 | 1 | 4 |
| routing | 6 | 4 | 2 |
| unsupported | 4 | 2 | 2 |

## Failures

- `academic_teaching_language_ka` (official_academic_facts): source group=admissions_rules
- `status_suspension_ka` (official_academic_facts): must not include 10=სტუდენტის სტატუსის შეჩერების საერთო ვადა არ უნდა აღემატებოდეს 5 წელს.

წყარო: page 10; chunk 23, page 2; შინაარსი მუხლი 1. ზოგადი დებულებანი ...............................................................................
- `credit_recognition_ka` (official_academic_facts): must include კრედიტ=უცხოეთში მიღებული განათლების აღიარება ხორციელდება ოფიციალური მიღების წესებისა და საქართველოს კანონმდებლობით დადგენილი პროცედურის მიხედვით, ჩარიცხვის საბოლოო გაფორმებამდე.

წყარო: page 13; chunk 30, page 22; chunk 49.
- `final_exam_admission_ka` (official_academic_facts): source group=academic_calendar_2025_2026
- `retake_exam_ka` (official_academic_facts): source group=academic_calendar_2025_2026; must include გამოცდ=დამტკიცებული 2025-2026 კალენდარი გადაბარების პერიოდებს პროგრამის კატეგორიის მიხედვით უთითებს, მათ შორის ბაკალავრიატისა და მაგისტრატურისთვის 16-21 თებერვალი 2026, როცა ეს კატეგორია ვრცელდება.

წყარო: page 15; chunk 35, pa
- `calendar_retakes_ka` (academic_calendar): must include გამოცდ=დამტკიცებული 2025-2026 კალენდარი გადაბარების პერიოდებს პროგრამის კატეგორიის მიხედვით უთითებს, მათ შორის ბაკალავრიატისა და მაგისტრატურისთვის 16-21 თებერვალი 2026, როცა ეს კატეგორია ვრცელდება.

წყარო: page 3; მუხლი 1. ზოგა
- `english_program_requirements_en` (admissions): department route=programs / Programs; source group=official_academic_rules; must include English=The AI service is temporarily unavailable. I can connect you with the relevant department.
- `clarification_admissions_ka` (clarification): should_handover expected=True; clarification required=False; must include ბაკალავრი=ამ მომენტში AI სერვისთან კავშირი შეფერხებულია. ამ საკითხზე დაგაკავშირებთ შესაბამის დეპარტამენტთან.; operator human_handover expected=True
- `routing_finance_operator_ka` (routing): must include ფინანს=ამ მომენტში AI სერვისთან კავშირი შეფერხებულია. ამ საკითხზე დაგაკავშირებთ შესაბამის დეპარტამენტთან.
- `routing_international_medicine_en` (routing): source group=admissions_rules; should_handover expected=False; must include international=Foreign applicants are routed through the official foreign applicant admission procedure; exact document and recognition requirements must be checked in the approved admissions source.; operator human_handover expected=False
- `unsupported_tuition_price_ka` (unsupported): source group=admissions_rules
- `unsupported_library_rules_en` (unsupported): must include approved source=I couldn't find an exact answer in the approved official sources. I can connect you with the relevant operator so your question is routed to the correct department.
- `operator_explicit_ka` (operator_handover): must include ოპერატორ=ამ მომენტში AI სერვისთან კავშირი შეფერხებულია. ამ საკითხზე დაგაკავშირებთ შესაბამის დეპარტამენტთან.
- `operator_wait_ka` (operator_handover): must include ოპერატორ=ამ მომენტში AI სერვისთან კავშირი შეფერხებულია. ამ საკითხზე დაგაკავშირებთ შესაბამის დეპარტამენტთან.
- `operator_contact_form_open_ka` (operator_handover): must include კონტაქტ=ამ მომენტში AI სერვისთან კავშირი შეფერხებულია. ამ საკითხზე დაგაკავშირებთ შესაბამის დეპარტამენტთან.
- `operator_finance_handover_en` (operator_handover): department route=general / General / Operator; must include Finance=The AI service is temporarily unavailable. I can connect you with the relevant department.

## Checks Covered

- Source-backed correctness
- Expected source group
- Department/routing
- Clarification behavior
- Unsupported no-hallucination fallback
- Handover expectation
- Operator `human_handover` state when API auth is available
- No lead/task/customer creation
- No direct phone/email/name request in chat answer
- No Georgian mojibake

## Final Recommendation

Review failed cases before approval; keep public launch blocked.
