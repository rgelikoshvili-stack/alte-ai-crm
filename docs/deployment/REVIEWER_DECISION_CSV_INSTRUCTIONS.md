# Reviewer Decision CSV Instructions

## File To Review

Open:

```text
backend/reports/knowledge_review_queue_for_review.csv
```

Do not edit these source columns:

- `source_key`
- `title`
- `category`
- `status`
- `recommended_action`

Fill these reviewer-owned columns:

- `decision`
- `reviewer`
- `review_date`
- `reviewer_notes`

Allowed `decision` values:

- `APPROVE`
- `REWRITE`
- `ARCHIVE`
- `HANDOVER_ONLY`
- `NEEDS_OFFICIAL_SOURCE`

Decision meanings:

- `APPROVE`: safe for public chatbot answer.
- `REWRITE`: content needs wording changes before public use.
- `ARCHIVE`: remove or disable from chatbot use.
- `HANDOVER_ONLY`: chatbot should route to a human, not answer directly.
- `NEEDS_OFFICIAL_SOURCE`: requires official source before public answer.

## Review Warnings

- Do not approve tuition or fee answers without an official source.
- Do not approve deadlines without an official source.
- Do not approve Medicine/MD requirements without an official source.
- Do not approve international admissions requirements without an official source.
- Visa, relocation, and legal-sensitive wording should be `HANDOVER_ONLY` unless official wording exists.
- If unsure, choose `NEEDS_OFFICIAL_SOURCE`.

## Next Step

After the reviewer fills `decision`, `reviewer`, `review_date`, and notes where needed, run Phase 8S-Apply again.

Do not treat `recommended_action` as a reviewer decision. It is only machine-generated guidance.
