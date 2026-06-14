# Phase 9AS Active Knowledge Inventory

Inventory date: 2026-05-31

Decision state before QA:
BACKEND_DEPLOYED_CHATBOT_OPERATOR_ALIGNMENT_FIX_VERIFIED_PENDING_APPROVALS

Public launch: NO-GO

## Scope

This inventory documents the knowledge groups and routing surfaces that Phase 9AS verifies against the production chatbot and Operator CRM.

The source of truth for this inventory is:

- `backend/app/data/knowledge/source_groups.json`
- `backend/app/data/knowledge/department_topic_source_map.json`
- `backend/app/data/knowledge/official_academic_rules_2025_2026.json`
- `backend/app/data/knowledge/official_academic_rules_full_chunks.json`
- `backend/app/data/knowledge/official_academic_rules_ka_en.json`
- `backend/app/data/knowledge/academic_calendar_2025_2026_structured.json`
- `backend/app/services/knowledge_routing_service.py`
- `backend/app/services/knowledge_service.py`
- `backend/app/services/chat_service.py`
- `backend/app/services/department_routing_service.py`

No production DB, Secret Manager, CORS, Bridge Hub, real site, upload, deploy, migration, seed, contact flow, lead, customer, or task creation was executed to produce this inventory.

## Knowledge Groups

### official_academic_rules

- Group label: Official academic rules
- Files/chunks used: bachelor regulation, study process regulation, master regulation; local structured files under `backend/app/data/knowledge/official_academic_rules_*`
- Topics covered: ECTS, admission rules, student status, mobility, assessment, GPA, FX/F, exams
- Answerable examples: Bachelor completion credits, Master completion credits, student status suspension, status restoration, status termination, mobility, credit recognition, final exam admission, FX/F
- Not-answerable gaps: highly specific finance, IT, library, career, or future policy claims unless another approved source exists
- Fallback department/operator: study process, programs, admissions, or operator depending route
- Official/source-backed status: official-only, exact answer allowed, stale sources not allowed

### academic_calendar_2025_2026

- Group label: Academic calendar 2025-2026
- Files/chunks used: `academic_calendar_2025_2026_structured.json`, academic calendar Georgian/English chunks in production KB
- Topics covered: registration dates, semester dates, exam dates, retakes, holidays
- Answerable examples: Computer Science spring registration, CS semester start, spring/fall registration, midterms, finals, retakes, holidays when present in the approved calendar
- Not-answerable gaps: dates outside 2025-2026 calendar or program-specific dates not present in the calendar
- Fallback department/operator: study process operator
- Official/source-backed status: official-only, exact answer allowed, stale sources not allowed

### admissions_rules

- Group label: Admissions rules
- Files/chunks used: bachelor admission chunks, master admission chunks, foreign applicant rules
- Topics covered: documents, enrollment, admission without exams, foreign applicant admission
- Answerable examples: bachelor admission documents, master admission documents, foreign education recognition, admission without national exams if in loaded official rules
- Not-answerable gaps: program-specific sales claims, unofficial pricing, unsupported international requirements
- Fallback department/operator: admissions or international admissions operator
- Official/source-backed status: official-only, exact answer allowed

### student_status_and_mobility

- Group label: Student status and mobility
- Files/chunks used: study process regulation
- Topics covered: status suspension, status restoration, status termination, mobility, internal mobility, credit recognition
- Answerable examples: maximum student status suspension period, restoration procedure, termination grounds, mobility/internal mobility, credit recognition
- Not-answerable gaps: individual student case decisions, unofficial exceptions
- Fallback department/operator: study process operator
- Official/source-backed status: official-only, exact answer allowed

### exams_and_assessment

- Group label: Exams and assessment
- Files/chunks used: study process regulation, academic calendar
- Topics covered: GPA, FX/F, final exam admission, retake/make-up exams, midterm/final calendar
- Answerable examples: GPA meaning, FX/F status, final exam admission, retake or make-up exam timing when source-backed
- Not-answerable gaps: individual grade disputes or dates absent from the approved calendar
- Fallback department/operator: study process operator
- Official/source-backed status: official-only, exact answer allowed

