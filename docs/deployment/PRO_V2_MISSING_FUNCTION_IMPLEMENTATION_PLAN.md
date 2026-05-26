# Pro v2 Missing Function Implementation Plan

PRO_V2_MISSING_FUNCTION_IMPLEMENTATION_PLAN_STATUS=READY

## Phase 9R-A — Exact Pro v2 UI Rebuild

- Rebuild modal layout to Pro v2 proportions.
- Add sidebar, expanded modal, header controls, composer, chips, cards, and responsive behavior.
- Replace small embedded final UI with Pro v2 safe modal.

## Phase 9R-B — Safe Backend Integration

- Keep `/chat/session/start` and `/chat/message` only.
- Preserve `channel=website_chat`.
- Send `selected_department`, `selected_topic`, `source_domain`, `language`, and `widget_variant=pro_v2_safe`.
- Render backend source cards, handover state, and fallback/error states.

## Phase 9R-C — Missing Safe Frontend Interactions

- Close/reopen.
- Expand/fullscreen.
- Sidebar collapse.
- Settings panel.
- Reset/new chat.
- Enter/Shift+Enter keyboard behavior.
- Language-specific placeholder and quick chips.
- Backend unavailable UI.

## Phase 9R-D — Restricted Features

- Voice input/transcription.
- File attachment/upload.
- Contact form submission.
- Live operator backend workflow.
- Server-side settings persistence.

These are documented separately and require backend support or approval before public use.
