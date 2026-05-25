# Official Content Review Report

## Purpose

This report gates chatbot public launch. It defines which knowledge content may be used for public chatbot answers, which content requires official review, and which topics must route to a human or official confirmation instead of producing invented facts.

The chatbot must not invent tuition prices, admission deadlines, official document requirements, Medicine/MD requirements, international student requirements, or legal/visa/relocation requirements.

## Current Seeded Knowledge Summary

- Production test knowledge seeded in Phase 8Q.
- `sources_created=12`
- `snippets_created=13`
- `review_required_count=11`
- Second run idempotency confirmed: zero new sources/snippets, 13 existing snippets skipped.
- Verification passed for:
  - general contact
  - admissions
  - finance
  - international admissions
  - medicine/MD
  - deadlines

## Review Categories

| category | current status | public answer allowed? | exact facts allowed? | handover required? | reviewer/owner | notes |
| --- | --- | --- | --- | --- | --- | --- |
| general_contact | REVIEW_REQUIRED | Only after official contact source confirmed | No | Yes until approved | PENDING | Do not invent address, phone, or email. |
| admissions_general | REVIEW_REQUIRED | Conservative overview only after review | No | Yes for program-specific details | PENDING | Route specific admissions cases to Admissions. |
| bachelor admissions | REVIEW_REQUIRED | Conservative overview only after review | No | Yes for requirements/deadlines | PENDING | Exact steps and requirements need official source. |
| master admissions | REVIEW_REQUIRED | Conservative overview only after review | No | Yes for requirements/deadlines | PENDING | Exact steps and requirements need official source. |
| required documents | REVIEW_REQUIRED | General guidance only | No | Yes | PENDING | Exact document lists must come from approved official source. |
| finance/tuition | HANDOVER_OR_OFFICIAL_SOURCE_ONLY | Only if approved current source exists | No unless source-approved | Yes when source missing | PENDING | Never invent exact tuition, fee, payment, or scholarship values. |
| deadlines/academic calendar | HANDOVER_OR_OFFICIAL_SOURCE_ONLY | Only if approved current source exists | No unless source-approved | Yes when source missing | PENDING | Never invent application or admission dates. |
| international admissions | REVIEW_REQUIRED | Conservative overview only after review | No | Yes | PENDING | Exact requirements depend on applicant and program. |
| medicine/MD | REVIEW_REQUIRED | Conservative routing only after review | No | Yes | PENDING | Route Medicine/MD questions to International Admissions/Medicine owner. |
| relocation/visa | HANDOVER_ONLY_UNTIL_APPROVED | No legal certainty | No | Yes | PENDING | Avoid legal, visa, or relocation certainty. |
| human handover | APPROVED_FOR_CONTROLLED_TESTING | Yes | No | Yes when requested or confidence/source is insufficient | PENDING | Confirm wording and SLA before public launch. |
| privacy/consent | PRIVACY_APPROVAL_REQUIRED | Not until privacy owner approves | No | Yes | PENDING | Consent text and data-use wording require privacy approval. |

## Public Launch Status

```text
OFFICIAL_CONTENT_REVIEW_STATUS=PENDING

## Phase 9A Reviewer Package

The final human reviewer package has been created from the full imported Alte KB.

- Package folder: `docs/reviewer_package/`
- Full decision CSV: `docs/reviewer_package/alte_kb_human_review_decisions.csv`
- Compact CSV: `docs/reviewer_package/alte_kb_human_review_compact.csv`
- Rows: 647
- High sensitivity: 379
- Review-required: 379
- Human decisions filled: 0
- Status: `PENDING_HUMAN_DECISIONS`

Official content review remains pending until a reviewer fills decisions and a later apply phase is explicitly approved.

## Full Local KB Import Evidence

The full local Alte KB package was imported into the application Knowledge Base for controlled testing and review:

- Evidence folder: `docs/knowledge_evidence/alte_full_local_kb/`
- Normalized seed: `backend/app/knowledge_seed/full_alte_local_kb/full_alte_local_kb_normalized.jsonl`
- Reviewer queue: `backend/reports/full_alte_local_kb_reviewer_decision_queue.csv`
- Source pages: 123
- Knowledge chunks: 647
- High-sensitivity records: 379
- Review-required records: 379

This import does not approve public launch. Tuition, deadlines, grants, official requirements, required documents, Medicine/MD, international admissions, visa/relocation/legal, and accreditation/recognition content must remain conservative until human reviewer decisions are applied.
```

