# Phase 9BD Academic Calendar GEO/ENG File QA Result

PHASE_9BD_ACADEMIC_CALENDAR_FILE_QA_STATUS=COMPLETED_WITH_FINDINGS

Decision state: `BACKEND_DEPLOYED_FILE_QA_FRAMEWORK_AND_PROGRAM_CATALOG_VERIFIED_PENDING_APPROVALS`

Public launch: `NO-GO`

## Summary

- Total tests: 30
- PASS count: 4
- PARTIAL count: 3
- FAIL count: 23
- Live backend/chatbot execution: COMPLETED
- Production backend: `alte-ai-crm-backend-00052-mjq`
- Image tag: `v0.9-phase-9bb-9bc-file-qa-framework`
- Tested source group: `academic_calendar_2025_2026`
- Public launch remains: NO-GO

## Failure Summary

- Wrong primary route/source: several GEO/ENG calendar questions routed to `program_catalog_sources`.
- Incomplete grounded calendar answer: several responses used generic calendar fallback text without exact dates.
- Wrong program group/date: several responses returned Computer Science or one-cycle dates for bachelor/master/general questions.
- Clarification missing: ambiguous exam/registration/semester questions returned a concrete default registration answer instead of asking which program/semester/exam type.
- Unsupported-year guard gap: the 2027 Computer Science question returned a 2025-2026 Computer Science date instead of refusing unsupported 2027 coverage.

## Safety Checks

- Real site modified: NO
- Assets uploaded or embedded: NO
- Frontend/Netlify changed: NO
- DB schema/migration/seed/import changed or run: NO
- Secret Manager changed: NO
- CORS changed: NO
- Bridge Hub touched: NO
- Contact flow submitted: NO
- Real contact data sent: NO
- Lead/customer/task created: NO
- Public launch remains: NO-GO

## Results

File: აკადემიური კალენდარი GEO
Category: Bachelor programs except Computer Science; fall semester start
Question: საბაკალავრო პროგრამებისთვის შემოდგომის სემესტრი როდის იწყება?
Expected answer: 29 September 2025.
Expected source: `academic_calendar_geo_2025_2026.pdf`, page 1
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: Program Catalog list; Computer Science dates; raw chunk/page/source noise; contact request
Live chatbot answer: "პროგრამების კატალოგის მიხედვით, ალტე უნივერსიტეტის 10 საბაკალავრო პროგრამაა: ..."
Observed source/route: `program_catalog_sources`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Wrong source and no semester start date.

File: აკადემიური კალენდარი GEO
Category: Bachelor programs except Computer Science; spring final exams
Question: საბაკალავრო პროგრამებისთვის გაზაფხულის სემესტრის დასკვნითი გამოცდები როდის არის?
Expected answer: 29 June - 11 July 2026.
Expected source: `academic_calendar_geo_2025_2026.pdf`, page 1
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: fall finals only; one-cycle dates; raw chunk/page/source noise
Live chatbot answer: "დამტკიცებული 2025-2026 კალენდარი დასკვნით გამოცდებს პროგრამის კატეგორიის მიხედვით უთითებს; ერთსაფეხურიანი პროგრამებისთვის მითითებულია 9-21 თებერვალი 2026 და 20-31 ივლისი 2026."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Routed to calendar but returned one-cycle generic dates, not bachelor spring finals.

File: აკადემიური კალენდარი GEO
Category: Bachelor programs except Computer Science; spring registration
Question: საბაკალავრო პროგრამებისთვის გაზაფხულის აკადემიური რეგისტრაცია როდის არის?
Expected answer: Academic registration is 2 - 7 March 2026.
Expected source: `academic_calendar_geo_2025_2026.pdf`, page 1
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: Program Catalog list; Computer Science dates
Live chatbot answer: "პროგრამების კატალოგის მიხედვით, ალტე უნივერსიტეტის 10 საბაკალავრო პროგრამაა: ..."
Observed source/route: `program_catalog_sources`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Wrong source and no registration date.

