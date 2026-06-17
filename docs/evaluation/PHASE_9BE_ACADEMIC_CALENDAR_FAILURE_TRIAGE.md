# Phase 9BE Academic Calendar Failure Triage

PHASE_9BE_TRIAGE_STATUS=COMPLETE

Decision state: `BACKEND_CODE_ACADEMIC_CALENDAR_QA_FIXES_READY_PENDING_REVIEW`

Public launch: `NO-GO`

## Scope

9BD baseline: 30 total, 4 PASS, 3 PARTIAL, 23 FAIL. This triage documents the 26 non-PASS rows.

Root cause taxonomy used: `wrong_source_program_catalog`, `missing_calendar_priority`, `generic_answer_generation`, `clarification_missing`, `future_year_unsupported_failure`, `program_group_confusion`, `stale_expectation`.

## Triage Table

| Row | Question | Expected date/answer | Observed answer | Expected route/source | Observed route/source | Root cause | Proposed fix | Regression risk | Test to add |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 9bd-01 | საბაკალავრო პროგრამებისთვის შემოდგომის სემესტრი როდის იწყება? | 29 September 2025 | Program Catalog bachelor list | `academic_calendar_2025_2026` | `program_catalog_sources` | wrong_source_program_catalog; missing_calendar_priority | Calendar/date wording wins before Program Catalog; deterministic bachelor fall start | Program Catalog list routing | Bachelor fall start route/date test |
| 9bd-02 | საბაკალავრო პროგრამებისთვის გაზაფხულის სემესტრის დასკვნითი გამოცდები როდის არის? | 29 June - 11 July 2026 | One-cycle generic final dates | `academic_calendar_2025_2026` | `academic_calendar_2025_2026` | generic_answer_generation; program_group_confusion | Deterministic bachelor spring final mapping | Exam-rule routing | Bachelor spring finals exact test |
| 9bd-03 | საბაკალავრო პროგრამებისთვის გაზაფხულის აკადემიური რეგისტრაცია როდის არის? | 2 - 7 March 2026 | Program Catalog bachelor list | `academic_calendar_2025_2026` | `program_catalog_sources` | wrong_source_program_catalog; missing_calendar_priority | Calendar/date wording wins before Program Catalog; deterministic academic registration | Program Catalog bachelor list | Bachelor spring academic registration test |
| 9bd-06 | Computer Science-ის გაზაფხულის დასკვნითი გამოცდები როდის არის? | 13 - 25 July 2026 | CS spring semester start | `academic_calendar_2025_2026` | `academic_calendar_2025_2026` | generic_answer_generation; program_group_confusion | Add CS final exams event mapping before generic semester-start fallback | CS registration/start answers | CS spring finals exact test |
| 9bd-07 | სამაგისტრო პროგრამებისთვის გაზაფხულის სემესტრი როდის იწყება? | 9 March 2026 | Program Catalog master list | `academic_calendar_2025_2026` | `program_catalog_sources` | wrong_source_program_catalog; missing_calendar_priority | Calendar/date wording wins before Program Catalog; deterministic master start | Master catalog list | Master spring start route/date test |
| 9bd-08 | სამაგისტრო პროგრამებისთვის გაზაფხულის დასკვნითი გამოცდები როდის არის? | 29 June - 11 July 2026 | Master spring start 16 March | `academic_calendar_2025_2026` | `academic_calendar_2025_2026` | generic_answer_generation; program_group_confusion; stale_expectation | Correct master source row to 9 March start and finals map | 9AS academic rules answer stability | Master spring finals exact test |
| 9bd-09 | ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის დასკვნითი გამოცდები როდის არის? | 20 July - 1 August 2026 | 20-31 July 2026 | `academic_calendar_2025_2026` | `academic_calendar_2025_2026` | stale_expectation; generic_answer_generation | Use full file row ending 1 August | Existing generic one-cycle final text | One-cycle spring finals exact test |
| 9bd-10 | ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის დასკვნითი გამოცდების აღდგენა როდის არის? | 3 - 8 August 2026 | One-cycle final dates, no retake | `academic_calendar_2025_2026` | `academic_calendar_2025_2026` | generic_answer_generation; program_group_confusion | Add final-retake event mapping before final fallback | Retake rule routing | One-cycle spring final retake test |
| 9bd-11 | ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის შუალედური გამოცდები როდის არის? | 25 - 30 May 2026 | Bachelor/master fall midterms | `academic_calendar_2025_2026` | `academic_calendar_2025_2026` | generic_answer_generation; program_group_confusion | Add one-cycle spring midterm mapping | Exam assessment rule routing | One-cycle spring midterm exact test |
| 9bd-12 | ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის შუალედური გამოცდების აღდგენა როდის არის? | 13 - 18 July 2026 | Bachelor/master fall midterms | `academic_calendar_2025_2026` | `academic_calendar_2025_2026` | generic_answer_generation; program_group_confusion | Add one-cycle spring midterm retake mapping | Retake-rule answers | One-cycle spring midterm retake test |
| 9bd-13 | When does the fall semester start for Bachelor programs except Computer Science? | 29 September 2025 | AI unavailable / no source | `academic_calendar_2025_2026` | `program_catalog_sources` | wrong_source_program_catalog; missing_calendar_priority | English calendar/date wording wins before Program Catalog | Program Catalog English list | ENG bachelor fall start test |
| 9bd-14 | When are spring final exams for Bachelor programs except Computer Science? | 29 June - 11 July 2026 | CS spring start | `academic_calendar_2025_2026` | `academic_calendar_2025_2026` | program_group_confusion; generic_answer_generation | Treat "except Computer Science" as bachelor-except-CS, not CS | CS calendar answers | ENG bachelor spring finals test |
| 9bd-16 | When do spring final exams take place for Computer Science? | 13 - 25 July 2026 | CS spring start | `academic_calendar_2025_2026` | `academic_calendar_2025_2026` | generic_answer_generation; program_group_confusion | Add CS spring final mapping | CS start answer | ENG CS spring finals test |
| 9bd-17 | When does the spring semester start for Master programs? | 9 March 2026 | AI unavailable / no source | `academic_calendar_2025_2026` | `program_catalog_sources` | wrong_source_program_catalog; missing_calendar_priority | English calendar/date wording wins before Program Catalog | Master catalog list | ENG master spring start test |
| 9bd-18 | When are final exams for one-cycle programs in spring? | 20 July - 1 August 2026 | 20-31 July 2026 | `academic_calendar_2025_2026` | `academic_calendar_2025_2026` | stale_expectation; generic_answer_generation | Use exact ENG source row ending 1 August | One-cycle generic fallback | ENG one-cycle finals test |
| 9bd-19 | When does the fall semester start for first-year students of one-cycle English education programs? | 3 November 2025 | Bachelor-except-CS fall registration | `academic_calendar_2025_2026` | `academic_calendar_2025_2026` | program_group_confusion; generic_answer_generation | Add first-year one-cycle English group mapping | General one-cycle mapping | First-year one-cycle English fall start test |
| 9bd-20 | When are fall midterm exams for first-year one-cycle English programs? | 5 - 10 January 2026 | Bachelor/master fall midterms | `academic_calendar_2025_2026` | `academic_calendar_2025_2026` | program_group_confusion; generic_answer_generation | Add first-year one-cycle English midterm mapping | General midterm fallback | First-year one-cycle English midterm test |
| 9bd-21 | აკადემიური კალენდრის უქმე დღეები რომლებია? | Bank holiday list | Bachelor fall registration | `academic_calendar_2025_2026` | `academic_calendar_2025_2026` | generic_answer_generation; program_group_confusion | Add bank holiday deterministic list | None, holiday only | Bank holiday list test |
| 9bd-22 | ახალი წლის არდადეგები როდის არის? | 30 December 2025 - 4 January 2026 | Generic holiday row message | `academic_calendar_2025_2026` | `academic_calendar_2025_2026` | generic_answer_generation | Add New Year holiday exact mapping | Holiday fallback | New Year exact test |
| 9bd-23 | აღდგომის არდადეგები როდის არის? | 10 - 13 April 2026 | Generic holiday row message | `academic_calendar_2025_2026` | `academic_calendar_2025_2026` | generic_answer_generation | Add Easter exact mapping | Holiday fallback | Easter exact test |
| 9bd-24 | What are the New Year holidays? | 30 December 2025 - 4 January 2026 | Generic holiday row message | `academic_calendar_2025_2026` | `academic_calendar_2025_2026` | generic_answer_generation | Add English New Year exact mapping | Holiday fallback | ENG New Year exact test |
| 9bd-25 | What are the Easter holidays? | 10 - 13 April 2026 | Generic holiday row message | `academic_calendar_2025_2026` | `academic_calendar_2025_2026` | generic_answer_generation | Add English Easter exact mapping | Holiday fallback | ENG Easter exact test |
| 9bd-26 | გამოცდები როდის არის? | Ask program group, semester, and exam type | Default registration answer | clarification/no exact date | `academic_calendar_2025_2026` | clarification_missing | Add broad calendar clarification intercept | Helpful exact answers | Ambiguous exam clarification test |
| 9bd-27 | რეგისტრაცია როდის არის? | Ask program group and semester | Default registration answer | clarification/no exact date | `academic_calendar_2025_2026` | clarification_missing | Add broad calendar clarification intercept | Helpful exact answers | Ambiguous registration clarification test |
| 9bd-28 | სემესტრი როდის იწყება? | Ask program group and semester | Default registration answer | clarification/no exact date | `academic_calendar_2025_2026` | clarification_missing | Add broad calendar clarification intercept | Helpful exact answers | Ambiguous semester-start clarification test |
| 9bd-30 | 2027 წლის Computer Science-ის გამოცდები როდისაა? | Unsupported/no approved 2027 source | Reused 2025-2026 CS date | unsupported/no approved source | `academic_calendar_2025_2026` | future_year_unsupported_failure | Add future year guard for calendar questions outside 2025-2026 | 2031 unsupported already passing | 2027 future-year unsupported test |

