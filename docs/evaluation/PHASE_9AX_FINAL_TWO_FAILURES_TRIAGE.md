# Phase 9AX Final Two 9AS Failures Triage

Date: 2026-06-01

Public launch: NO-GO

## Scope

Phase 9AX targets only the two remaining full 9AS production failures after the Phase 9AW deploy. Focused 9AT QA and Operator alignment QA were already passing in production.

## Failure Table

| QA id | Question | Expected route/source group | Observed route/source group | Root cause | Exact fix | Regression risk | Tests added |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `admission_without_exams_ka` | `ეროვნული გამოცდების გარეშე ჩარიცხვა შესაძლებელია?` | Admissions / `admissions_rules` | `exams_and_assessment` | Georgian `გამოცდების` was treated as an exam-rule marker before recognizing the admissions phrase `ეროვნული გამოცდების გარეშე`. | Added admission-without-exams priority detection before exam specialization and forced source selection. | Could accidentally weaken real exam-rule routing. Preserved direct tests for final-exam admission rules and retake rules. | `test_admission_without_exams_ka_routes_to_admissions_not_exams`, variant tests, exam-rule preservation tests. |
| `english_program_requirements_en` | `What are the English-language program requirements if they are in the approved source?` | International Admissions / `international_admissions_sources` | Programs / `programs` | English-language requirement wording was treated as generic Programs unless international/applicant terms were present. | Added English-language program requirements priority detection for English-taught/program/proficiency/IELTS/TOEFL requirement prompts. | Could over-route generic program browsing to International Admissions. Preserved generic programs test. | `test_english_program_requirements_routes_to_international_not_programs`, IELTS/TOEFL variants, generic programs preservation test. |

## Safety Notes

- No approved-source expectation was weakened.
- No broad retrieval fallback was reintroduced.
- Informational answers still must not create handover pollution.
- Explicit operator/wait flows remain handover paths.
- No contact flow was executed.
- No lead/customer/task was created.
- Public launch remains NO-GO.