File: აკადემიური კალენდარი GEO
Category: Computer Science GEO/ENG; spring registration
Question: Computer Science-ის გაზაფხულის სემესტრის რეგისტრაცია როდის არის?
Expected answer: Academic/administrative registration is 9 - 14 March 2026.
Expected source: `academic_calendar_geo_2025_2026.pdf`, page 2
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: bachelor-except-CS registration dates
Live chatbot answer: "კომპიუტერული მეცნიერების პროგრამებისთვის გაზაფხულის სემესტრის აკადემიური/ადმინისტრაციული რეგისტრაცია არის 9-14 მარტს. გაზაფხულის სემესტრის დაწყება მითითებულია 30 მარტს."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: PASS
Notes: Correct date range and program group; year not stated but answer is grounded in 2025-2026 source context.

File: აკადემიური კალენდარი GEO
Category: Computer Science GEO/ENG; spring semester start
Question: Computer Science-ის გაზაფხულის სემესტრი როდის იწყება?
Expected answer: 30 March 2026.
Expected source: `academic_calendar_geo_2025_2026.pdf`, page 2
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: 16 March or 9 March as CS answer
Live chatbot answer: "კომპიუტერული მეცნიერების გაზაფხულის სემესტრის დაწყება მითითებულია 30 მარტს."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: PASS
Notes: Correct date and program group; year not stated but answer is grounded in 2025-2026 source context.

File: აკადემიური კალენდარი GEO
Category: Computer Science GEO/ENG; spring final exams
Question: Computer Science-ის გაზაფხულის დასკვნითი გამოცდები როდის არის?
Expected answer: 13 - 25 July 2026.
Expected source: `academic_calendar_geo_2025_2026.pdf`, page 2
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: semester start instead of final exams
Live chatbot answer: "კომპიუტერული მეცნიერების გაზაფხულის სემესტრის დაწყება მითითებულია 30 მარტს."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Correct route but answered semester start, not final exams.

File: აკადემიური კალენდარი GEO
Category: Master programs; spring semester start
Question: სამაგისტრო პროგრამებისთვის გაზაფხულის სემესტრი როდის იწყება?
Expected answer: 9 March 2026.
Expected source: `academic_calendar_geo_2025_2026.pdf`, page 3
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: Program Catalog list; 16 March
Live chatbot answer: "პროგრამების კატალოგის სამაგისტრო პროგრამებია: სამართალი, ეროვნული და საერთაშორისო უსაფრთხოება, ბიზნესის ადმინისტრირება."
Observed source/route: `program_catalog_sources`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Wrong source and no semester start date.

File: აკადემიური კალენდარი GEO
Category: Master programs; spring final exams
Question: სამაგისტრო პროგრამებისთვის გაზაფხულის დასკვნითი გამოცდები როდის არის?
Expected answer: 29 June - 11 July 2026.
Expected source: `academic_calendar_geo_2025_2026.pdf`, page 3
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: semester start instead of final exams; 16 March
Live chatbot answer: "მაგისტრატურის პროგრამებისთვის 2025-2026 აკადემიურ კალენდარში გაზაფხულის სემესტრის დაწყება მითითებულია 16 მარტი 2026."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Correct route but wrong answer type and date; source row has 9 March start and 29 June - 11 July finals.

File: აკადემიური კალენდარი GEO
Category: One-cycle programs; spring final exams
Question: ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის დასკვნითი გამოცდები როდის არის?
Expected answer: 20 July - 1 August 2026.
Expected source: `academic_calendar_geo_2025_2026.pdf`, page 4
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: bachelor/master dates
Live chatbot answer: "დამტკიცებული 2025-2026 კალენდარი დასკვნით გამოცდებს პროგრამის კატეგორიის მიხედვით უთითებს; ერთსაფეხურიანი პროგრამებისთვის მითითებულია 9-21 თებერვალი 2026 და 20-31 ივლისი 2026."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: PARTIAL
Notes: Correct broad program group, but spring date range does not exactly match the full calendar source end date of 1 August 2026.

File: აკადემიური კალენდარი GEO
Category: One-cycle programs; spring final exam retake
Question: ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის დასკვნითი გამოცდების აღდგენა როდის არის?
Expected answer: 3 - 8 August 2026.
Expected source: `academic_calendar_geo_2025_2026.pdf`, page 4
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: final exam date instead of retake
Live chatbot answer: "დამტკიცებული 2025-2026 კალენდარი დასკვნით გამოცდებს პროგრამის კატეგორიის მიხედვით უთითებს; ერთსაფეხურიანი პროგრამებისთვის მითითებულია 9-21 თებერვალი 2026 და 20-31 ივლისი 2026."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Correct route but returned final exam periods, not spring final retake.

