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
