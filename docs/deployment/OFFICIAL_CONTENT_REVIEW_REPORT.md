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
- `--apply` run: NO
- Reason: no explicit reviewer decisions were present in the review queue.
- Apply status: `OFFICIAL_CONTENT_REVIEW_APPLY_STATUS=DRY_RUN_ONLY_PENDING_REVIEWER_DECISIONS`
- Official approval is still pending.

## Required Approval Phrase

Public content may be marked approved only after the user says:

```text
Approve official content review for public chatbot launch
```
