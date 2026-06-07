# Phase 9BC Global File Source Map And QA Framework Result

PHASE_9BC_STATUS=CODE_READY_PENDING_REVIEW  
Decision state: `BACKEND_CODE_GLOBAL_FILE_QA_FRAMEWORK_READY_PENDING_REVIEW`  
Deploy status: NOT_DEPLOYED  
Public launch: NO-GO

## Scope

Phase 9BC creates the scalable framework for file-by-file chatbot knowledge QA. It does not deploy backend code and does not modify any real site, upload, embed, database, Secret Manager, CORS, Bridge Hub, or contact-flow behavior.

## Created

- Human-readable global source map:
  `docs/knowledge_evidence/PHASE_9BC_GLOBAL_FILE_SOURCE_MAP.md`
- Machine-readable source map:
  `backend/app/data/knowledge/global_source_map.json`
- Per-file QA template:
  `docs/evaluation/PHASE_9BC_FILE_QA_TEMPLATE.md`
- Local QA runner framework:
  `backend/app/scripts/local_phase_9bc_file_by_file_qa_framework.py`
- Verifier:
  `backend/app/scripts/verify_phase_9bc_global_file_source_map.py`
- Regression tests:
  `backend/app/tests/test_phase_9bc_global_file_source_map.py`

## Source Map Summary

The Phase A source map starts with 19 primary file/source entries:

- Program Catalog
- Academic Calendar GEO
- Academic Calendar ENG
- Bachelor Regulation
- Master Regulation
- Study Process Rule
- ECTS Credit Recognition
- Exam Regulation
- Financial Support
- State/Social Grants
- Student Services
- Student Rights
- Ombudsman
- Library
- Career
- Special Needs
- AI Policy
- Plagiarism
- Ethics Code

Each JSON source entry includes:

- source identity and file name
- source group and route
- public labels in Georgian and English
- use-when and do-not-use-when boundaries
- clarification triggers and questions
- unsupported examples
- deterministic priority rules
- routability status: `source_group_status`, `routable`, and `qa_ready`

Entries are now split into two safe states:

- `configured`, `routable=true`, `qa_ready=true` when strict source group membership contains the mapped source identity.
- `missing_source_group_config`, `routable=false`, `qa_ready=false` when the file is catalogued for planning but must not be used for routing/retrieval yet.

Configured entries:

- Program Catalog
- Academic Calendar GEO
- Academic Calendar ENG
- Bachelor Regulation
- Master Regulation
- Study Process Rule
- Financial Support
- State/Social Grants
- Library
- Career

Config-gap entries:

- ECTS Credit Recognition
- Exam Regulation
- Student Services
- Student Rights
- Ombudsman
- Special Needs
- AI Policy
- Plagiarism
- Ethics Code

These config-gap sources remain catalogued, but strict source group membership must be configured before routing/retrieval or file-level QA execution treats them as ready.

## Clarification Router Summary

Added or documented conservative clarification behavior for broad/ambiguous prompts:

- `გამოცდებზე მაინტერესებს` asks whether the user means dates, exam admission rules, assessment, or retake.
- `პროგრამის კრედიტები მაინტერესებს` asks which level/program credits are meant.
- `მიღება მაინტერესებს` asks bachelor, master, international admission, documents, or admission without exams.
- `სტატუსზე კითხვა მაქვს` asks suspension, restoration, termination, or mobility.

Priority examples remain explicit:

- `ეროვნული გამოცდების გარეშე ჩარიცხვა` routes to Admissions / `admissions_rules`.
- `დასკვნით გამოცდაზე დაშვების წესი` routes to `exams_and_assessment`.
- `დასკვნითი გამოცდები როდის არის?` routes to `academic_calendar_2025_2026`.
- Generic `რამდენი კრედიტია პროგრამა?` asks clarification and does not retrieve broadly.

## Safety Controls

- No real site/upload/embed/contact-flow/DB/Secret/CORS changes were made.
- No lead/customer/task created.
- No contact flow executed.
- Public launch remains NO-GO.
- Informational QA framework records lead/customer/task creation as false.
- Unsupported examples remain conservative and do not become answerable without approved sources.
- Config-gap source-map entries are skipped/blocked by the local QA framework and verifier until strict source group membership exists.

## Verification

Local checks to run:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\python.exe -m compileall app
.\.venv\Scripts\python.exe -m pytest --basetemp .pytest_tmp_9bc_global_file_qa
.\.venv\Scripts\python.exe -m app.scripts.verify_phase_9bc_global_file_source_map
```

Result at creation time:

- compileall: PASS
- local Phase 9BC QA framework: 7/7 PASS, 9 blocked config-gap entries
- focused Phase 9BC tests: 11 passed
- pytest: 1081 passed
- Phase 9BC verifier: PASS

## Remaining Work

- Review Phase 9BC framework.
- Extend the source map from the Phase A set to all 45 primary chatbot files.
- Generate file QA sets using the template and execute each one.
- Deploy status remains `NOT_DEPLOYED`.
- Public launch remains `NO-GO`.
