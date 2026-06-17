# Phase 9BC Global File Source Map

Status: `CODE_READY_PENDING_REVIEW`  
Decision state: `BACKEND_CODE_GLOBAL_FILE_QA_FRAMEWORK_READY_PENDING_REVIEW`  
Public launch: `NO-GO`

This map defines the first scalable file-by-file routing layer for ALTE chatbot knowledge QA. It starts with the Phase A primary files and is designed to expand to all 45 primary chatbot sources. The routing rule is conservative: if a user question can plausibly belong to more than one source group, the chatbot must ask clarification instead of retrieving broadly.

## Global Routing Principles

- Source group selection must be specific to the file/topic boundary.
- Similar keywords are resolved by priority rules before retrieval.
- Broad questions ask clarification and use no broad approved-source fallback.
- Unsupported facts must return no approved source or operator fallback, not a guessed answer.
- Informational answers must not create lead/customer/task records.
- User-facing answers must not expose raw source keys, page/chunk IDs, or internal policy text.

## Priority Examples

| User phrasing | Required route | Required source group | Do not route to |
|---|---|---|---|
| ეროვნული გამოცდების გარეშე ჩარიცხვა | Admissions | `admissions_rules` | `exams_and_assessment` |
| დასკვნით გამოცდაზე დაშვების წესი | Study Process | `exams_and_assessment` | `academic_calendar_2025_2026` |
| დასკვნითი გამოცდები როდის არის? | Study Process | `academic_calendar_2025_2026` | `exams_and_assessment` |
| რამდენი კრედიტია პროგრამა? | Programs clarification | none | broad retrieval |
| რა ღირს სამართლის პროგრამა? | Unsupported / finance or operator if source missing | none unless approved source contains tuition | guessed tuition |

## Clarification Prompts

| Ambiguous question | Clarification |
|---|---|
| გამოცდებზე მაინტერესებს | გთხოვთ დააზუსტოთ: გამოცდების თარიღები გაინტერესებთ, გამოცდაზე დაშვების წესი, შეფასება თუ გადაბარება? |
| პროგრამის კრედიტები მაინტერესებს | რომელი პროგრამის კრედიტები გაინტერესებთ — ბაკალავრიატი, მაგისტრატურა, მედიცინა / MD, სტომატოლოგია თუ კონკრეტული პროგრამა? |
| მიღება მაინტერესებს | გთხოვთ დააზუსტოთ: ბაკალავრიატი, მაგისტრატურა, საერთაშორისო მიღება, საბუთები თუ გამოცდების გარეშე ჩარიცხვა გაინტერესებთ? |
| სტატუსზე კითხვა მაქვს | სტუდენტის სტატუსთან დაკავშირებით რა გაინტერესებთ — შეჩერება, აღდგენა, შეწყვეტა თუ მობილობა? |

## Phase A Source Map

Routability rule: entries marked as `missing_source_group_config` are catalogued for planning and QA expansion only. They must not be used for routing or retrieval until strict source group membership is configured with explicit source identity metadata.

