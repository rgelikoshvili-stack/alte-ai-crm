# Pro v2 Backend Gaps Requiring Approval

PRO_V2_BACKEND_GAPS_STATUS=DOCUMENTED_PENDING_APPROVAL

The following Pro v2 standalone functions are not faked in the safe widget:

- Real live operator queue and operator dashboard integration.
- Real contact form submission that creates CRM lead/task/customer.
- File upload and document analysis.
- Voice input/transcription.
- Browser notification callback workflow.
- Server-side settings persistence.
- Theme preference persistence beyond local UI state.
- Regenerate/copy/thumb feedback analytics.

## Current Safe Handling

- Attachment and voice controls are shown as disabled/approval-gated.
- Contact request card is rendered as a no-contact safety notice during smoke tests.
- Handover is displayed only from backend response flags or explicit safe operator entry.
- Sources are rendered only from backend response `used_sources`.
- Frontend never creates CRM records.
