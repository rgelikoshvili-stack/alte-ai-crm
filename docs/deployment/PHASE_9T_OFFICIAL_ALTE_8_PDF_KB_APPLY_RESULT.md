# Phase 9T Official Alte 8 PDF KB Apply Result

PHASE_9T_OFFICIAL_ALTE_8_PDF_KB_APPLY_STATUS=APPLIED_TO_PRODUCTION_KB_SINGLE_SMOKE_PASSED

## Scope

Applied the prepared `official_alte_8_pdf_kb` package to the production Knowledge Base after explicit approval. The write was limited to Knowledge Base source/snippet records for the temporary chatbot knowledge package.

## Imported Official Files

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

## Production Apply Summary

- Total chunks read: `273`
- Review-required chunks: `56`
- Public-answer-allowed chunks: `183`
- Sources created: `273`
- Sources updated: `0`
- Snippets created: `273`
- Snippets updated: `0`
- Approved for chatbot retrieval: `273`
- Production source count for this package: `273`
- Production snippet count for this package: `273`
- Production approved snippet count for this package: `273`

Review-required metadata remains preserved on sensitive chunks. Approval for chatbot retrieval means the retriever can use these official chunks, while answer policy still requires conservative source-grounded answers and handover when support is insufficient.

## Safety

- Production DB modified: YES, Knowledge Base source/snippet records only
- Migration run: NO
- Seed run: NO
- Schema changed: NO
- Secret Manager changed: NO
- Cloud Run deployed: NO
- CORS changed: NO
- Real `alte.edu.ge` or `join.alte.edu.ge` changed: NO
- Public chatbot UI changed: NO
- Lead/task/customer created: NO
- Contact-flow test run: NO
- Credentials, tokens, hashes, or connection-string values printed: NO
- Public launch: NO-GO

## Production Chat Smoke

Single-question production smoke after import:

- `/chat/session/start`: `200`
- `/chat/message`: `200`
- Question topic: bachelor ECTS
- Answer present: YES
- Answer source status: `answered_from_approved_source`
- Used sources count: `10`
- Lead created: NO
- Task created: NO

A broader multi-question smoke started successfully at session creation but one message request timed out. This is recorded as a latency/retry follow-up, not as a Knowledge Base apply failure, because the production DB package counts and the single-answer source-grounded smoke passed.

## Notes

The first local apply path failed before any database write because the Windows async driver path could not use the expected local socket style. The successful apply used the Cloud SQL connector path with credentials handled in memory and sanitized output only.

## Decision State

```text
BACKEND_PRODUCTION_KB_OFFICIAL_ALTE_8_PDF_KB_APPLIED_SINGLE_SMOKE_PASSED_PENDING_BROADER_QA
```
