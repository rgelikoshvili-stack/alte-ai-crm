# Full Alte Local KB Import Result

Date/time: 2026-05-24

## Source Files Used

Copied into `docs/knowledge_evidence/alte_full_local_kb/`:

- `alte_knowledge_base_ka.jsonl`
- `alte_knowledge_base_index.md`
- `alte_source_urls.txt`
- `alte_university_knowledge_base.py`
- `alte_university_knowledge_base_v2.py`
- `append_kb_appendix_to_master_plan.py`
- `extract_alte_knowledge.py`
- `demo.html`
- `prototype/README.md`
- `prototype/app.js`
- `prototype/styles.css`
- `prototype/index.html`

The duplicate `alte_knowledge_base/` copy was not imported twice. The desktop Word document that contained an API key/secret was intentionally excluded and must not be committed.

## Normalization Summary

- Source pages: 123
- Source knowledge chunks: 647
- Crawl errors: 0
- Normalized records: 647
- Deduplicated records: 0
- High sensitivity count: 379
- Review required count: 379
- Normalized seed: `backend/app/knowledge_seed/full_alte_local_kb/full_alte_local_kb_normalized.jsonl`
- Reviewer CSV: `backend/reports/full_alte_local_kb_reviewer_decision_queue.csv`

## Import Summary

Dry-run:

- records_read=647
- high_sensitivity_chunks=379
- review_required_chunks=379
- warnings=0

Apply to Knowledge Base:

- records_read=647
- sources_created=240
- sources_updated=390
- chunks_created=645
- chunks_updated=0
- chunks_skipped_duplicate=2
- high_sensitivity_chunks=379
- review_required_chunks=379
- warnings=0

DB verification:

- uploaded local KB sources exist: PASS, count=240
- uploaded local KB snippets exist: PASS, count=645
- sensitive snippets remain review_required: PASS, unsafe=0

## Governance

FULL_ALTE_LOCAL_KB_IMPORT_STATUS=IMPORTED_TO_KNOWLEDGE_BASE_PENDING_HUMAN_REVIEW

This import makes the uploaded/study KB available to the application Knowledge Base, but it does not approve public launch. Sensitive facts such as tuition, deadlines, grants, document requirements, Medicine/MD, international admissions, visa/relocation/legal wording, and accreditation/recognition claims remain review-required until a human reviewer approves them.

## Safety

- Production database modified only in Knowledge Base tables.
- No CRM customers/leads/tasks/conversations/messages created.
- No contact-flow test run.
- No live website scraping/crawling run.
- No real Alte website modified.
- No gcloud commands run.
- No Cloud Run deploy.
- No Docker image pushed.
- No Google Cloud resources changed.
- No Secret Manager changes.
- No secrets printed.
- DATABASE_URL not printed.
- `.env` and `.local-secrets` not committed.
- Bridge Hub not touched.