## Review Queue Export

- Export command prepared: `python -m app.scripts.export_knowledge_review_queue`
- Latest export generated: `backend/reports/knowledge_review_queue.csv`
- Rows exported: 26
- Export type: read-only knowledge review queue
- The export contains truncated content previews for reviewer workflow and no secrets.

## Phase 8S Apply Status

- Review apply dry-run completed.
- Explicit reviewer decisions present: NO
- Reviewer `decision` column present: NO
- Generated `recommended_action` values were not treated as reviewer decisions.
- `--apply` run: NO
- Reason: the review queue does not contain a reviewer-owned `decision` column.
- Apply status: `OFFICIAL_CONTENT_REVIEW_APPLY_STATUS=DRY_RUN_ONLY_PENDING_REVIEWER_DECISIONS`
- Official approval is still pending.

## Phase 8T Reviewer CSV Status

- Reviewer decision CSV prepared: `backend/reports/knowledge_review_queue_for_review.csv`
- Rows prepared: 26
- Reviewer `decision` column added: YES
- Decision cells prefilled: NO
- Generated `recommended_action` values copied into `decision`: NO
- `--apply` run: NO
- Official approval remains pending human review.
- Decision state: `BACKEND_DEPLOYED_REVIEWER_DECISION_CSV_READY_PENDING_HUMAN_REVIEW`

## Phase 8W Production Knowledge Smoke Status

- Study docs Knowledge Base import completed before smoke.
- Production endpoint checks: `/health`, `/version`, `/diagnostics/ai` all `200`.
- Smoke status: `PRODUCTION_KNOWLEDGE_SMOKE_AFTER_STUDY_DOCS_STATUS=FAILED_NEEDS_REVIEW`
- Contact-flow test run: NO
- Contact details sent: NO
- Intentional lead/task/customer creation: NO
- Sensitive tuition/deadline responses remained conservative on exact facts.
- Review item: one tuition no-contact response returned `should_create_lead=true` while `created_lead_id=null` and `created_task_id=null`.
- Official approval remains pending.

## Required Approval Phrase

Public content may be marked approved only after the user says:

```text
Approve official content review for public chatbot launch
```

## Phase 9F Conservative Decision Draft

Phase 9F prepared a conservative official-content decision draft:

- Source reviewer file: `docs/reviewer_package/alte_kb_human_review_decisions.csv`
- Conservative decision file: `docs/reviewer_package/alte_kb_conservative_decisions_for_approval.csv`
- Total rows: 647
- `APPROVE`: 67
- `HANDOVER_ONLY`: 10
- `NEEDS_OFFICIAL_SOURCE`: 570
- High sensitivity rows: 379
- Sensitive blocked count: 580
- Public launch allowed count: 67

Official human approval exists: NO.

Production DB modified: NO.

Public launch approved: NO.

Decision state:

```text
BACKEND_DEPLOYED_CONTENT_DECISIONS_PREPARED_PENDING_HUMAN_APPROVAL
```

## Phase 9G-H Embed Readiness Update

Privacy/data approval package and embed package were prepared, but official content approval is still pending.

- Privacy approval: pending
- Official content approval: pending
- Final asset URL: pending
- Actual site embed: not executed
- Real-domain browser smoke: not executed

Decision state:

```text
BACKEND_DEPLOYED_PRIVACY_AND_EMBED_PACKAGE_READY_PENDING_FINAL_APPROVALS
```

## Phase 9J Content Approval Gate

Official content approval remains pending at the final pre-site-embed gate.

- Conservative CSV exists.
- Human approval not recorded.
- `apply --apply` not run.
- Public launch not approved.

Decision state:

```text
BACKEND_DEPLOYED_FINAL_PRE_EMBED_GATE_READY_NO_GO_PENDING_APPROVALS
```
