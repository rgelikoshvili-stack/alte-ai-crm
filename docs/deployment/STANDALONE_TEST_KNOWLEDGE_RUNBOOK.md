# Standalone Test Knowledge Runbook

## Purpose

The standalone chatbot test knowledge seed provides manually curated, safe content for testing common chatbot paths before the widget is embedded on real Alte pages.

It covers:

- general contact
- admissions
- finance/tuition safety
- international admissions
- medicine / MD routing
- deadlines
- human handover

The content is not scraped. It is manually curated and conservative. Unconfirmed content is marked as review required.

## Run Locally

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.seed_required_test_knowledge
```

The command is idempotent and prints:

- `sources_created`
- `snippets_created`
- `skipped_existing`
- `review_required_count`
- `warnings`

## Production Cloud SQL Use

Do not run this seed against production Cloud SQL unless the content has been reviewed and the project owner explicitly approves production seeding.

The seed script refuses production mode unless an approval flag is provided.

Current production seed approval status:

```text
APPROVED_AND_EXECUTED
```

Phase 8Q production execution summary:

- First run created 12 sources and 13 snippets.
- Second run created zero new records and skipped 13 existing snippets.
- Required test knowledge verification passed.
- Official content review remains required before public launch.

Required approval gate:

```text
TEST_KNOWLEDGE_SEED_APPROVAL_GATE.md
```

Required explicit phrase:

```text
Approve Phase 8Q-Execution for production test knowledge seed
```

## Review Guidance

Review seeded snippets in the knowledge admin/review workflow before treating them as final official answers.

High-risk topics such as tuition, deadlines, medicine, international admissions documents, and exact contact details should remain conservative until official source text is approved.

Official content review is required before public launch. Use:

- `OFFICIAL_CONTENT_REVIEW_REPORT.md`
- `OFFICIAL_CONTENT_REVIEW_CHECKLIST.md`
- `CHATBOT_PUBLIC_ANSWER_POLICY.md`

## Export Review Queue

To export review-required, stale, draft, finance, deadline, international, and medicine snippets for manual review:

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.export_knowledge_review_queue
```

The script is read-only. It writes:

```text
backend/reports/knowledge_review_queue.csv
```

Do not print or commit secrets. If the database URL is not configured locally, the script fails safely and asks for local configuration without printing credentials.

## Approve Or Archive After Review

After official review:

- mark approved snippets as `approved`
- set `review_required=false`
- keep finance, deadline, Medicine/MD, international admissions, visa, and relocation wording conservative until exact official sources are approved
- archive unsafe snippets through the knowledge review workflow
- do not edit production rows directly outside an approved maintenance process

## Phase 8S Apply Dry-Run

- Dry-run command: `python -m app.scripts.apply_official_content_review --dry-run`
- Explicit reviewer decisions found: 0
- Apply command run: NO
- Current status: `DRY_RUN_ONLY_PENDING_REVIEWER_DECISIONS`
- Official content review remains pending.

Phase 8T reviewer decision CSV:

- Reviewer CSV prepared: `backend/reports/knowledge_review_queue_for_review.csv`
- Reviewer-owned `decision` column added and left empty.
- `recommended_action` remains guidance only.
- Apply command was not run.
- Official content review remains pending human review.

## Archive Or Update

If a snippet is wrong or outdated:

- mark it for review
- replace it with approved official wording
- archive old content through the knowledge review workflow
- avoid editing production records directly unless a controlled maintenance process is approved

## Test After Seed

Run:

```powershell
python -m app.scripts.standalone_chatbot_api_smoke
```

For browser testing, use:

```text
widget/full-standalone-chatbot-test.html
```

Local browser calls may be blocked by production CORS. Full browser smoke should happen from an allowed Alte origin or after explicit temporary CORS test-mode approval.

## Phase 8W Study Docs Smoke

After importing the local Alte study documents into Knowledge Base, run:

```powershell
python -m app.scripts.production_knowledge_smoke_after_study_docs
```

Latest result:

- Status: `FAILED_NEEDS_REVIEW`
- Assertions: `22 passed`, `1 failed`
- Contact-flow test run: no
- Contact details sent: no
- Intentional lead/task/customer creation: no
- Review item: one tuition no-contact response returned `should_create_lead=true` without `created_lead_id` or `created_task_id`.

Do not proceed to public launch until this review item and official content review are resolved.

## Full Local Alte KB Import

The full local Alte KB has been copied, normalized, and imported into the application Knowledge Base for controlled testing:

- Evidence: `docs/knowledge_evidence/alte_full_local_kb/`
- Normalized seed: `backend/app/knowledge_seed/full_alte_local_kb/full_alte_local_kb_normalized.jsonl`
- Reviewer CSV: `backend/reports/full_alte_local_kb_reviewer_decision_queue.csv`
- Imported snippets: 645
- High-sensitivity records: 379
- Review-required records: 379

This makes the available local KB usable by the program, but it does not approve public launch. A human reviewer must fill reviewer decisions before sensitive facts can become official public answers.
