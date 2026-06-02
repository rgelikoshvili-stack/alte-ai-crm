# Phase 9AY Program Catalog Source QA Result

PHASE_9AY_PROGRAM_CATALOG_QA_STATUS=FAILED_PENDING_FIXES

Decision state: `BACKEND_DEPLOYED_FULL_KNOWLEDGE_QA_PASSED_PENDING_APPROVALS`

Public launch: `NO-GO`

## Tested Source

- File/source: `01_program_catalog.pdf` / Higher Education Program Catalog
- Topic: Programs and Admissions

## Tested URLs

- Production backend: https://alte-ai-crm-backend-226875230147.europe-west1.run.app
- Netlify chatbot: https://nimble-croissant-2f66e8.netlify.app/join.html

## Summary

- Test time UTC: 2026-06-01T17:28:40.317646+00:00
- Backend revision: `alte-ai-crm-backend-00045-dg2`
- Total questions: 10
- Passed: 0
- Failed: 10
- Operator API auth: AUTH_OK
- Contact flow submitted: NO
- Real contact data sent: NO
- Lead/customer/task created: NO
- Public launch: NO-GO

## Ten-Question Results

| Question ID | Status | answer_status | source_group | Catalog source exposed | should_handover | department | Answer snippet |
| --- | --- | --- | --- | --- | --- | --- | --- |
| program_count_total | FAIL | answered_from_approved_source | official_academic_rules | NO | False | programs | დამტკიცებული წყაროს მიხედვით (page 5; chunk 9): Official source: სასწავლო პროცესის მარეგულირებელი წესი Reference: page 5; chunk 9 Policy: answer only from this official source; han |
| program_levels_distribution | FAIL | answered_from_approved_source | official_academic_rules | NO | False | programs | დამტკიცებული წყაროს მიხედვით (page 7; chunk 14): Official source: სასწავლო პროცესის მარეგულირებელი წესი Reference: page 7; chunk 14 Policy: answer only from this official source; h |
| bachelor_programs_list | FAIL | answered_from_approved_source | official_academic_rules | NO | False | programs | დამტკიცებული წყაროს მიხედვით (page 21; chunk 47): Official source: სასწავლო პროცესის მარეგულირებელი წესი Reference: page 21; chunk 47 Policy: answer only from this official source; |
| master_programs_list | FAIL | answered_from_approved_source | official_academic_rules | NO | False | programs | დამტკიცებული წყაროს მიხედვით (page 3; მუხლი 1. ზოგადი დებულებანი): Official source: სასწავლო პროცესის მარეგულირებელი წესი Reference: page 3; მუხლი 1. ზოგადი დებულებანი Policy: answ |
| one_cycle_programs_list | FAIL | answered_from_approved_source | official_academic_rules | NO | False | programs | დამტკიცებული წყაროს მიხედვით (page 8; მუხლი 5. მობილობის ზოგადი წესი და პროცედურა): Official source: სასწავლო პროცესის მარეგულირებელი წესი Reference: page 8; მუხლი 5. მობილობის ზოგ |
| catalog_fields | FAIL | answered_from_approved_source | official_academic_rules | NO | False | programs | დამტკიცებული წყაროს მიხედვით (page 4; chunk 6): Official source: ბაკალავრიატის დებულება Reference: page 4; chunk 6 Policy: answer only from this official source; handover if the an |
| law_bachelor_qualification | FAIL | answered_from_approved_source | official_academic_rules | NO | False | programs | დამტკიცებული წყაროს მიხედვით (page 22; მუხლი 22. საგანმანათლებლო პროგრამის დასრულება და კურსდამთავრებულისათვის): Official source: სასწავლო პროცესის მარეგულირებელი წესი Reference: p |
| law_master_qualification | FAIL | answered_from_approved_source | official_academic_rules | NO | False | programs | დამტკიცებული წყაროს მიხედვით (page 3; მაგისტრატურის დებულება მუხლი 1. ზოგადი დებულებანი წინამდებარე დებულება შემუშავებულია უმაღლესი განათლების შესახებ საქართვ): Official source: მა |
| computer_science_languages | FAIL | answered_from_approved_source | official_academic_rules | NO | False | programs | დამტკიცებული წყაროს მიხედვით (page 5; chunk 8): Official source: ბაკალავრიატის დებულება Reference: page 5; chunk 8 Policy: answer only from this official source; handover if the an |
| tuition_not_in_catalog | FAIL | answered_from_approved_source | official_academic_rules | NO | False | finance | დამტკიცებული წყაროს მიხედვით (page 3; მაგისტრატურის დებულება მუხლი 1. ზოგადი დებულებანი წინამდებარე დებულება შემუშავებულია უმაღლესი განათლების შესახებ საქართვ): Official source: მა |