File: აკადემიური კალენდარი GEO
Category: One-cycle programs; spring midterm exams
Question: ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის შუალედური გამოცდები როდის არის?
Expected answer: 25 - 30 May 2026.
Expected source: `academic_calendar_geo_2025_2026.pdf`, page 4
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: bachelor/master fall midterms
Live chatbot answer: "დამტკიცებული 2025-2026 კალენდარი შუალედურ გამოცდებს პროგრამის კატეგორიის მიხედვით უთითებს; ბაკალავრიატისა და მაგისტრატურისთვის მითითებულია 17-22 ნოემბერი 2025, თუ ცალკე კატეგორია არ ვრცელდება."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Correct route but wrong semester and program-specific date.

File: აკადემიური კალენდარი GEO
Category: One-cycle programs; spring midterm retake/make-up
Question: ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის შუალედური გამოცდების აღდგენა როდის არის?
Expected answer: 13 - 18 July 2026.
Expected source: `academic_calendar_geo_2025_2026.pdf`, page 4
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: bachelor/master fall midterms
Live chatbot answer: "დამტკიცებული 2025-2026 კალენდარი შუალედურ გამოცდებს პროგრამის კატეგორიის მიხედვით უთითებს; ბაკალავრიატისა და მაგისტრატურისთვის მითითებულია 17-22 ნოემბერი 2025, თუ ცალკე კატეგორია არ ვრცელდება."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Correct route but wrong semester and no retake/make-up date.

File: Academic Calendar ENG
Category: Bachelor programs except Computer Science; fall semester start
Question: When does the fall semester start for Bachelor programs except Computer Science?
Expected answer: 29 September 2025.
Expected source: `academic_calendar_eng_2025_2026.pdf`, page 1
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: Program Catalog fallback; AI service unavailable
Live chatbot answer: "The AI service is temporarily unavailable. I can connect you with the relevant department."
Observed source/route: `program_catalog_sources`; answer status `no_approved_source_found`; department `study_process`; handover `true`
Result: FAIL
Notes: No calendar answer despite approved ENG source.

File: Academic Calendar ENG
Category: Bachelor programs except Computer Science; spring final exams
Question: When are spring final exams for Bachelor programs except Computer Science?
Expected answer: 29 June - 11 July 2026.
Expected source: `academic_calendar_eng_2025_2026.pdf`, page 1
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: Computer Science semester start
Live chatbot answer: "For Computer Science, the spring semester start is listed as 30 March."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Wrong program group and wrong answer type.

File: Academic Calendar ENG
Category: Computer Science GEO/ENG; spring registration
Question: When is academic registration for Computer Science in spring?
Expected answer: Academic/administrative registration is 9 - 14 March 2026.
Expected source: `academic_calendar_eng_2025_2026.pdf`, page 2
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: bachelor-except-CS registration
Live chatbot answer: "For Computer Science, spring semester registration is 9-14 March, and the semester start is listed as 30 March."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: PASS
Notes: Correct date range and program group; year not stated but answer is grounded in 2025-2026 source context.

File: Academic Calendar ENG
Category: Computer Science GEO/ENG; spring final exams
Question: When do spring final exams take place for Computer Science?
Expected answer: 13 - 25 July 2026.
Expected source: `academic_calendar_eng_2025_2026.pdf`, page 2
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: semester start instead of finals
Live chatbot answer: "For Computer Science, the spring semester start is listed as 30 March."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Correct route but answered semester start, not final exams.

File: Academic Calendar ENG
Category: Master programs; spring semester start
Question: When does the spring semester start for Master programs?
Expected answer: 9 March 2026.
Expected source: `academic_calendar_eng_2025_2026.pdf`, page 3
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: AI service unavailable; Program Catalog source
Live chatbot answer: "The AI service is temporarily unavailable. I can connect you with the relevant department."
Observed source/route: `program_catalog_sources`; answer status `no_approved_source_found`; department `study_process`; handover `true`
Result: FAIL
Notes: No calendar answer despite approved ENG source.

File: Academic Calendar ENG
Category: One-cycle programs; spring final exams
Question: When are final exams for one-cycle programs in spring?
Expected answer: 20 July - 1 August 2026.
Expected source: `academic_calendar_eng_2025_2026.pdf`, page 4
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: bachelor/master dates
Live chatbot answer: "The approved 2025-2026 calendar lists final exams by program category; one-cycle programs include 9-21 February 2026 and 20-31 July 2026."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: PARTIAL
Notes: Correct broad program group, but spring date range does not exactly match the full ENG source end date of 1 August 2026.

