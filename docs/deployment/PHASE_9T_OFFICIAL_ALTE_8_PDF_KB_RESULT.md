# Phase 9T Official Alte 8 PDF Knowledge Base Result

PHASE_9T_OFFICIAL_ALTE_8_PDF_KB_STATUS=APPLIED_TO_PRODUCTION_KB_SINGLE_SMOKE_PASSED

## Scope

Prepared and applied a production-safe Knowledge Base package from 8 official Alte PDF files. The package is now present in the production Knowledge Base for chatbot retrieval. Public launch remains `NO-GO`.

## Evidence

Evidence directory:

```text
docs/knowledge_evidence/official_alte_8_pdf_kb/
```

Imported files:

- `01_program_catalog.pdf`
- `02_academic_calendar_2025_2026.pdf`
- `03_financial_support_mechanisms_2026_04_07.pdf`
- `04_state_social_grants.pdf`
- `05_bachelor_regulation.pdf`
- `06_master_regulation.pdf`
- `07_ects_credit_recognition.pdf`
- `08_study_process_regulation.pdf`

Source manifest:

```text
docs/knowledge_evidence/official_alte_8_pdf_kb/OFFICIAL_ALTE_8_PDF_SOURCE_MANIFEST.md
```

## Generated Knowledge Package

- Normalized JSONL:
  `backend/app/knowledge_seed/official_alte_8_pdf_kb/official_alte_8_pdf_kb_normalized.jsonl`
- Question bank:
  `backend/app/knowledge_seed/official_alte_8_pdf_kb/official_alte_8_pdf_supported_questions.jsonl`
- Topic taxonomy:
  `backend/app/knowledge_seed/official_alte_8_pdf_kb/topic_taxonomy.json`
- Answer policy:
  `backend/app/knowledge_seed/official_alte_8_pdf_kb/official_alte_8_pdf_answer_policy.json`
- Reviewer CSV:
  `backend/reports/official_alte_8_pdf_kb_reviewer_queue.csv`
- Behavior doc:
  `docs/knowledge_base/OFFICIAL_ALTE_8_PDF_CHATBOT_BEHAVIOR.md`
- Routing map:
  `docs/knowledge_base/OFFICIAL_ALTE_8_PDF_ROUTING_MAP.md`

## Chunk Summary

Total chunks: `273`

Chunks by document:

| File | Chunks |
| --- | ---: |
| `01_program_catalog.pdf` | 184 |
| `02_academic_calendar_2025_2026.pdf` | 5 |
| `03_financial_support_mechanisms_2026_04_07.pdf` | 5 |
| `04_state_social_grants.pdf` | 2 |
| `05_bachelor_regulation.pdf` | 20 |
| `06_master_regulation.pdf` | 17 |
| `07_ects_credit_recognition.pdf` | 15 |
| `08_study_process_regulation.pdf` | 25 |

Review-required chunks: `56`
Public-answer-allowed chunks: `183`

## Dry-Run Apply

Command:

```powershell
python -m app.scripts.apply_official_alte_8_pdf_kb --dry-run
```

Result:

- mode: `dry-run`
- would_write: `false`
- total_chunks: `273`
- review_required_count: `56`
- public_answer_allowed_count: `183`

## Safety

- Production DB modified: YES, Knowledge Base source/snippet records only
- `--apply` run: YES, with `--approve-for-chatbot`
- Migrations run: NO
- Seed production DB: NO
- Secret Manager changed: NO
- Real Alte site modified: NO
- Cloud Run deploy: NO
- CORS change: NO
- Lead/task/customer created: NO
- Public launch: NO-GO

## Production Apply Result

Detailed apply result:

```text
docs/deployment/PHASE_9T_OFFICIAL_ALTE_8_PDF_KB_APPLY_RESULT.md
```

Production Knowledge Base result:

- Sources created: `273`
- Sources updated: `0`
- Snippets created: `273`
- Snippets updated: `0`
- Production source count for this package: `273`
- Production snippet count for this package: `273`
- Production approved snippet count for this package: `273`
- Review-required metadata preserved: `56`

The initial direct local socket-style apply path failed before database writes on Windows. The completed apply used a Cloud SQL connector path and did not print credentials, tokens, hashes, or connection-string values.

Decision state:

```text
BACKEND_PRODUCTION_KB_OFFICIAL_ALTE_8_PDF_KB_APPLIED_SINGLE_SMOKE_PASSED_PENDING_BROADER_QA
```
