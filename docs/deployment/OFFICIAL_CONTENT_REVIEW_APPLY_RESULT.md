# Official Content Review Apply Result

## Run Metadata

- Date/time: `2026-05-24 14:46:45 +04:00`
- CSV used: `backend/reports/knowledge_review_queue.csv`
- Dry-run command: `python -m app.scripts.apply_official_content_review --dry-run`
- Apply command: not run

## Dry-Run Summary

- `mode`: `dry-run`
- `total_rows`: 26
- `valid_decisions`: 0
- `missing_decisions`: 26
- `approve_count`: 0
- `rewrite_count`: 0
- `archive_count`: 0
- `handover_only_count`: 3
- `needs_official_source_count`: 6
- `applied_count`: 0
- `warnings`: Reviewer decisions missing; `--apply` should not be run automatically.

## Apply Status

- `--apply` was run: NO
- Reason: no explicit reviewer decisions were present in the review queue.
- Current official review status: `OFFICIAL_CONTENT_REVIEW_STATUS=PENDING`
- Public launch status: BLOCKED

```text
OFFICIAL_CONTENT_REVIEW_APPLY_STATUS=DRY_RUN_ONLY_PENDING_REVIEWER_DECISIONS
```

## Verification Result

- Sensitive categories are not fully approved without explicit review: PASS
- Sensitive seeded content remains pending/review-required: PASS
- Sensitive fully approved count: 0
- Sensitive pending review count: 7

## Remaining Review Items

- Official contact information
- Bachelor admissions process
- Master admissions process
- Required documents
- Finance/tuition policy
- Deadlines/academic calendar
- International admissions requirements
- Medicine/MD requirements
- Relocation/visa wording
- Privacy/consent wording
- Handover wording

## Safety Confirmation

- No secrets printed.
- No CRM leads/tasks/customers created.
- No website modified.
- No Cloud Run deployment.
- No database records were changed because apply was not run.