File: Academic Calendar ENG
Category: First-year one-cycle English programs; fall start
Question: When does the fall semester start for first-year students of one-cycle English education programs?
Expected answer: 3 November 2025.
Expected source: `academic_calendar_eng_2025_2026.pdf`, page 5
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: bachelor-except-CS registration
Live chatbot answer: "For bachelor programs except Computer Science, the fall semester registration includes 8-13 September 2025 for administrative registration and 15-20 September 2025 for academic registration."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Wrong program group and no semester start date.

File: Academic Calendar ENG
Category: First-year one-cycle English programs; fall midterms
Question: When are fall midterm exams for first-year one-cycle English programs?
Expected answer: 5 - 10 January 2026.
Expected source: `academic_calendar_eng_2025_2026.pdf`, page 5
Expected route: `academic_calendar_2025_2026`
Answer type: exact date
Must not say: bachelor/master generic midterms
Live chatbot answer: "The approved 2025-2026 calendar lists midterm exams by program category; bachelor and master programs use 17-22 November 2025 unless a separate category applies."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Correct route but wrong program-specific midterm date.

File: აკადემიური კალენდარი GEO
Category: Bank holidays
Question: აკადემიური კალენდრის უქმე დღეები რომლებია?
Expected answer: Includes 14 October, 23 November, 7 January, 19 January, 3 March, 8 March, 9 April, 9 May, 12 May, 17 May, 26 May.
Expected source: `academic_calendar_geo_2025_2026.pdf`, page 5
Expected route: `academic_calendar_2025_2026`
Answer type: list/exact dates
Must not say: registration period instead of bank holidays
Live chatbot answer: "ბაკალავრიატის პროგრამებისთვის, კომპიუტერული მეცნიერების გარდა, შემოდგომის სემესტრის ადმინისტრაციული რეგისტრაცია არის 8-13 სექტემბერი 2025, აკადემიური რეგისტრაცია კი 15-20 სექტემბერი 2025."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Correct route but wrong topic answer.

File: აკადემიური კალენდარი GEO
Category: New Year holidays
Question: ახალი წლის არდადეგები როდის არის?
Expected answer: 30 December 2025 - 4 January 2026.
Expected source: `academic_calendar_geo_2025_2026.pdf`, page 5
Expected route: `academic_calendar_2025_2026`
Answer type: exact date range
Must not say: generic "check row" answer when exact source is available
Live chatbot answer: "დამტკიცებულ 2025-2026 აკადემიურ კალენდარში არდადეგების/დასვენების პერიოდები მოცემულია კალენდრის შესაბამის რიგებში; ზუსტი თარიღი უნდა შემოწმდეს კონკრეტული კატეგორიის მიხედვით."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Correct route but no exact holiday date.

File: აკადემიური კალენდარი GEO
Category: Easter holidays
Question: აღდგომის არდადეგები როდის არის?
Expected answer: 10 - 13 April 2026.
Expected source: `academic_calendar_geo_2025_2026.pdf`, page 5
Expected route: `academic_calendar_2025_2026`
Answer type: exact date range
Must not say: generic "check row" answer when exact source is available
Live chatbot answer: "დამტკიცებულ 2025-2026 აკადემიურ კალენდარში არდადეგების/დასვენების პერიოდები მოცემულია კალენდრის შესაბამის რიგებში; ზუსტი თარიღი უნდა შემოწმდეს კონკრეტული კატეგორიის მიხედვით."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Correct route but no exact holiday date.

File: Academic Calendar ENG
Category: New Year holidays
Question: What are the New Year holidays?
Expected answer: 30 December 2025 - 4 January 2026.
Expected source: `academic_calendar_eng_2025_2026.pdf`, page 6
Expected route: `academic_calendar_2025_2026`
Answer type: exact date range
Must not say: generic "check row" answer when exact source is available
Live chatbot answer: "The approved 2025-2026 academic calendar includes holiday rows; answer should be checked against the exact calendar category."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Correct route but no exact holiday date.