## Source-Backed Verification Notes

- `program_count_total`: catalog source not exposed/detected; used_sources=['official_academic_rules_full_01_p005_c009', 'official_academic_rules_full_01_p006_c012', 'official_academic_rules_full_01_p009_c020', 'official_academic_rules_full_01_p010_c022', 'official_academic_rules_full_01_p011_c025', 'official_academic_rules_full_02_p004_c006', 'official_academic_rules_full_01_p006_c013', 'official_academic_rules_full_01_p011_c024', 'official_academic_rules_full_01_p012_c027', 'official_academic_rules_full_03_p003_c004']
- `program_levels_distribution`: catalog source not exposed/detected; used_sources=['official_academic_rules_full_01_p007_c014', 'official_academic_rules_full_01_p013_c030', 'official_academic_rules_full_01_p016_c038', 'official_academic_rules_full_01_p017_c039', 'official_academic_rules_full_01_p018_c042', 'official_academic_rules_full_02_p004_c006', 'official_academic_rules_full_02_p006_c011', 'official_academic_rules_full_02_p013_c024', 'official_academic_rules_full_03_p011_c020', 'official_academic_rules_full_01_p002_c003']
- `bachelor_programs_list`: catalog source not exposed/detected; used_sources=['official_academic_rules_full_01_p021_c047', 'official_academic_rules_full_01_p022_c050', 'official_academic_rules_full_02_p008_c015', 'official_academic_rules_full_02_p009_c017', 'official_academic_rules_full_02_p016_c031', 'official_academic_rules_full_02_p007_c012', 'official_academic_rules_full_02_p001_c001', 'official_academic_rules_full_02_p003_c004', 'official_academic_rules_full_02_p004_c006', 'official_academic_rules_full_02_p005_c008']
- `master_programs_list`: catalog source not exposed/detected; used_sources=['official_academic_rules_full_01_p003_c005', 'official_academic_rules_full_01_p006_c012', 'official_academic_rules_full_01_p007_c014', 'official_academic_rules_full_01_p021_c047', 'official_academic_rules_full_03_p005_c008', 'official_academic_rules_full_03_p007_c012', 'official_academic_rules_full_03_p010_c019', 'official_academic_rules_full_01_p003_c006', 'official_academic_rules_full_01_p004_c007', 'official_academic_rules_full_01_p004_c008']
- `one_cycle_programs_list`: catalog source not exposed/detected; used_sources=['official_academic_rules_full_01_p008_c018', 'official_academic_rules_full_02_p016_c031', 'official_academic_rules_full_01_p005_c009', 'official_academic_rules_full_01_p006_c013', 'official_academic_rules_full_01_p009_c020', 'official_academic_rules_full_01_p015_c035', 'official_academic_rules_full_01_p016_c037', 'official_academic_rules_full_01_p016_c038', 'official_academic_rules_full_01_p020_c046', 'official_academic_rules_full_02_p004_c006']
- `catalog_fields`: catalog source not exposed/detected; used_sources=['official_academic_rules_full_02_p004_c006', 'official_academic_rules_full_01_p007_c014', 'official_academic_rules_full_01_p013_c030', 'official_academic_rules_full_01_p017_c039', 'official_academic_rules_full_01_p020_c046', 'official_academic_rules_full_01_p021_c047', 'official_academic_rules_full_02_p006_c011', 'official_academic_rules_full_02_p008_c014', 'official_academic_rules_full_03_p010_c018', 'official_academic_rules_full_01_p002_c003']
- `law_bachelor_qualification`: catalog source not exposed/detected; used_sources=['official_academic_rules_full_01_p022_c050', 'official_academic_rules_full_02_p009_c017', 'official_academic_rules_full_02_p016_c032', 'official_academic_rules_full_02_p007_c012', 'official_academic_rules_full_02_p005_c008', 'official_academic_rules_full_02_p007_c013', 'official_academic_rules_full_02_p008_c014', 'official_academic_rules_full_02_p008_c015', 'official_academic_rules_full_02_p009_c016', 'official_academic_rules_full_02_p010_c019']
- `law_master_qualification`: catalog source not exposed/detected; used_sources=['official_academic_rules_full_03_p003_c004', 'official_academic_rules_full_01_p022_c050', 'official_academic_rules_full_03_p003_c005', 'official_academic_rules_full_03_p005_c008', 'official_academic_rules_full_03_p008_c014', 'official_academic_rules_full_01_p006_c012', 'official_academic_rules_full_01_p018_c041', 'official_academic_rules_full_01_p022_c049', 'official_academic_rules_full_03_p002_c002', 'official_academic_rules_full_03_p004_c006']
- `computer_science_languages`: catalog source not exposed/detected; used_sources=['official_academic_rules_full_02_p005_c008', 'official_academic_rules_full_01_p006_c012', 'official_academic_rules_full_01_p006_c013', 'official_academic_rules_full_01_p007_c014', 'official_academic_rules_full_01_p009_c020', 'official_academic_rules_full_01_p011_c024', 'official_academic_rules_full_01_p022_c049', 'official_academic_rules_full_01_p022_c050', 'official_academic_rules_full_02_p004_c006', 'official_academic_rules_full_02_p006_c011']
- `tuition_not_in_catalog`: catalog source not exposed/detected; used_sources=['official_academic_rules_full_03_p003_c004', 'official_academic_rules_full_02_p007_c012', 'official_academic_rules_full_01_p007_c014', 'official_academic_rules_full_01_p008_c018', 'official_academic_rules_full_01_p013_c030', 'official_academic_rules_full_01_p021_c047', 'official_academic_rules_full_01_p022_c049', 'official_academic_rules_full_01_p023_c052', 'official_academic_rules_full_01_p024_c054', 'official_academic_rules_full_02_p003_c004']