| File/source | Human-readable label | Source group | Department/route | Topic category | Use when | Do not use when | Common keywords | Ambiguity triggers | Clarification | Unsupported examples | Operator fallback |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `01_program_catalog.pdf` | Higher Education Program Catalog / უმაღლესი განათლების პროგრამების კატალოგი | `program_catalog_sources` | Programs | Program catalog | program count, program lists, level distribution, qualifications, catalog-specific credits/language | generic ECTS rules, tuition not in catalog, admission without exams, library catalog | program catalog, პროგრამების კატალოგი, საბაკალავრო პროგრამები, სამაგისტრო პროგრამები | generic program credits, broad catalog detail | ask which level/program/detail | exact tuition, consultant phone, 2031 space campus program | Programs / Admissions |
| Academic Calendar GEO | აკადემიური კალენდარი 2025–2026 | `academic_calendar_2025_2026` | Study Process | Calendar | Georgian registration, semester, exam, holiday dates | exam admission rules, GPA/FX, admission documents | როდის, თარიღი, კალენდარი, განრიგი | გამოცდებზე მაინტერესებს | ask dates vs rules vs assessment | future calendar outside source | Study Process |
| Academic Calendar ENG | Academic Calendar 2025-2026 English | `academic_calendar_2025_2026` | Study Process | Calendar | English date/schedule questions | exam rules, admissions, program requirements | when, date, schedule, semester | calendar question | ask which calendar date | future calendar outside source | Study Process |
| Bachelor Regulation | ბაკალავრიატის დებულება | `official_academic_rules` | Study Process | Academic rules | bachelor ECTS, bachelor completion rules | specific program catalog credits, tuition, calendar dates | bachelor ECTS, ბაკალავრიატი | generic credits | ask general bachelor vs specific program | tuition or consultant phone | Study Process |
| Master Regulation | მაგისტრატურის დებულება | `official_academic_rules` | Study Process | Academic rules | master ECTS, master completion rules | specific program catalog credits, international requirements | master ECTS, მაგისტრატურა | generic credits | ask general master vs specific program | current tuition | Study Process |
| Study Process Rule | სასწავლო პროცესის მარეგულირებელი წესი | `student_status_and_mobility` | Study Process | Status/mobility | status suspension, restoration, termination, mobility | calendar dates, program catalog, tuition | სტატუსი, შეჩერება, აღდგენა, მობილობა | სტატუსზე კითხვა მაქვს | ask suspension/restoration/termination/mobility | legal advice outside source | Study Process |
| ECTS Credit Recognition | კრედიტების აღიარების წესი | `missing_source_group_config` (planned: `student_status_and_mobility`) | Study Process | Credit recognition | catalogued only until strict source membership is configured | program credit amount, bachelor/master ECTS totals | კრედიტების აღიარება, credit recognition | კრედიტებზე კითხვა | ask recognition vs credit volume | external institution decision | Study Process |
| Exam Regulation | გამოცდებისა და შეფასების წესი | `missing_source_group_config` (planned: `exams_and_assessment`) | Study Process | Exams/assessment | catalogued only until strict source membership is configured | exam dates/calendar, admission without national exams | დასკვნით, დაშვება, გადაბარება, FX, ქულა | გამოცდებზე მაინტერესებს | ask dates/rules/assessment/retake | future schedule not in source | Study Process |
| Financial Support | ფინანსური მხარდაჭერის მექანიზმები | `finance_sources` | Finance | Finance | financial support, internal scholarships, payment support | program catalog, exact current tuition if missing | დაფინანსება, scholarship, tuition | გადახდებზე მაინტერესებს | ask tuition/payment/grants/finance contact | current exact tuition not sourced | Finance |
| State/Social Grants | სახელმწიფო და სოციალური გრანტები | `finance_sources` | Finance | Grants | state grants, social grants, grant eligibility | program list, admissions documents | გრანტი, grant, social grant | გრანტებზე მაინტერესებს | ask state/social/internal support | future grant amount | Finance |
| Student Services | სტუდენტური სერვისები | `missing_source_group_config` (planned: `student_status_and_mobility`) | Study Process | Student support | catalogued only until strict source membership is configured | explicit operator request, library/career | student services, სტუდენტური სერვისი | დახმარება მინდა | ask which support type | personal case decision | Human Operator / Study Process |
| Student Rights | სტუდენტის უფლებები | `missing_source_group_config` (planned: `student_status_and_mobility`) | Study Process | Rights | catalogued only until strict source membership is configured | ombudsman complaint unless explicit, ethics-specific cases | student rights, უფლებები | უფლებებზე კითხვა | ask which right/obligation | legal advice outside source | Study Process |
| Ombudsman | ომბუდსმენი | `missing_source_group_config` (planned: `student_status_and_mobility`) | Study Process | Rights/escalation | catalogued only until strict source membership is configured | ethics unless explicit, operator contact only | ombudsman, ომბუდსმენი | საჩივარზე კითხვა | ask complaint/role/escalation | legal representation | Study Process |
| Library | ბიბლიოთეკა | `library_sources` | Library | Library | library catalog, books, databases, electronic resources | program catalog, program list, calendar | ბიბლიოთეკის კატალოგი, library catalog, databases | ბიბლიოთეკაზე კითხვა | ask catalog/books/databases/resources | rare manuscripts | Library |
| Career | კარიერული განვითარება | `career_sources` | Career | Career | career services, internships, employment support | admissions, status, operator request | კარიერა, სტაჟირება, career, internship | კარიერაზე კითხვა | ask internship/employment/consultation | guaranteed employment | Career |
| Special Needs | სპეციალური საჭიროებების მხარდაჭერა | `missing_source_group_config` (planned: `student_status_and_mobility`) | Study Process | Accessibility/support | catalogued only until strict source membership is configured | medical advice, contact-only operator request | special needs, accessibility | სპეციალურ საჭიროებებზე კითხვა | ask which support topic | medical diagnosis/advice | Study Process |
| AI Policy | ხელოვნური ინტელექტის გამოყენების პოლიტიკა | `missing_source_group_config` (planned: `official_academic_rules`) | Study Process | Academic integrity | catalogued only until strict source membership is configured | AI program catalog, IT support | AI policy, ხელოვნური ინტელექტი | AI-ზე კითხვა | ask which AI-use rule | AI product support | Study Process |
| Plagiarism | პლაგიატის წესი | `missing_source_group_config` (planned: `official_academic_rules`) | Study Process | Academic integrity | catalogued only until strict source membership is configured | ethics unless broad conduct, exam dates | plagiarism, პლაგიატი | პლაგიატზე კითხვა | ask definition/procedure/consequence | personal disciplinary decision | Study Process |
| Ethics Code | ეთიკის კოდექსი | `missing_source_group_config` (planned: `official_academic_rules`) | Study Process | Academic conduct | catalogued only until strict source membership is configured | program catalog, finance, library | ethics code, ეთიკის კოდექსი | ეთიკაზე კითხვა | ask which ethics-code area | personal legal judgment | Study Process |

## Launch And Safety Status

- Production backend is verified for core knowledge/routing/answer cleanup, but Phase 9BC is local code/docs only.
- Deploy status: `NOT_DEPLOYED`
- Public launch remains: `NO-GO`
- No real site, upload, embed, contact-flow, DB, Secret Manager, CORS, or Bridge Hub changes are part of this phase.
