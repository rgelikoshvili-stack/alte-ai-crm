# Pro v2 ZIP Exact Port Plan

PRO_V2_ZIP_EXACT_PORT_PLAN_STATUS=READY

## Decision

The previous approximation is rejected as final UI. The final widget must be ported from the ZIP source, especially `deploy/variants/pro-v2-chat.jsx`, rather than recreated approximately.

## Exact UI Behaviors To Preserve

- Floating launcher bottom-right.
- `.cw-win` collapsed floating mode: `width:min(94vw,420px)`, `height:min(92vh,680px)`, `right:22px`, `bottom:22px`, `border-radius:18px`.
- `.cw-win.expanded` centered modal: `width:min(96vw,980px)`, `height:min(92vh,720px)`, centered with `left:50%`, `top:50%`, `transform:translate(-50%,-50%)`.
- `.cw-backdrop` overlay when expanded.
- `.cw-side` sidebar width `188px`.
- `.cw-side.collapsed` width `54px`.
- Header controls: KA/EN, reset/new, settings, expand/collapse, close.
- Trust bar.
- Greeting state and quick chips.
- Sidebar departments and active item highlight.
- Source cards, operator/handover card, contact request safety card.
- Composer plus/mic/send controls.
- Enter send and Shift+Enter newline.
- Settings modal/panel.
- Mobile behavior.

## Safe Backend Replacement

Removed/replaced from production/test widget:

- `window.claude.complete`
- `/api/chat`
- direct `api.anthropic.com`
- frontend API-key usage
- frontend system prompt as source of truth
- frontend lead/task/customer creation

The browser calls only:

- `POST {apiBaseUrl}/chat/session/start`
- `POST {apiBaseUrl}/chat/message`

Backend remains the source of truth for answers, routing, knowledge, handover, and CRM safety.