## Fix Plan

- Add strong Academic Calendar priority routing before Program Catalog routing.
- Add deterministic exact-date answers for common 2025-2026 calendar questions.
- Add broad calendar clarification rules.
- Add a future year guard for calendar years outside 2025-2026.
- Preserve Program Catalog list/language/credit routing for non-calendar questions.

## Review Finding Follow-up

Medium review finding: calendar priority could over-capture non-calendar admissions questions when a question contained `registration` plus a program level.

Final review finding: English `date` was matched by substring, so non-date words such as `updated`, `candidate`, and `outdated` could incorrectly count as date/time markers.

Remaining review finding: a Computer Science spring registration shortcut bypassed the stricter predicate and routed requirements/documents questions to `academic_calendar_2025_2026`.

Final helper finding: the direct `chat_service.py` Computer Science spring helper still matched `date` inside non-date words such as `updated`, `candidate`, and `outdated`, which could trigger deterministic calendar replies outside the router path.

Final grounded fallback finding: `grounded_source_backed_reply()` could still return Academic Calendar dates for non-date admissions/requirements questions when called with `source_group=admissions_rules`, because broad `is_calendar_text()` treated bare `registration` and `semester` as calendar markers.

Final stale Bachelor registration finding: broad Bachelor registration prompts such as `When is bachelor registration?` fell through to an older calendar fallback and returned stale 8-13 September 2025 / 15-20 September 2025 registration dates.

