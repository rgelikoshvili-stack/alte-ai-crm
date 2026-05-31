# Phase 9AS Full Knowledge Coverage QA Result

PHASE_9AS_FULL_KNOWLEDGE_QA_STATUS=FAILED

Test time UTC: 2026-05-31T20:29:09.240013+00:00
Backend URL: https://alte-ai-crm-backend-226875230147.europe-west1.run.app
Netlify Origin: https://nimble-croissant-2f66e8.netlify.app
Dataset: `backend\app\data\evaluation\phase_9as_full_knowledge_qa.json`
Operator API auth: AUTH_OK

## Summary

- Total questions: 53
- Passed: 32
- Failed: 21
- Skipped: 0
- Contact flow executed: NO
- Real contact data sent: NO
- Lead/task/customer created: NO
- Public launch: NO-GO

## Per-Category Results

| Category | Total | Passed | Failed |
| --- | ---: | ---: | ---: |
| academic_calendar | 9 | 8 | 1 |
| admissions | 6 | 3 | 3 |
| clarification | 6 | 5 | 1 |
| official_academic_facts | 17 | 7 | 10 |
| operator_handover | 5 | 4 | 1 |
| routing | 6 | 4 | 2 |
| unsupported | 4 | 1 | 3 |

## Failures

- `status_suspension_ka` (official_academic_facts): source group=official_academic_rules; must not include 10=სტუდენტის სტატუსის შეჩერების საერთო ვადა არ უნდა აღემატებოდეს 5 წელს.

წყარო: page 10; chunk 23, page 2; შინაარსი მუხლი 1. ზოგადი დებულებანი ...............................................................................
- `status_restoration_ka` (official_academic_facts): source group=official_academic_rules
- `status_termination_ka` (official_academic_facts): source group=official_academic_rules
- `mobility_ka` (official_academic_facts): source group=official_academic_rules
- `internal_mobility_ka` (official_academic_facts): source group=official_academic_rules
- `credit_recognition_ka` (official_academic_facts): source group=official_academic_rules; must include კრედიტ=უცხოეთში მიღებული განათლების აღიარება ხორციელდება ოფიციალური მიღების წესებისა და საქართველოს კანონმდებლობით დადგენილი პროცედურის მიხედვით, ჩარიცხვის საბოლოო გაფორმებამდე.

წყარო: page 13; chunk 30, page 22; chunk 49.
- `gpa_en` (official_academic_facts): source group=official_academic_rules
- `fx_f_ka` (official_academic_facts): source group=official_academic_rules
- `final_exam_admission_ka` (official_academic_facts): source group=official_academic_rules
- `retake_exam_ka` (official_academic_facts): source group=official_academic_rules
- `calendar_retakes_ka` (academic_calendar): must include გამოცდ=დამტკიცებული 2025-2026 კალენდარი გადაბარების პერიოდებს პროგრამის კატეგორიის მიხედვით უთითებს, მათ შორის ბაკალავრიატისა და მაგისტრატურისთვის 16-21 თებერვალი 2026, როცა ეს კატეგორია ვრცელდება.

წყარო: page 3; მუხლი 1. ზოგა
- `foreign_education_recognition_en` (admissions): source group=international_admissions_sources
- `foreign_applicant_en` (admissions): source group=international_admissions_sources
- `english_program_requirements_en` (admissions): department route=programs / Programs; source group=official_academic_rules
- `clarification_help_ka` (clarification): must include რომ=გთხოვთ დააზუსტოთ, რა სახის დახმარება გჭირდებათ: მიღება, პროგრამები, ფინანსები, IT დახმარება თუ ოპერატორთან დაკავშირება?

- მიღება
- პროგრამები
- ფინანსები
- IT დახმარება
- `routing_finance_operator_ka` (routing): source group=None; must include ფინანს=შემიძლია ეს მოთხოვნა გადავცე შესაბამის გუნდს: Finance. შეგიძლიათ დაელოდოთ ოპერატორს ამ ჩატში ან სურვილის შემთხვევაში დატოვოთ კონტაქტი.
- `routing_international_medicine_en` (routing): should_handover expected=False; must include international=Foreign applicants are routed through the official foreign applicant admission procedure; exact document and recognition requirements must be checked in the approved admissions source.; operator human_handover expected=False
- `unsupported_tuition_price_ka` (unsupported): source group=None
- `unsupported_library_rules_en` (unsupported): source group=None; must include approved source=I couldn't find an exact answer in the approved official sources. I can connect you with the relevant operator so your question is routed to the correct department. I can route this to Library so the correct advisor can 
- `unsupported_it_details_en` (unsupported): source group=None
- `operator_finance_handover_en` (operator_handover): source group=None

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
