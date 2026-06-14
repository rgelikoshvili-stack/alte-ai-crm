# Phase 9BD Academic Calendar GEO/ENG File QA Set

PHASE_9BD_ACADEMIC_CALENDAR_FILE_QA_SET_STATUS=READY_FOR_EXECUTION

Decision state: `BACKEND_DEPLOYED_FILE_QA_FRAMEWORK_AND_PROGRAM_CATALOG_VERIFIED_PENDING_APPROVALS`

Public launch: `NO-GO`

## Scope

- GEO file: `academic_calendar_geo_2025_2026.pdf` / `აკადემიური კალენდარი 2025-2026 GEO`
- ENG file: `academic_calendar_eng_2025_2026.pdf` / `Academic Calendar 2025-2026 ENG`
- Expected route/source group: `academic_calendar_2025_2026`
- Expected department: `academic_calendar` or equivalent Academic Registry / Study Process calendar route
- Execution target: live production backend/chatbot, with no contact creation flow and no CRM object creation

## PASS Criteria

- Exact dates match the approved 2025-2026 academic calendar source.
- The correct program group is used.
- GEO and ENG questions both work.
- Ambiguous calendar questions ask for clarification.
- Unsupported future year/date questions do not hallucinate.
- Public answer has no raw chunk/page/source noise.
- No lead/customer/task is created.

## QA Rows

