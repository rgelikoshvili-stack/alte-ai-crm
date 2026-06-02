# Phase 9AY Program Catalog Source QA Result

PHASE_9AY_PROGRAM_CATALOG_QA_STATUS=PASSED

Decision state: `BACKEND_DEPLOYED_FULL_KNOWLEDGE_QA_PASSED_PENDING_APPROVALS`

Public launch: `NO-GO`

## Tested Source

- File/source: `01_program_catalog.pdf` / Higher Education Program Catalog
- Topic: Programs and Admissions

## Tested URLs

- Production backend: https://alte-ai-crm-backend-226875230147.europe-west1.run.app
- Netlify chatbot: https://nimble-croissant-2f66e8.netlify.app/join.html

## Summary

- Test time UTC: 2026-06-02T19:04:08.348547+00:00
- Backend revision: `alte-ai-crm-backend-00048-zk8`
- Backend image tag: `v0.9-phase-9ay-program-catalog-source-routing3`
- Traffic: 100%
- Total questions: 10
- Passed: 10
- Failed: 0
- Operator API auth: AUTH_OK
- Contact flow submitted: NO
- Real contact data sent: NO
- Lead/customer/task created: NO
- Public launch: NO-GO

## Ten-Question Results

| Question ID | Status | answer_status | source_group | Catalog source exposed | should_handover | department | Answer snippet |
| --- | --- | --- | --- | --- | --- | --- | --- |
| program_count_total | PASS | answered_from_approved_source | program_catalog_sources | YES | False | programs | პროგრამების კატალოგის მიხედვით, ალტე უნივერსიტეტში სულ 16 საგანმანათლებლო პროგრამაა: 10 საბაკალავრო, 3 სამაგისტრო და 3 ერთსაფეხურიანი პროგრამა.  წყარო: Higher Education Program Cat |
| program_levels_distribution | PASS | answered_from_approved_source | program_catalog_sources | YES | False | programs | პროგრამების კატალოგში პროგრამები საფეხურების მიხედვით ასე ნაწილდება: ბაკალავრიატი - 10 პროგრამა, მაგისტრატურა - 3 პროგრამა, ერთსაფეხურიანი - 3 პროგრამა; სულ 16.  წყარო: Higher Educ |
| bachelor_programs_list | PASS | answered_from_approved_source | program_catalog_sources | YES | False | programs | პროგრამების კატალოგის საბაკალავრო პროგრამებში შედის: სამართალი, ფსიქოლოგია, საერთაშორისო ურთიერთობები, ჟურნალისტიკა, ბიზნესის ადმინისტრირება, ტურიზმი, კომპიუტერული მეცნიერება, კომპ |
| master_programs_list | PASS | answered_from_approved_source | program_catalog_sources | YES | False | programs | პროგრამების კატალოგის სამაგისტრო პროგრამებია: სამართალი, ეროვნული და საერთაშორისო უსაფრთხოება, ბიზნესის ადმინისტრირება.  წყარო: Higher Education Program Catalog p.125 c.124, Higher |
| one_cycle_programs_list | PASS | answered_from_approved_source | program_catalog_sources | YES | False | programs | პროგრამების კატალოგის ერთსაფეხურიანი პროგრამებია: მედიცინა, მედიცინა (ინგლისურენოვანი) და სტომატოლოგია.  წყარო: Higher Education Program Catalog p.59 c.59, Higher Education Program |
| catalog_fields | PASS | answered_from_approved_source | program_catalog_sources | YES | False | programs | პროგრამების კატალოგი თითოეულ პროგრამაზე აჩვენებს ისეთ მონაცემებს, როგორიცაა: პროგრამის სახელწოდება, საფეხური, მისანიჭებელი კვალიფიკაცია, სწავლების ენა, პროგრამის მოცულობა კრედიტები |
| law_bachelor_qualification | PASS | answered_from_approved_source | program_catalog_sources | YES | False | programs | სამართლის საბაკალავრო პროგრამა ანიჭებს სამართლის ბაკალავრის კვალიფიკაციას.  წყარო: Higher Education Program Catalog p.4 c.4, Higher Education Program Catalog p.13 c.13. |
| law_master_qualification | PASS | answered_from_approved_source | program_catalog_sources | YES | False | programs | სამართლის სამაგისტრო პროგრამა ანიჭებს სამართლის მაგისტრის კვალიფიკაციას.  წყარო: Higher Education Program Catalog p.125 c.124, Higher Education Program Catalog p.133 c.132. |
| computer_science_languages | PASS | answered_from_approved_source | program_catalog_sources | YES | False | programs | პროგრამების კატალოგში კომპიუტერული მეცნიერების პროგრამა მოცემულია ქართულ და ინგლისურენოვან ვერსიებად.  წყარო: Higher Education Program Catalog p.59 c.59, Higher Education Program C |
| tuition_not_in_catalog | PASS | answered_from_approved_source | program_catalog_sources | YES | False | finance | პროგრამების კატალოგი პროგრამის სწავლის ზუსტ საფასურს არ აჩვენებს. ზუსტი თანხა არ უნდა გამოიგონოს; სწავლის საფასური უნდა გადამოწმდეს ოფიციალურ ფინანსურ წყაროში ან შესაბამის ოპერატორ |

