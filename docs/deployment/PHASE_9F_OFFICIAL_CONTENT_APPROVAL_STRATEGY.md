# Phase 9F Official Content Approval Strategy

## Current Backend And Widget Status

- Production backend is deployed and healthy at `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`.
- Current Cloud Run image: `v0.9-sidebar-ambiguous-routing-fix`.
- Department-aware routing smoke passed in production: 28/28.
- Finance no-contact smoke passed in production: 24/24.
- Broader knowledge smoke final run passed in production: 25/25.
- Safe Pro sidebar widget is backend-connected and does not call Anthropic directly from the browser.

## Why Approval Is Required

The imported Alte Knowledge Base contains official university facts that can affect admissions, finance, legal, and student decisions. Public launch requires human/official review before the bot can answer exact sensitive facts.

The chatbot must not invent:

- tuition prices
- admission deadlines
- grants or scholarships
- official document requirements
- Medicine/MD requirements
- international admissions requirements
- visa, relocation, or legal requirements

If source is missing, content is review-required, confidence is low, or the topic is sensitive, the bot must answer conservatively and route the student to the correct department/operator.

## Conservative Approval Policy

- Low-risk general official content may be approve-candidate only when it is official-source-backed and non-sensitive.
- Sensitive facts remain restricted unless explicit human reviewer approval exists.
- Conservative system-prepared decisions are not official human approval.
- Public launch remains blocked until reviewer decisions, official content approval, privacy/data approval, final widget asset URL, actual site embed, and real-domain smoke are complete.

## Conservative Defaults

- `finance_tuition`: `NEEDS_OFFICIAL_SOURCE` or `HANDOVER_ONLY`
- `deadlines_calendar`: `NEEDS_OFFICIAL_SOURCE` or `HANDOVER_ONLY`
- `required_documents`: `NEEDS_OFFICIAL_SOURCE`
- `medicine_md`: `NEEDS_OFFICIAL_SOURCE` or `HANDOVER_ONLY`
- `international_admissions`: `NEEDS_OFFICIAL_SOURCE`
- `visa_relocation` / legal: `HANDOVER_ONLY`
- scholarship / grant / payment: `NEEDS_OFFICIAL_SOURCE` or `HANDOVER_ONLY`
- `general_contact` / about / FAQ: `APPROVE_CANDIDATE` only if official source URL exists and sensitivity is LOW
- `student_services`: `APPROVE_CANDIDATE` if non-sensitive
- IT support: `APPROVE_CANDIDATE` if generic and non-sensitive

## Public Launch Status

NOT_READY_UNTIL_APPROVAL_AND_SITE_SMOKE