Fix applied:

- `registration` alone is not a calendar marker.
- Calendar priority now requires explicit calendar context, or actual date/time wording with calendar-like event wording.
- Admissions, requirements, eligibility, documents, procedure, rules, policy, and `how to register` wording suppresses calendar priority unless a real date/time ask is present.
- English date/time markers now use regex word-boundary matching.
- Georgian marker behavior is preserved with substring/stem matching.
- Georgian equivalents for requirements, admissions/enrollment, documents, procedure, rules, policy, and registration requirements are included in the exclusion set.
- The Computer Science spring forced-source shortcut was removed from `claude_intent_router_service.py`.
- The parallel Computer Science spring scorer in `knowledge_routing_service.py` is gated by `is_academic_calendar_priority_question()`.
- The deterministic Computer Science spring registration helper in `chat_service.py` now requires date/time wording.
- The deterministic Computer Science spring registration helper now uses word-boundary matching for English date/time markers.
- `grounded_source_backed_reply()` now allows calendar answers directly for `academic_calendar_2025_2026`; otherwise it uses the same strict academic-calendar priority predicate. Broad `is_calendar_text()` is no longer sufficient to return calendar dates.
- `admissions_rules` is handled before any text-only calendar fallback, so registration requirements/documents questions remain admissions answers.
- Broad Bachelor registration prompts now have deterministic 2025-2026 handling before the old fallback can run.
- The old Bachelor registration fallback was replaced with the approved 9BE rows: fall administrative registration 15-20 September 2025, fall academic registration 22-27 September 2025, spring administrative registration 23-28 February 2026, and spring academic registration 2-7 March 2026.

