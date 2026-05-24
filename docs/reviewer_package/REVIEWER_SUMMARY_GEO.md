# Reviewer Summary - Alte AI Chatbot

## მიმდინარე backend status

- Production backend: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Current Cloud Run revision: `alte-ai-crm-backend-00004-gsn`
- Image tag: `v0.8-finance-no-contact-guard`
- Safe backend-connected widget ready, but real website embed is not done.
- Public launch is not complete.

## Knowledge Base import status

- Source pages: 123
- Knowledge chunks: 647
- Snippets created: 645
- High sensitivity records: 379
- Review-required records: 379
- Reviewer package rows: 647

Sensitive topics remain review-required until human decision:

- tuition / fees / prices
- deadlines
- required documents
- Medicine / MD
- international admissions
- visa / relocation / legal wording
- accreditation / official rules

## Production smoke status

- Finance no-contact smoke: 24/24 passed
- Broader knowledge smoke: 25/25 passed
- Contact-flow test was not run.
- Contact details were not sent.
- No intentional production lead/task/customer creation occurred.

## Reviewer task

Reviewer must fill:

```text
docs/reviewer_package/alte_kb_human_review_decisions.csv
```

Fill only:

- `decision`
- `reviewer`
- `review_date`
- `reviewer_notes`

Allowed decisions:

- `APPROVE`
- `REWRITE`
- `ARCHIVE`
- `HANDOVER_ONLY`
- `NEEDS_OFFICIAL_SOURCE`

## Still blocked

- Human reviewer decisions pending
- Official content approval pending
- Privacy/data approval pending
- Final widget asset URL pending
- Actual Alte website embed pending
- Real-domain browser smoke pending

No public launch should proceed until those items are completed.
