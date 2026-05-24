# Official Content Review Apply Plan

## Source

- Source CSV: `backend/reports/knowledge_review_queue.csv`
- Reviewer decision column found: NO
- Reviewer decisions found: NO

The current CSV contains generated `recommended_action` values only. It does not contain reviewer-owned decisions, reviewer names, or approval notes.

## Conservative Default Policy

Because no explicit reviewer decisions are present, do not approve all content automatically.

Conservative defaults:

- `finance/tuition`: keep as `HANDOVER_ONLY` or `NEEDS_OFFICIAL_SOURCE`
- `deadlines`: keep as `HANDOVER_ONLY` or `NEEDS_OFFICIAL_SOURCE`
- `required documents`: keep `REVIEW_REQUIRED` / `NEEDS_OFFICIAL_SOURCE`
- `international admissions`: keep `REVIEW_REQUIRED`
- `medicine/MD`: keep `REVIEW_REQUIRED`
- `visa/relocation/legal`: keep `HANDOVER_ONLY`
- `general contact/admissions overview`: keep `REVIEW_REQUIRED` unless explicitly safe and source-approved

## Categories To Keep Review Required

- general contact without official source
- admissions general
- bachelor admissions
- master admissions
- required documents
- international admissions
- medicine/MD
- privacy/consent wording

## Categories To Mark Handover Only

- finance/tuition without approved current source
- deadlines without approved current source
- visa/relocation/legal topics
- medicine/MD requirements without official review
- international admissions requirements without official review

## Categories Requiring Explicit Reviewer Approval

- tuition prices
- admission deadlines
- official document requirements
- Medicine/MD requirements
- international student requirements
- legal/visa/relocation requirements
- final privacy/consent wording

## Safety Rules

- No invented tuition.
- No invented deadlines.
- No invented document requirements.
- Medicine/International requires official review.
- Visa/relocation uses handover unless approved.
- Do not mark sensitive or exact-fact content fully approved from generated recommendations.

## Expected Output

- `applied_count`: 0 unless explicit reviewer decisions exist and `--apply` is used.
- `kept_review_required_count`: count of rows with missing reviewer decisions.
- `handover_only_count`: generated or reviewer handover-only rows.
- `archived_count`: explicit reviewer archive decisions only.
- `needs_official_source_count`: generated or reviewer official-source-needed rows.