### finance_sources

- Group label: Finance sources
- Files/chunks used: none listed in `source_groups.json`
- Topics covered: tuition, payment schedule, scholarships
- Answerable examples: none unless production DB contains separately approved finance snippets
- Not-answerable gaps: tuition amounts, payment deadlines, scholarship promises where no approved finance source exists
- Fallback department/operator: finance operator
- Official/source-backed status: official-only, exact answer allowed only if approved source exists; otherwise no hallucination and operator fallback

### library_sources

- Group label: Library sources
- Files/chunks used: none listed in `source_groups.json`
- Topics covered: library resources, databases, books
- Answerable examples: none unless production DB contains separately approved library snippets
- Not-answerable gaps: library access rules, exact database names, book borrowing rules where no approved library source exists
- Fallback department/operator: library operator
- Official/source-backed status: official-only; no exact answer if source is missing

### it_support_sources

- Group label: IT support sources
- Files/chunks used: none listed in `source_groups.json`
- Topics covered: EMIS login, student portal, technical access
- Answerable examples: none unless production DB contains separately approved IT snippets
- Not-answerable gaps: passwords, portal troubleshooting steps, account-specific access where no approved IT source exists
- Fallback department/operator: IT operator
- Official/source-backed status: official-only; no exact answer if source is missing

### career_sources

- Group label: Career sources
- Files/chunks used: none listed in `source_groups.json`
- Topics covered: career support, internships, employment
- Answerable examples: none unless production DB contains separately approved career snippets
- Not-answerable gaps: internship listings, employer commitments, job guarantees where no approved career source exists
- Fallback department/operator: career operator
- Official/source-backed status: official-only; no exact answer if source is missing

### international_admissions_sources

- Group label: International admissions sources
- Files/chunks used: none listed in `source_groups.json`; routes may also use admissions/official academic rules when foreign applicant rules are loaded
- Topics covered: foreign applicants, foreign education recognition, English-language requirements, international admission
- Answerable examples: foreign applicant admission and recognition if available through approved admissions/academic rules
- Not-answerable gaps: visa promises, relocation, unsupported country-specific claims
- Fallback department/operator: international admissions operator
- Official/source-backed status: official-only, exact answer allowed only if approved source exists

## Department And Topic Routing

Expected public chatbot departments:

- მიღება -> Admissions
- პროგრამები -> Programs
- დაფინანსება -> Finance
- საერთ. სტუდენტები -> International Admissions
- მედიცინა / MD -> Medicine / MD
- ბიბლიოთეკა -> Library
- კარიერა -> Career
- IT დახმარება -> IT Support
- ცოცხალი ოპერატორი -> Human Operator

Important Phase 9AR alignment:

- Source-backed informational answers must not set `should_handover=true` or `human_handover=true`.
- Unsupported or no-approved-source fallback may set handover and offer the correct operator.
- Explicit operator requests and wait-for-operator must set handover/waiting state.
- Bachelor/Master ECTS should route to Programs or Admissions, not internal Study Process, when used as public program-credit questions.

## Known Knowledge Gaps To Verify

- Finance sources are configured but have no listed source files.
- Library sources are configured but have no listed source files.
- IT support sources are configured but have no listed source files.
- Career sources are configured but have no listed source files.
- International admissions may depend on admissions/academic rules unless separately approved international snippets exist in production.
- Contact-flow approval remains NOT_APPROVED, so contact submission is not part of this QA.

## Safety

- Public launch remains NO-GO.
- CONTACT_FLOW_EXECUTED=NO
- REAL_CONTACT_DATA_SENT=NO
- LEAD_TASK_CUSTOMER_CREATED=NO
- REAL_ALTE_SITE_MODIFIED=NO
- ASSET_UPLOAD_EXECUTED=NO
- REAL_SITE_EMBED_EXECUTED=NO