| ID | File | Category | Question | Expected answer | Expected source | Expected route | Answer type | Must not say |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 9bd-01 | აკადემიური კალენდარი GEO | Bachelor programs except Computer Science; fall semester start | საბაკალავრო პროგრამებისთვის შემოდგომის სემესტრი როდის იწყება? | 29 September 2025 for bachelor programs except Computer Science. | `academic_calendar_geo_2025_2026.pdf`, page 1 | `academic_calendar_2025_2026` | exact date | Computer Science dates; raw chunk/source/page noise; contact request |
| 9bd-02 | აკადემიური კალენდარი GEO | Bachelor programs except Computer Science; spring final exams | საბაკალავრო პროგრამებისთვის გაზაფხულის სემესტრის დასკვნითი გამოცდები როდის არის? | 29 June - 11 July 2026. | `academic_calendar_geo_2025_2026.pdf`, page 1 | `academic_calendar_2025_2026` | exact date | fall finals only; Computer Science dates; lead/customer/task |
| 9bd-03 | აკადემიური კალენდარი GEO | Bachelor programs except Computer Science; spring registration | საბაკალავრო პროგრამებისთვის გაზაფხულის აკადემიური რეგისტრაცია როდის არის? | Academic registration: 2 - 7 March 2026. | `academic_calendar_geo_2025_2026.pdf`, page 1 | `academic_calendar_2025_2026` | exact date | administrative-only answer; Computer Science dates |
| 9bd-04 | აკადემიური კალენდარი GEO | Computer Science GEO/ENG; spring registration | Computer Science-ის გაზაფხულის სემესტრის რეგისტრაცია როდის არის? | Academic/administrative registration: 9 - 14 March 2026. | `academic_calendar_geo_2025_2026.pdf`, page 2 | `academic_calendar_2025_2026` | exact date | bachelor-except-CS registration dates |
| 9bd-05 | აკადემიური კალენდარი GEO | Computer Science GEO/ENG; spring semester start | Computer Science-ის გაზაფხულის სემესტრი როდის იწყება? | 30 March 2026. | `academic_calendar_geo_2025_2026.pdf`, page 2 | `academic_calendar_2025_2026` | exact date | 16 March or 9 March as CS answer |
| 9bd-06 | აკადემიური კალენდარი GEO | Computer Science GEO/ENG; spring final exams | Computer Science-ის გაზაფხულის დასკვნითი გამოცდები როდის არის? | 13 - 25 July 2026. | `academic_calendar_geo_2025_2026.pdf`, page 2 | `academic_calendar_2025_2026` | exact date | 29 June - 11 July as CS answer |
| 9bd-07 | აკადემიური კალენდარი GEO | Master programs; spring semester start | სამაგისტრო პროგრამებისთვის გაზაფხულის სემესტრი როდის იწყება? | 9 March 2026. | `academic_calendar_geo_2025_2026.pdf`, page 3 | `academic_calendar_2025_2026` | exact date | 16 March as master answer |
| 9bd-08 | აკადემიური კალენდარი GEO | Master programs; spring final exams | სამაგისტრო პროგრამებისთვის გაზაფხულის დასკვნითი გამოცდები როდის არის? | 29 June - 11 July 2026. | `academic_calendar_geo_2025_2026.pdf`, page 3 | `academic_calendar_2025_2026` | exact date | Computer Science or one-cycle dates |
| 9bd-09 | აკადემიური კალენდარი GEO | One-cycle programs; spring final exams | ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის დასკვნითი გამოცდები როდის არის? | 20 July - 1 August 2026. | `academic_calendar_geo_2025_2026.pdf`, page 4 | `academic_calendar_2025_2026` | exact date | bachelor/master dates |
| 9bd-10 | აკადემიური კალენდარი GEO | One-cycle programs; spring final exam retake | ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის დასკვნითი გამოცდების აღდგენა როდის არის? | 3 - 8 August 2026. | `academic_calendar_geo_2025_2026.pdf`, page 4 | `academic_calendar_2025_2026` | exact date | midterm retake; bachelor/master retake |
| 9bd-11 | აკადემიური კალენდარი GEO | One-cycle programs; spring midterm exams | ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის შუალედური გამოცდები როდის არის? | 25 - 30 May 2026. | `academic_calendar_geo_2025_2026.pdf`, page 4 | `academic_calendar_2025_2026` | exact date | quiz dates as midterm answer |
| 9bd-12 | აკადემიური კალენდარი GEO | One-cycle programs; spring midterm retake/make-up | ერთსაფეხურიანი პროგრამებისთვის გაზაფხულის შუალედური გამოცდების აღდგენა როდის არის? | 13 - 18 July 2026. | `academic_calendar_geo_2025_2026.pdf`, page 4 | `academic_calendar_2025_2026` | exact date | final retake date |
| 9bd-13 | Academic Calendar ENG | Bachelor programs except Computer Science; fall semester start | When does the fall semester start for Bachelor programs except Computer Science? | 29 September 2025. | `academic_calendar_eng_2025_2026.pdf`, page 1 | `academic_calendar_2025_2026` | exact date | Computer Science dates |
| 9bd-14 | Academic Calendar ENG | Bachelor programs except Computer Science; spring final exams | When are spring final exams for Bachelor programs except Computer Science? | 29 June - 11 July 2026. | `academic_calendar_eng_2025_2026.pdf`, page 1 | `academic_calendar_2025_2026` | exact date | fall finals only |
| 9bd-15 | Academic Calendar ENG | Computer Science GEO/ENG; spring registration | When is academic registration for Computer Science in spring? | Academic/administrative registration: 9 - 14 March 2026. | `academic_calendar_eng_2025_2026.pdf`, page 2 | `academic_calendar_2025_2026` | exact date | bachelor-except-CS registration |
| 9bd-16 | Academic Calendar ENG | Computer Science GEO/ENG; spring final exams | When do spring final exams take place for Computer Science? | 13 - 25 July 2026. | `academic_calendar_eng_2025_2026.pdf`, page 2 | `academic_calendar_2025_2026` | exact date | bachelor/master dates |
| 9bd-17 | Academic Calendar ENG | Master programs; spring semester start | When does the spring semester start for Master programs? | 9 March 2026. | `academic_calendar_eng_2025_2026.pdf`, page 3 | `academic_calendar_2025_2026` | exact date | 16 March as master answer |
| 9bd-18 | Academic Calendar ENG | One-cycle programs; spring final exams | When are final exams for one-cycle programs in spring? | 20 July - 1 August 2026. | `academic_calendar_eng_2025_2026.pdf`, page 4 | `academic_calendar_2025_2026` | exact date | bachelor/master dates |
| 9bd-19 | Academic Calendar ENG | First-year one-cycle English programs; fall start | When does the fall semester start for first-year students of one-cycle English education programs? | 3 November 2025. | `academic_calendar_eng_2025_2026.pdf`, page 5 | `academic_calendar_2025_2026` | exact date | one-cycle general 6 October start |
| 9bd-20 | Academic Calendar ENG | First-year one-cycle English programs; fall midterms | When are fall midterm exams for first-year one-cycle English programs? | 5 - 10 January 2026. | `academic_calendar_eng_2025_2026.pdf`, page 5 | `academic_calendar_2025_2026` | exact date | one-cycle general 1 - 6 December |
| 9bd-21 | აკადემიური კალენდარი GEO | Bank holidays | აკადემიური კალენდრის უქმე დღეები რომლებია? | Includes listed bank holidays: 14 October, 23 November, 7 January, 19 January, 3 March, 8 March, 9 April, 9 May, 12 May, 17 May, 26 May. | `academic_calendar_geo_2025_2026.pdf`, page 5 | `academic_calendar_2025_2026` | list/exact dates | invented holidays |
| 9bd-22 | აკადემიური კალენდარი GEO | New Year holidays | ახალი წლის არდადეგები როდის არის? | 30 December 2025 - 4 January 2026. | `academic_calendar_geo_2025_2026.pdf`, page 5 | `academic_calendar_2025_2026` | exact date range | generic holiday answer |
| 9bd-23 | აკადემიური კალენდარი GEO | Easter holidays | აღდგომის არდადეგები როდის არის? | 10 - 13 April 2026. | `academic_calendar_geo_2025_2026.pdf`, page 5 | `academic_calendar_2025_2026` | exact date range | unsupported/handover if source-backed answer is available |
| 9bd-24 | Academic Calendar ENG | New Year holidays | What are the New Year holidays? | 30 December 2025 - 4 January 2026. | `academic_calendar_eng_2025_2026.pdf`, page 6 | `academic_calendar_2025_2026` | exact date range | invented year |
| 9bd-25 | Academic Calendar ENG | Easter holidays | What are the Easter holidays? | 10 - 13 April 2026. | `academic_calendar_eng_2025_2026.pdf`, page 6 | `academic_calendar_2025_2026` | exact date range | generic no-date answer |
| 9bd-26 | აკადემიური კალენდარი GEO | Ambiguous calendar question requiring clarification | გამოცდები როდის არის? | Ask which program group, semester, and exam type. | Calendar routing policy | clarification/no exact date | clarification | single date; hallucinated exam period |
| 9bd-27 | აკადემიური კალენდარი GEO | Ambiguous registration question requiring clarification | რეგისტრაცია როდის არის? | Ask which program group and semester. | Calendar routing policy | clarification/no exact date | clarification | single date; contact request |
| 9bd-28 | აკადემიური კალენდარი GEO | Ambiguous semester-start question requiring clarification | სემესტრი როდის იწყება? | Ask which program group and semester. | Calendar routing policy | clarification/no exact date | clarification | single date; raw source noise |
| 9bd-29 | აკადემიური კალენდარი GEO | Unsupported future year/date question | 2031 წლის გაზაფხულის სემესტრი როდის იწყება? | Unsupported/no approved source for 2031; do not provide invented dates. | Calendar source only covers 2025-2026 | unsupported/no approved source | conservative unsupported | 2031 exact date; 2026 date as if 2031 |
| 9bd-30 | აკადემიური კალენდარი GEO | Unsupported future Computer Science question | 2027 წლის Computer Science-ის გამოცდები როდისაა? | Unsupported/no approved source unless source has 2027; no hallucination. | Calendar source only covers 2025-2026 | unsupported/no approved source | conservative unsupported | invented 2027 exams |

## Safety Claims

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