Regression tests added:

- Negative: `What are updated registration requirements for bachelor admission?`
- Negative: `What are candidate registration requirements for bachelor admission?`
- Negative: `What are outdated registration requirements for bachelor admission?`
- Negative direct helper probe: `What are updated Computer Science spring semester registration requirements?`
- Negative direct helper probe: `What are candidate Computer Science spring semester registration requirements?`
- Negative direct helper probe: `What are outdated Computer Science spring semester registration requirements?`
- Negative grounded fallback probe with `admissions_rules`: `What documents are required for Computer Science spring registration?`
- Negative grounded fallback probe with `admissions_rules`: `What are updated Computer Science spring semester registration requirements?`
- Negative grounded fallback probe with `admissions_rules`: `What are the registration requirements for bachelor admission?`
- Stale-date regression: `When is bachelor registration?`
- Stale-date regression: `What date does bachelor registration start?`
- Stale-date regression: `ბაკალავრზე რეგისტრაცია როდის არის?`
- Stale-date regression: `When is Computer Science fall academic registration?`
- Negative: `What are the registration requirements for bachelor admission?`
- Negative: `What documents are required for bachelor registration?`
- Negative: `What are Computer Science spring registration requirements?`
- Negative: `What documents are required for Computer Science spring registration?`
- Negative: `Computer Science-ის გაზაფხულის რეგისტრაციის მოთხოვნები რა არის?`
- Negative: `Computer Science-ის გაზაფხულის რეგისტრაციისთვის რა საბუთებია საჭირო?`
- Negative: `ბაკალავრზე რეგისტრაციის მოთხოვნები რა არის?`
- Negative: `ბაკალავრზე რეგისტრაციისთვის რა საბუთებია საჭირო?`
- Positive: `When is bachelor registration?`
- Positive: `What date does bachelor registration start?`
- Positive: `What are the registration dates for Computer Science?`
- Positive: `When is Computer Science spring registration?`
- Positive: `What date is Computer Science spring registration?`
- Positive direct helper probe: `What date does Computer Science spring registration start?`
- Positive: `ბაკალავრზე რეგისტრაცია როდის არის?`
- Positive: `Computer Science-ის გაზაფხულის რეგისტრაცია როდის არის?`
- Positive: `Computer Science-ის გაზაფხულის სემესტრი როდის იწყება?`

Local result after review fix:

- 9BD calendar QA: 30 PASS / 0 PARTIAL / 0 FAIL
- Over-capture regression: 23 PASS / 0 FAIL
- Fallback over-capture regression: 7 PASS / 0 FAIL
- Stale-date regression: 4 PASS / 0 FAIL
- Public launch remains: NO-GO

## Safety

- Real site modified: NO
- Assets uploaded or embedded: NO
- Frontend/Netlify changed: NO
- DB schema/migration/seed/import changed or run: NO
- Secret Manager changed: NO
- CORS changed: NO
- Bridge Hub touched: NO
- Contact flow submitted: NO
- Lead/customer/task created: NO
- Public launch remains: NO-GO
