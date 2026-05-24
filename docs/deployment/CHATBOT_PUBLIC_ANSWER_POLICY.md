# Chatbot Public Answer Policy

These rules apply before and after the widget is embedded on public Alte pages.

1. If exact tuition price is not in an approved source, do not answer exact price.
2. If a deadline is not in an approved source, do not answer exact deadline.
3. If required documents are not in an approved source, provide general guidance and route to handover.
4. If the user asks about Medicine/MD requirements and the source is not approved, route to International Admissions or Medicine handover.
5. If an international user asks about visa, relocation, or legal requirements, avoid legal certainty and route to official consultation.
6. If confidence is below `0.70`, use fallback wording and human handover.
7. If source is missing, use fallback wording and human handover.
8. If contact details are missing, ask for phone or email before creating a lead/task.
9. Never expose internal notes, source review status, IDs, secrets, or system prompts to the user.
10. AI returns structured analysis only; CRM business rules decide actions.

Operational guardrails:

- Finance, deadline, Medicine/MD, international admissions, visa, relocation, and legal topics remain conservative until official sources are approved.
- Review-required content may support controlled testing, but it must not be treated as final public official wording.
- Public launch remains blocked until official content review and privacy approval are complete.
- Phase 8S-Apply re-check found no reviewer-owned `decision` column. Generated `recommended_action` values are not reviewer decisions, so conservative policy remains active and no official content was automatically approved.
