# Pro v2 Uploaded Widget Audit

PRO_V2_UPLOADED_WIDGET_AUDIT_STATUS=COMPLETED_REFERENCE_ONLY

## Artifact

The uploaded file is a bundled standalone HTML that requires JavaScript to render. It contains a bundler manifest/template and embedded compressed assets.

## Visual Structure

- Floating chat window with launcher and expanded modal state.
- Compact window is about `420px` wide and `680px` tall.
- Expanded modal is about `980px` wide and `720px` tall, centered with a backdrop.
- Left sidebar appears in expanded mode.
- Right chat panel contains header, trust/status bar, messages, chips, composer, and footer hint.
- Mobile behavior hides/reflows the sidebar and keeps the chat viewport-aware.

## Controls And Interactions

- KA/EN language switch.
- Reset/new chat.
- Settings panel.
- Expand/collapse modal.
- Close/reopen via launcher.
- Sidebar collapse.
- Department navigation and active department state.
- Quick chips and recommended card.
- Text composer with Enter to send and Shift+Enter newline.
- Plus/attachment and voice buttons in the composer.
- Typing/loading indicator.
- Source cards.
- Operator/handover card.
- Contact request card.
- Settings toggles for sources/notifications/theme/clear in the standalone prototype.

## Visual System

- Deep Alte teal active controls.
- Cream/paper backgrounds.
- Soft borders and rounded corners.
- Subtle large shadows.
- Georgian/English typography using Noto Sans Georgian, Inter, and Fraunces-style headings.
- Orange accent for handover/operator states.

## Security And Product Scan

- Direct AI/provider browser logic: present through standalone model-completion calls.
- Browser API key literal: not found.
- Database URL literal: not found.
- Hardcoded system prompt: present.
- Hardcoded tuition/deadline/MD/international facts: present in prompt/sample logic.
- Frontend contact/lead prototype: present.
- File/voice UI: present as a prototype.

## Production Decision

The uploaded Pro v2 file is the visual and functional source-of-truth, but unsafe standalone logic is replaced by safe backend calls. Browser production/test widget may only call:

```text
/chat/session/start
/chat/message
```
