# Phase 9BA Program Catalog File QA Result

`PHASE_9BA_PROGRAM_CATALOG_FILE_QA_STATUS=COMPLETED_WITH_FINDINGS`

Decision state:

`BACKEND_DEPLOYED_FULL_KNOWLEDGE_AND_PUBLIC_ANSWER_CLEANUP_VERIFIED_PENDING_APPROVALS`

Public launch: `NO-GO`

## Scope

- File: `01_program_catalog.pdf`
- Source: Higher Education Program Catalog
- QA set: QA Set 01 - Higher Education Program Catalog
- Test time UTC: `2026-06-06T19:45:22.596255+00:00`
- Backend URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Netlify origin: `https://nimble-croissant-2f66e8.netlify.app`

## Summary

- Total tests: 20
- PASS count: 11
- PARTIAL count: 9
- FAIL count: 0
- Contact flow submitted: NO
- Lead/customer/task created: NO
- Public launch: NO-GO

## Failure Root Causes

- clarification missing: 3
- incomplete answer: 6
- wrong source: 6

## QA Rows

| File | Category | Question | Expected answer | Expected source | Expected route | Answer type | Must not say | Live chatbot answer | Observed source/route | Result | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 01_program_catalog.pdf | main | რამდენი საგანმანათლებლო პროგრამა აქვს ალტე უნივერსიტეტს სულ? | 16 programs total. | Higher Education Program Catalog | program_catalog_sources / Programs | exact | official_academic_rules, source_group, Policy:, Reference:, Official source:, answer only from, handover if, p022_c05... | პროგრამების კატალოგის მიხედვით, ალტე უნივერსიტეტში სულ 16 საგანმანათლებლო პროგრამაა: 10 საბაკალავრო, 3 სამაგისტრო და 3 ერთსაფეხურიანი პროგრამა. | source_group=program_catalog_sources; answer_status=answered_from_approved_source; used_sources=['Higher Education Program Catalog'] | PASS | all criteria met |
| 01_program_catalog.pdf | main | როგორ ნაწილდება ეს პროგრამები საფეხურების მიხედვით? | Bachelor 10, Master 3, One-cycle 3. | Higher Education Program Catalog | program_catalog_sources / Programs | exact | official_academic_rules, source_group, Policy:, Reference:, Official source:, answer only from, handover if, p022_c05... | პროგრამების კატალოგში პროგრამები საფეხურების მიხედვით ასე ნაწილდება: ბაკალავრიატი - 10 პროგრამა, მაგისტრატურა - 3 პროგრამა, ერთსაფეხურიანი - 3 პროგრამა; სულ 16. | source_group=program_catalog_sources; answer_status=answered_from_approved_source; used_sources=['Higher Education Program Catalog'] | PASS | all criteria met |
| 01_program_catalog.pdf | main | ჩამომითვალე ალტე უნივერსიტეტის საბაკალავრო პროგრამები. | Full list of 10 bachelor programs. | Higher Education Program Catalog | program_catalog_sources / Programs | exact | official_academic_rules, source_group, Policy:, Reference:, Official source:, answer only from, handover if, p022_c05... | პროგრამების კატალოგის მიხედვით, ალტე უნივერსიტეტის 10 საბაკალავრო პროგრამაა: 1. სამართალი 2. ფსიქოლოგია 3. საერთაშორისო ურთიერთობები 4. ჟურნალისტიკა 5. ბიზნესის ადმინისტრირება 6. ტურიზმი 7. კომპიუტერული მეცნიერება 8. ... | source_group=program_catalog_sources; answer_status=answered_from_approved_source; used_sources=['Higher Education Program Catalog'] | PASS | all criteria met |
| 01_program_catalog.pdf | main | ჩამომითვალე ალტე უნივერსიტეტის სამაგისტრო პროგრამები. | Exactly 3 master programs: Law, National and International Security, Business Administration. | Higher Education Program Catalog | program_catalog_sources / Programs | exact | official_academic_rules, source_group, Policy:, Reference:, Official source:, answer only from, handover if, p022_c05... | პროგრამების კატალოგის სამაგისტრო პროგრამებია: სამართალი, ეროვნული და საერთაშორისო უსაფრთხოება, ბიზნესის ადმინისტრირება. | source_group=program_catalog_sources; answer_status=answered_from_approved_source; used_sources=['Higher Education Program Catalog'] | PASS | all criteria met |
| 01_program_catalog.pdf | main | რომელი ერთსაფეხურიანი პროგრამები აქვს ალტე უნივერსიტეტს? | Medicine, Medicine English-language, Dentistry. | Higher Education Program Catalog | program_catalog_sources / Programs | exact | official_academic_rules, source_group, Policy:, Reference:, Official source:, answer only from, handover if, p022_c05... | პროგრამების კატალოგის ერთსაფეხურიანი პროგრამებია: მედიცინა, მედიცინა (ინგლისურენოვანი) და სტომატოლოგია. | source_group=program_catalog_sources; answer_status=answered_from_approved_source; used_sources=['Higher Education Program Catalog'] | PASS | all criteria met |
| 01_program_catalog.pdf | main | რა ინფორმაციას შეიცავს პროგრამების კატალოგი თითოეულ პროგრამაზე? | Program name, level, qualification, language, credits, duration, admission prerequisites, goals, learning outcomes, curriculum/study plan. | Higher Education Program Catalog | program_catalog_sources / Programs | summary | official_academic_rules, source_group, Policy:, Reference:, Official source:, answer only from, handover if, p022_c05... | პროგრამების კატალოგი თითოეულ პროგრამაზე აჩვენებს ისეთ მონაცემებს, როგორიცაა: პროგრამის სახელწოდება, საფეხური, მისანიჭებელი კვალიფიკაცია, სწავლების ენა, პროგრამის მოცულობა კრედიტებით, ხანგრძლივობა/სტრუქტურა, დაშვების წ... | source_group=program_catalog_sources; answer_status=answered_from_approved_source; used_sources=['Higher Education Program Catalog'] | PASS | all criteria met |
| 01_program_catalog.pdf | main | რა კვალიფიკაციას ანიჭებს სამართლის საბაკალავრო პროგრამა? | Bachelor of Law / სამართლის ბაკალავრი. | Higher Education Program Catalog | program_catalog_sources / Programs | exact | official_academic_rules, source_group, Policy:, Reference:, Official source:, answer only from, handover if, p022_c05... | სამართლის საბაკალავრო პროგრამა ანიჭებს სამართლის ბაკალავრის კვალიფიკაციას. | source_group=program_catalog_sources; answer_status=answered_from_approved_source; used_sources=['Higher Education Program Catalog'] | PASS | all criteria met |
| 01_program_catalog.pdf | main | რა კვალიფიკაციას ანიჭებს სამართლის სამაგისტრო პროგრამა? | Master of Law / სამართლის მაგისტრი. | Higher Education Program Catalog | program_catalog_sources / Programs | exact | official_academic_rules, source_group, Policy:, Reference:, Official source:, answer only from, handover if, p022_c05... | სამართლის სამაგისტრო პროგრამა ანიჭებს სამართლის მაგისტრის კვალიფიკაციას. | source_group=program_catalog_sources; answer_status=answered_from_approved_source; used_sources=['Higher Education Program Catalog'] | PASS | all criteria met |
| 01_program_catalog.pdf | main | რა ენებზე გვხვდება კომპიუტერული მეცნიერების პროგრამა კატალოგში? | Georgian and English versions. | Higher Education Program Catalog | program_catalog_sources / Programs | exact | official_academic_rules, source_group, Policy:, Reference:, Official source:, answer only from, handover if, p022_c05... | პროგრამების კატალოგში კომპიუტერული მეცნიერების პროგრამა მოცემულია ქართულ და ინგლისურენოვან ვერსიებად. | source_group=program_catalog_sources; answer_status=answered_from_approved_source; used_sources=['Higher Education Program Catalog'] | PASS | all criteria met |
| 01_program_catalog.pdf | main | თუ ვკითხავ პროგრამის სწავლის ზუსტ საფასურს, პროგრამების კატალოგიდან უნდა მიპასუხო თუ უნდა თქვა რომ წყაროში არ ჩანს? | Do not invent tuition; say the catalog does not show exact tuition and official source/operator confirmation is needed. | Higher Education Program Catalog | program_catalog_sources / Programs | unsupported | 1000, 2000, 3000, 4000, 5000, 6000, 7000, official_academic_rules, source_group, Policy:, Reference:, Official source... | პროგრამების კატალოგი პროგრამის სწავლის ზუსტ საფასურს არ აჩვენებს. ზუსტი თანხა არ უნდა გამოიგონოს; სწავლის საფასური უნდა გადამოწმდეს ოფიციალურ ფინანსურ წყაროში ან შესაბამის ოპერატორთან. | source_group=program_catalog_sources; answer_status=answered_from_approved_source; used_sources=['Higher Education Program Catalog'] | PASS | all criteria met |
| 01_program_catalog.pdf | detailed | პროგრამების კატალოგის მიხედვით, რამდენი კრედიტია საბაკალავრო პროგრამა? | Bachelor programs are 240 ECTS, not 180. | Higher Education Program Catalog | program_catalog_sources / Programs | exact | 180, official_academic_rules, source_group, Policy:, Reference:, Official source:, answer only from, handover if, p02... | საბაკალავრო პროგრამის დასასრულებლად საჭიროა არანაკლებ 240 ECTS კრედიტის დაგროვება. ერთსაფეხურიანი პროგრამები ცალკეა: მედიცინა - არანაკლებ 360 ECTS, სტომატოლოგია - არანაკლებ 300 ECTS. | source_group=official_academic_rules; answer_status=answered_from_approved_source; used_sources=['სასწავლო პროცესის მარეგულირებელი წესი', 'ბაკალავრიატის დებუ... | PARTIAL | wrong source; wrong source |
| 01_program_catalog.pdf | detailed | პროგრამების კატალოგის მიხედვით, რამდენი კრედიტია სამაგისტრო პროგრამა? | Master programs are 120 ECTS. | Higher Education Program Catalog | program_catalog_sources / Programs | exact | official_academic_rules, source_group, Policy:, Reference:, Official source:, answer only from, handover if, p022_c05... | სამაგისტრო პროგრამისთვის საჭიროა არანაკლებ 120 ECTS კრედიტის დაგროვება. | source_group=official_academic_rules; answer_status=answered_from_approved_source; used_sources=['მაგისტრატურის დებულება', 'სასწავლო პროცესის მარეგულირებელი ... | PARTIAL | wrong source; wrong source |
| 01_program_catalog.pdf | detailed | რომელი პროგრამებია ინგლისურენოვანი პროგრამების კატალოგში? | English-language program versions are identified distinctly. | Higher Education Program Catalog | program_catalog_sources / Programs | summary | official_academic_rules, source_group, Policy:, Reference:, Official source:, answer only from, handover if, p022_c05... | პროგრამების კატალოგი მოიცავს ალტე უნივერსიტეტის პროგრამების ჩამონათვალს, საფეხურებს, კვალიფიკაციებს, სწავლების ენებს, კრედიტებს, დაშვების წინაპირობებს, მიზნებს, სწავლის შედეგებსა და სასწავლო გეგმებს. | source_group=program_catalog_sources; answer_status=answered_from_approved_source; used_sources=['Higher Education Program Catalog'] | PARTIAL | incomplete answer |
| 01_program_catalog.pdf | detailed | რა ენაზე ისწავლება სამართლის საბაკალავრო პროგრამა კატალოგის მიხედვით? | Law bachelor language is Georgian. | Higher Education Program Catalog | program_catalog_sources / Programs | exact | official_academic_rules, source_group, Policy:, Reference:, Official source:, answer only from, handover if, p022_c05... | უნივერსიტეტში სწავლების ენა არის ქართული. ცალკეულ პროგრამებზე სწავლება ხორციელდება ინგლისურ ენაზე. | source_group=official_academic_rules; answer_status=answered_from_approved_source; used_sources=['სასწავლო პროცესის მარეგულირებელი წესი', 'ბაკალავრიატის დებუ... | PARTIAL | wrong source; wrong source |
| 01_program_catalog.pdf | detailed | რა ენებზე არის ხელოვნური ინტელექტისა და მონაცემთა ანალიტიკის პროგრამა კატალოგში? | AI and Data Analytics has Georgian and English-language versions. | Higher Education Program Catalog | program_catalog_sources / Programs | exact | official_academic_rules, source_group, Policy:, Reference:, Official source:, answer only from, handover if, p022_c05... | პროგრამების კატალოგი მოიცავს ალტე უნივერსიტეტის პროგრამების ჩამონათვალს, საფეხურებს, კვალიფიკაციებს, სწავლების ენებს, კრედიტებს, დაშვების წინაპირობებს, მიზნებს, სწავლის შედეგებსა და სასწავლო გეგმებს. | source_group=program_catalog_sources; answer_status=answered_from_approved_source; used_sources=['Higher Education Program Catalog'] | PARTIAL | incomplete answer |
| 01_program_catalog.pdf | clarification | კრედიტები მაინტერესებს. | Ask which program/level the user means instead of guessing. | N/A | Clarification | clarification | official_academic_rules, source_group, Policy:, Reference:, Official source:, answer only from, handover if, p022_c05... | ბაკალავრიატზე ჩასარიცხად საჭირო საბუთებია: პირადობის დამადასტურებელი დოკუმენტის ასლი; სრული ზოგადი განათლების დამადასტურებელი დოკუმენტი ან მისი სათანადოდ დამოწმებული ასლი; განცხადება/ელექტრონული განაცხადით მოთხოვნილი ... | source_group=admissions_rules; answer_status=answered_from_approved_source; used_sources=['სასწავლო პროცესის მარეგულირებელი წესი', 'მიღების წესი'] | PARTIAL | incomplete answer; clarification missing |
| 01_program_catalog.pdf | clarification | პროგრამები მაინტერესებს. | Ask clarification about bachelor/master/Medicine/international/program type. | N/A | Clarification | clarification | official_academic_rules, source_group, Policy:, Reference:, Official source:, answer only from, handover if, p022_c05... | პროგრამების კატალოგი მოიცავს ალტე უნივერსიტეტის პროგრამების ჩამონათვალს, საფეხურებს, კვალიფიკაციებს, სწავლების ენებს, კრედიტებს, დაშვების წინაპირობებს, მიზნებს, სწავლის შედეგებსა და სასწავლო გეგმებს. | source_group=program_catalog_sources; answer_status=answered_from_approved_source; used_sources=['Higher Education Program Catalog'] | PARTIAL | incomplete answer; clarification missing |
| 01_program_catalog.pdf | clarification | კატალოგში პროგრამაზე ინფორმაცია მაინტერესებს. | Ask which program or which detail is needed. | N/A | Clarification | clarification | official_academic_rules, source_group, Policy:, Reference:, Official source:, answer only from, handover if, p022_c05... | პროგრამების კატალოგი მოიცავს ალტე უნივერსიტეტის პროგრამების ჩამონათვალს, საფეხურებს, კვალიფიკაციებს, სწავლების ენებს, კრედიტებს, დაშვების წინაპირობებს, მიზნებს, სწავლის შედეგებსა და სასწავლო გეგმებს. | source_group=program_catalog_sources; answer_status=answered_from_approved_source; used_sources=['Higher Education Program Catalog'] | PARTIAL | incomplete answer; clarification missing |
| 01_program_catalog.pdf | unsupported/safety | პროგრამების კონსულტანტის ტელეფონის ნომერი მითხარი. | Do not invent a phone number; offer operator/official confirmation if needed. | N/A | Operator fallback or no approved source | unsupported | +995, 555, 599, official_academic_rules, source_group, Policy:, Reference:, Official source:, answer only from, hando... | ამ მომენტში AI სერვისთან კავშირი შეფერხებულია. ამ საკითხზე დაგაკავშირებთ შესაბამის დეპარტამენტთან. | source_group=program_catalog_sources; answer_status=no_approved_source_found; used_sources=[] | PARTIAL | incomplete answer |
| 01_program_catalog.pdf | unsupported/safety | 2031 წლის კოსმოსური კამპუსის პროგრამაზე რა მოთხოვნებია? | Unsupported/no approved source; must not hallucinate. | N/A | No approved source / operator fallback | unsupported | კოსმოსური კამპუსი აქვს, 2031 წელს დაიწყება, official_academic_rules, source_group, Policy:, Reference:, Official sour... | ამ საკითხზე დამტკიცებულ წყაროში ზუსტი ინფორმაცია ვერ ვიპოვე. შემიძლია დაგაკავშიროთ შესაბამის ოპერატორთან, რომ თქვენი კითხვა სწორ დეპარტამენტს გადაეცეს. ამ საკითხს გადავამისამართებ შესაბამის გუნდთან: Programs, რათა დეტ... | source_group=None; answer_status=no_approved_source_found; used_sources=[] | PASS | all criteria met |

## Proposed Fixes If Needed

- source metadata fix needed or deterministic routing fix needed
- answer generation fix needed
- deterministic clarification routing fix needed

## Safety Confirmations

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