## Failures / Gaps

- `program_count_total`: expected_terms, catalog_source, program_catalog_primary_source_group, official_academic_rules_not_primary
- `program_levels_distribution`: expected_terms, catalog_source, program_catalog_primary_source_group, official_academic_rules_not_primary
- `bachelor_programs_list`: expected_terms, catalog_source, program_catalog_primary_source_group, official_academic_rules_not_primary
- `master_programs_list`: expected_terms, catalog_source, program_catalog_primary_source_group, official_academic_rules_not_primary
- `one_cycle_programs_list`: expected_terms, catalog_source, program_catalog_primary_source_group, official_academic_rules_not_primary
- `catalog_fields`: expected_terms, catalog_source, program_catalog_primary_source_group, official_academic_rules_not_primary
- `law_bachelor_qualification`: expected_terms, catalog_source, program_catalog_primary_source_group, official_academic_rules_not_primary
- `law_master_qualification`: expected_terms, catalog_source, program_catalog_primary_source_group, official_academic_rules_not_primary
- `computer_science_languages`: expected_terms, catalog_source, program_catalog_primary_source_group, official_academic_rules_not_primary
- `tuition_not_in_catalog`: expected_terms, catalog_source, program_catalog_primary_source_group, official_academic_rules_not_primary

## Safety Checks

- Real site modified: NO
- Deploy performed: NO
- Frontend/Netlify changed: NO
- DB/Secret Manager/CORS/Bridge Hub changed: NO
- Contact flow submitted: NO
- Lead/customer/task created: NO
- Public launch: NO-GO

## Final Recommendation

Review failed catalog source-backed cases before considering launch approval.