File: Academic Calendar ENG
Category: Easter holidays
Question: What are the Easter holidays?
Expected answer: 10 - 13 April 2026.
Expected source: `academic_calendar_eng_2025_2026.pdf`, page 6
Expected route: `academic_calendar_2025_2026`
Answer type: exact date range
Must not say: generic "check row" answer when exact source is available
Live chatbot answer: "The approved 2025-2026 academic calendar includes holiday rows; answer should be checked against the exact calendar category."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Correct route but no exact holiday date.

File: აკადემიური კალენდარი GEO
Category: Ambiguous calendar questions requiring clarification
Question: გამოცდები როდის არის?
Expected answer: Ask which program group, semester, and exam type.
Expected source: Calendar routing policy
Expected route: clarification/no exact date
Answer type: clarification
Must not say: a single default date or registration answer
Live chatbot answer: "ბაკალავრიატის პროგრამებისთვის, კომპიუტერული მეცნიერების გარდა, შემოდგომის სემესტრის ადმინისტრაციული რეგისტრაცია არის 8-13 სექტემბერი 2025, აკადემიური რეგისტრაცია კი 15-20 სექტემბერი 2025."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Clarification missing; answer also switches topic to registration.

File: აკადემიური კალენდარი GEO
Category: Ambiguous calendar questions requiring clarification
Question: რეგისტრაცია როდის არის?
Expected answer: Ask which program group and semester.
Expected source: Calendar routing policy
Expected route: clarification/no exact date
Answer type: clarification
Must not say: a single default registration period
Live chatbot answer: "ბაკალავრიატის პროგრამებისთვის, კომპიუტერული მეცნიერების გარდა, შემოდგომის სემესტრის ადმინისტრაციული რეგისტრაცია არის 8-13 სექტემბერი 2025, აკადემიური რეგისტრაცია კი 15-20 სექტემბერი 2025."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Clarification missing; defaulted to bachelor except Computer Science fall registration.

File: აკადემიური კალენდარი GEO
Category: Ambiguous calendar questions requiring clarification
Question: სემესტრი როდის იწყება?
Expected answer: Ask which program group and semester.
Expected source: Calendar routing policy
Expected route: clarification/no exact date
Answer type: clarification
Must not say: a single default registration period
Live chatbot answer: "ბაკალავრიატის პროგრამებისთვის, კომპიუტერული მეცნიერების გარდა, შემოდგომის სემესტრის ადმინისტრაციული რეგისტრაცია არის 8-13 სექტემბერი 2025, აკადემიური რეგისტრაცია კი 15-20 სექტემბერი 2025."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Clarification missing; answer also switches topic to registration.

File: აკადემიური კალენდარი GEO
Category: Unsupported future year/date questions
Question: 2031 წლის გაზაფხულის სემესტრი როდის იწყება?
Expected answer: Unsupported/no approved source for 2031; no hallucination.
Expected source: Calendar source only covers 2025-2026
Expected route: unsupported/no approved source
Answer type: conservative unsupported
Must not say: invented 2031 exact date
Live chatbot answer: "ამ საკითხზე დამტკიცებულ წყაროში ზუსტი ინფორმაცია ვერ ვიპოვე. შემიძლია დაგაკავშიროთ შესაბამის ოპერატორთან, რომ თქვენი კითხვა სწორ დეპარტამენტს გადაეცეს. ამ საკითხს გადავამისამართებ შესაბამის გუნდთან: Study Process, რათა დეტალები ოფიციალურად დაგიდასტურონ."
Observed source/route: none; answer status `no_approved_source_found`; department `study_process`; handover `true`
Result: PASS
Notes: Correctly did not hallucinate a 2031 calendar date.

File: აკადემიური კალენდარი GEO
Category: Unsupported future year/date questions
Question: 2027 წლის Computer Science-ის გამოცდები როდისაა?
Expected answer: Unsupported/no approved source unless source has 2027; no hallucination.
Expected source: Calendar source only covers 2025-2026
Expected route: unsupported/no approved source
Answer type: conservative unsupported
Must not say: 2025-2026 Computer Science date as answer for 2027
Live chatbot answer: "კომპიუტერული მეცნიერების გაზაფხულის სემესტრის დაწყება მითითებულია 30 მარტს."
Observed source/route: `academic_calendar_2025_2026`; answer status `answered_from_approved_source`; department `study_process`
Result: FAIL
Notes: Unsupported 2027 question reused the 2025-2026 Computer Science spring start answer and did not answer exams.
