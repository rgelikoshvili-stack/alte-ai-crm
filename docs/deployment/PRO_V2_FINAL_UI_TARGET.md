# Pro v2 Final UI Target

CURRENT_SMALL_WIDGET_STATUS=REJECTED_AS_FINAL_UI
UPLOADED_PRO_V2_STATUS=APPROVED_FINAL_UI_TARGET

## Decision

The current smaller embedded widget is not acceptable as the final UI. The final chatbot must be rebuilt to match the uploaded Pro v2 standalone chatbot as closely as possible.

## Ownership Boundary

- Uploaded Pro v2 controls the visual and interaction target.
- Alte backend controls answers, routing, CRM safety, knowledge retrieval, handover status, and content policy.
- Unsafe standalone browser AI logic is not copied into production.

## Target Requirements

- Large modal/window, not a small inline panel.
- Sidebar with department navigation.
- Header controls for KA/EN, reset, settings, expand, close.
- Trust/status bar.
- Welcome state, recommended card, quick chips.
- Source cards, handover card, contact request card.
- Composer with plus/voice controls as disabled/approval-gated where unsupported.
- Mobile responsive behavior.
