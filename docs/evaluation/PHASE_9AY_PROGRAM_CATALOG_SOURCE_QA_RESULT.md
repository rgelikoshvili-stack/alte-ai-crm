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

- Test time UTC: 2026-06-22T17:00:51.339505+00:00
- Backend revision: `alte-ai-crm-backend-00065-l8r`
- Backend image tag: `v1.0-phase-10h-topic-override-chat-only-cta`
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
| program_count_total | PASS | answered_from_approved_source | program_catalog_sources | YES | False | programs | პროგრამების კატალოგის მიხედვით, ალტე უნივერსიტეტში სულ 16 საგანმანათლებლო პროგრამაა: 10 საბაკალავრო, 3 სამაგისტრო და 3 ერთსაფეხურიანი პროგრამა. |
| program_levels_distribution | PASS | answered_from_approved_source | program_catalog_sources | YES | False | programs | პროგრამების კატალოგში პროგრამები საფეხურების მიხედვით ასე ნაწილდება: ბაკალავრიატი - 10 პროგრამა, მაგისტრატურა - 3 პროგრამა, ერთსაფეხურიანი - 3 პროგრამა; სულ 16. |
| bachelor_programs_list | PASS | answered_from_approved_source | program_catalog_sources | YES | False | programs | პროგრამების კატალოგის მიხედვით, ალტე უნივერსიტეტის 10 საბაკალავრო პროგრამაა: 1. სამართალი 2. ფსიქოლოგია 3. საერთაშორისო ურთიერთობები 4. ჟურნალისტიკა 5. ბიზნესის ადმინისტრირება 6. ტ |
| master_programs_list | PASS | answered_from_approved_source | program_catalog_sources | YES | False | programs | პროგრამების კატალოგის სამაგისტრო პროგრამებია: სამართალი, ეროვნული და საერთაშორისო უსაფრთხოება, ბიზნესის ადმინისტრირება. |
| one_cycle_programs_list | PASS | answered_from_approved_source | program_catalog_sources | YES | False | programs | პროგრამების კატალოგის ერთსაფეხურიანი პროგრამებია: მედიცინა, მედიცინა (ინგლისურენოვანი) და სტომატოლოგია. |
| catalog_fields | PASS | answered_from_approved_source | program_catalog_sources | YES | False | programs | პროგრამების კატალოგი თითოეულ პროგრამაზე აჩვენებს ისეთ მონაცემებს, როგორიცაა: პროგრამის სახელწოდება, საფეხური, მისანიჭებელი კვალიფიკაცია, სწავლების ენა, პროგრამის მოცულობა კრედიტები |
| law_bachelor_qualification | PASS | answered_from_approved_source | program_catalog_sources | YES | False | programs | სამართლის საბაკალავრო პროგრამა ანიჭებს სამართლის ბაკალავრის კვალიფიკაციას. |
| law_master_qualification | PASS | answered_from_approved_source | program_catalog_sources | YES | False | programs | სამართლის სამაგისტრო პროგრამა ანიჭებს სამართლის მაგისტრის კვალიფიკაციას. |
| computer_science_languages | PASS | answered_from_approved_source | program_catalog_sources | YES | False | programs | პროგრამების კატალოგში კომპიუტერული მეცნიერების პროგრამა მოცემულია ქართულ და ინგლისურენოვან ვერსიებად. |
| tuition_not_in_catalog | PASS | answered_from_approved_source | program_catalog_sources | YES | False | finance | პროგრამების კატალოგი პროგრამის სწავლის ზუსტ საფასურს არ აჩვენებს. ზუსტი თანხა არ უნდა გამოიგონოს; სწავლის საფასური უნდა გადამოწმდეს ოფიციალურ ფინანსურ წყაროში ან შესაბამის ოპერატორ |

## Source-Backed Verification Notes

- `program_count_total`: catalog source exposed; used_sources=['საგანმანათლებლო პროგრამების კატალოგი']
- `program_levels_distribution`: catalog source exposed; used_sources=['საგანმანათლებლო პროგრამების კატალოგი']
- `bachelor_programs_list`: catalog source exposed; used_sources=['საგანმანათლებლო პროგრამების კატალოგი']
- `master_programs_list`: catalog source exposed; used_sources=['საგანმანათლებლო პროგრამების კატალოგი']
- `one_cycle_programs_list`: catalog source exposed; used_sources=['საგანმანათლებლო პროგრამების კატალოგი']
- `catalog_fields`: catalog source exposed; used_sources=['საგანმანათლებლო პროგრამების კატალოგი']
- `law_bachelor_qualification`: catalog source exposed; used_sources=['საგანმანათლებლო პროგრამების კატალოგი']
- `law_master_qualification`: catalog source exposed; used_sources=['საგანმანათლებლო პროგრამების კატალოგი']
- `computer_science_languages`: catalog source exposed; used_sources=['საგანმანათლებლო პროგრამების კატალოგი']
- `tuition_not_in_catalog`: catalog source exposed; used_sources=['საგანმანათლებლო პროგრამების კატალოგი']

## Failures / Gaps

- None

## Safety Checks

- Real site modified: NO
- Deploy performed: NO
- Frontend/Netlify changed: NO
- DB/Secret Manager/CORS/Bridge Hub changed: NO
- Contact flow submitted: NO
- Lead/customer/task created: NO
- Public launch: NO-GO

## Final Recommendation

The program catalog source is active for the targeted production chatbot checks.