## Source-Backed Verification Notes

- `program_count_total`: catalog source exposed; used_sources=['official_alte_8_pdf_kb_01_01_program_catalog_p059_c059', 'official_alte_8_pdf_kb_01_01_program_catalog_p062_c062', 'official_alte_8_pdf_kb_01_01_program_catalog_p075_c075', 'official_alte_8_pdf_kb_01_01_program_catalog_p078_c078', 'official_alte_8_pdf_kb_01_01_program_catalog_p091_c090', 'official_alte_8_pdf_kb_01_01_program_catalog_p110_c109', 'official_alte_8_pdf_kb_01_01_program_catalog_p177_c176', 'official_alte_8_pdf_kb_01_01_program_catalog_p003_c003', 'official_alte_8_pdf_kb_01_01_program_catalog_p004_c004', 'official_alte_8_pdf_kb_01_01_program_catalog_p014_c014']
- `program_levels_distribution`: catalog source exposed; used_sources=['official_alte_8_pdf_kb_01_01_program_catalog_p005_c005', 'official_alte_8_pdf_kb_01_01_program_catalog_p015_c015', 'official_alte_8_pdf_kb_01_01_program_catalog_p021_c021', 'official_alte_8_pdf_kb_01_01_program_catalog_p038_c038', 'official_alte_8_pdf_kb_01_01_program_catalog_p147_c146', 'official_alte_8_pdf_kb_01_01_program_catalog_p156_c155', 'official_alte_8_pdf_kb_01_01_program_catalog_p167_c166', 'official_alte_8_pdf_kb_01_01_program_catalog_p002_c002', 'official_alte_8_pdf_kb_01_01_program_catalog_p003_c003', 'official_alte_8_pdf_kb_01_01_program_catalog_p001_c001']
- `bachelor_programs_list`: catalog source exposed; used_sources=['official_alte_8_pdf_kb_01_01_program_catalog_p004_c004', 'official_alte_8_pdf_kb_01_01_program_catalog_p013_c013', 'official_alte_8_pdf_kb_01_01_program_catalog_p022_c022', 'official_alte_8_pdf_kb_01_01_program_catalog_p030_c030', 'official_alte_8_pdf_kb_01_01_program_catalog_p047_c047', 'official_alte_8_pdf_kb_01_01_program_catalog_p059_c059', 'official_alte_8_pdf_kb_01_01_program_catalog_p074_c074', 'official_alte_8_pdf_kb_01_01_program_catalog_p075_c075', 'official_alte_8_pdf_kb_01_01_program_catalog_p091_c090', 'official_alte_8_pdf_kb_01_01_program_catalog_p109_c108']
- `master_programs_list`: catalog source exposed; used_sources=['official_alte_8_pdf_kb_01_01_program_catalog_p125_c124', 'official_alte_8_pdf_kb_01_01_program_catalog_p002_c002', 'official_alte_8_pdf_kb_01_01_program_catalog_p003_c003', 'official_alte_8_pdf_kb_01_01_program_catalog_p004_c004', 'official_alte_8_pdf_kb_01_01_program_catalog_p013_c013', 'official_alte_8_pdf_kb_01_01_program_catalog_p062_c062', 'official_alte_8_pdf_kb_01_01_program_catalog_p078_c078', 'official_alte_8_pdf_kb_01_01_program_catalog_p133_c132', 'official_alte_8_pdf_kb_01_01_program_catalog_p140_c139', 'official_alte_8_pdf_kb_01_01_program_catalog_p147_c146']
- `one_cycle_programs_list`: catalog source exposed; used_sources=['official_alte_8_pdf_kb_01_01_program_catalog_p059_c059', 'official_alte_8_pdf_kb_01_01_program_catalog_p062_c062', 'official_alte_8_pdf_kb_01_01_program_catalog_p075_c075', 'official_alte_8_pdf_kb_01_01_program_catalog_p078_c078', 'official_alte_8_pdf_kb_01_01_program_catalog_p091_c090', 'official_alte_8_pdf_kb_01_01_program_catalog_p110_c109', 'official_alte_8_pdf_kb_01_01_program_catalog_p147_c146', 'official_alte_8_pdf_kb_01_01_program_catalog_p003_c003', 'official_alte_8_pdf_kb_01_01_program_catalog_p004_c004', 'official_alte_8_pdf_kb_01_01_program_catalog_p013_c013']
- `catalog_fields`: catalog source exposed; used_sources=['official_alte_8_pdf_kb_01_01_program_catalog_p001_c001', 'official_alte_8_pdf_kb_01_01_program_catalog_p013_c013', 'official_alte_8_pdf_kb_01_01_program_catalog_p003_c003', 'official_alte_8_pdf_kb_01_01_program_catalog_p004_c004', 'official_alte_8_pdf_kb_01_01_program_catalog_p005_c005', 'official_alte_8_pdf_kb_01_01_program_catalog_p006_c006', 'official_alte_8_pdf_kb_01_01_program_catalog_p015_c015', 'official_alte_8_pdf_kb_01_01_program_catalog_p022_c022', 'official_alte_8_pdf_kb_01_01_program_catalog_p030_c030', 'official_alte_8_pdf_kb_01_01_program_catalog_p039_c039']
- `law_bachelor_qualification`: catalog source exposed; used_sources=['official_alte_8_pdf_kb_01_01_program_catalog_p004_c004', 'official_alte_8_pdf_kb_01_01_program_catalog_p013_c013', 'official_alte_8_pdf_kb_01_01_program_catalog_p022_c022', 'official_alte_8_pdf_kb_01_01_program_catalog_p030_c030', 'official_alte_8_pdf_kb_01_01_program_catalog_p005_c005', 'official_alte_8_pdf_kb_01_01_program_catalog_p012_c012', 'official_alte_8_pdf_kb_01_01_program_catalog_p047_c047', 'official_alte_8_pdf_kb_01_01_program_catalog_p059_c059', 'official_alte_8_pdf_kb_01_01_program_catalog_p075_c075', 'official_alte_8_pdf_kb_01_01_program_catalog_p091_c090']
- `law_master_qualification`: catalog source exposed; used_sources=['official_alte_8_pdf_kb_01_01_program_catalog_p125_c124', 'official_alte_8_pdf_kb_01_01_program_catalog_p133_c132', 'official_alte_8_pdf_kb_01_01_program_catalog_p126_c125', 'official_alte_8_pdf_kb_01_01_program_catalog_p140_c139', 'official_alte_8_pdf_kb_01_01_program_catalog_p004_c004', 'official_alte_8_pdf_kb_01_01_program_catalog_p005_c005', 'official_alte_8_pdf_kb_01_01_program_catalog_p013_c013', 'official_alte_8_pdf_kb_01_01_program_catalog_p022_c022', 'official_alte_8_pdf_kb_01_01_program_catalog_p030_c030', 'official_alte_8_pdf_kb_01_01_program_catalog_p040_c040']
- `computer_science_languages`: catalog source exposed; used_sources=['official_alte_8_pdf_kb_01_01_program_catalog_p059_c059', 'official_alte_8_pdf_kb_01_01_program_catalog_p060_c060', 'official_alte_8_pdf_kb_01_01_program_catalog_p061_c061', 'official_alte_8_pdf_kb_01_01_program_catalog_p075_c075', 'official_alte_8_pdf_kb_01_01_program_catalog_p076_c076', 'official_alte_8_pdf_kb_01_01_program_catalog_p077_c077', 'official_alte_8_pdf_kb_01_01_program_catalog_p091_c090', 'official_alte_8_pdf_kb_01_01_program_catalog_p092_c091', 'official_alte_8_pdf_kb_01_01_program_catalog_p110_c109', 'official_alte_8_pdf_kb_01_01_program_catalog_p111_c110']
- `tuition_not_in_catalog`: catalog source exposed; used_sources=['official_alte_8_pdf_kb_01_01_program_catalog_p005_c005', 'official_alte_8_pdf_kb_01_01_program_catalog_p013_c013', 'official_alte_8_pdf_kb_01_01_program_catalog_p147_c146', 'official_alte_8_pdf_kb_01_01_program_catalog_p148_c147', 'official_alte_8_pdf_kb_01_01_program_catalog_p157_c156', 'official_alte_8_pdf_kb_01_01_program_catalog_p158_c157', 'official_alte_8_pdf_kb_01_01_program_catalog_p004_c004']

## Failures / Gaps

- None

## Safety Checks

- Real site modified: NO
- Deploy performed: YES, backend only
- Frontend/Netlify changed: NO
- DB/Secret Manager/CORS/Bridge Hub changed: NO
- Contact flow submitted: NO
- Lead/customer/task created: NO
- Public launch: NO-GO

## Final Recommendation

The program catalog source is active for the targeted production chatbot checks.
