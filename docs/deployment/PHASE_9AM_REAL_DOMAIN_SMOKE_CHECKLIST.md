# Phase 9AM Real-Domain Smoke Checklist

PHASE_9AM_REAL_DOMAIN_SMOKE_CHECKLIST_STATUS=READY_PENDING_APPROVED_UPLOAD_AND_EMBED

Public launch: NO-GO

Run this checklist only after:

- final upload bundle is approved and uploaded;
- staged embed is explicitly approved and applied;
- privacy/contact-flow gates are resolved or contact collection remains blocked;
- smoke owner and rollback owner are named.

## Target Pages

First-stage pages:

1. `join.alte.edu.ge` main admissions page.
2. One `alte.edu.ge` admissions/program-related page selected by the site owner.

No global site-wide embed until staged smoke passes.

## Asset Loading

- `https://alte.edu.ge/assets/alte-ai-chat-widget.js` returns `200`.
- `https://alte.edu.ge/assets/alte-ai-chat-widget.html` returns `200`.
- `https://alte.edu.ge/assets/variants/pro-v2-chat.jsx` returns `200`.
- `https://alte.edu.ge/assets/variants/pro-v2-icons.jsx` returns `200`.
- `https://alte.edu.ge/assets/variants/pro-v2-modals.jsx` returns `200`.
- `https://alte.edu.ge/assets/variants/pro-v2-page.jsx` returns `200`.
- `https://alte.edu.ge/assets/variants/pro-v2-strings.jsx` returns `200`.
- `https://alte.edu.ge/assets/variants/tweaks-panel.jsx` returns `200`.
- Served files preserve UTF-8 and Georgian text has no mojibake.

## Browser/API Smoke

- Widget launcher appears.
- Widget opens.
- No browser console CORS errors.
- `/chat/session/start` returns success.
- `/chat/message` returns success.
- Browser does not call `/api/chat`.
- Browser does not call `api.anthropic.com`.
- Browser does not expose API keys.

## Visual Smoke

- Desktop `1440x900`: widget visible, header visible, composer visible.
- Desktop `1366x768`: widget usable.
- Mobile `430x932`: no horizontal scroll, sidebar hidden/collapsed.
- Mobile `390x844`: no horizontal scroll.
- Mobile `375x667`: no horizontal scroll.
- Source cards wrap/stack safely.
- Georgian text displays correctly.

## Official KB Smoke

- Bachelor completion question returns `240 ECTS`, not `180`.
- Master program question returns `120 ECTS`.
- Student status suspension returns maximum `5 years`.
- Computer Science spring registration returns `9–14 March`; semester starts `30 March`.
- Master admissions documents match the official checklist.
- Broad question `სწავლა მაინტერესებს` asks a clarification question.
- Unsupported `2031` scholarship question does not hallucinate and returns no approved source / operator handover.

## Contact And Operator Smoke

- Contact form includes `თქვენი კითხვა / შეტყობინება` / `Your question / message`.
- `დაელოდე ოპერატორს` / `Wait for operator` button is visible.
- Assistant answer does not directly ask user to type phone/email/name in chat.
- No lead/customer/task is created for informational questions.
- No lead/customer/task is created unless contact-flow approval explicitly allows synthetic testing.
- Operator handover routes to the inferred/correct department.

## CORS Checks

- `https://join.alte.edu.ge` origin is accepted.
- `https://alte.edu.ge` origin is accepted.
- Preflight and POST checks pass for:
  - `/chat/session/start`
  - `/chat/message`

## Rollback Check

- Confirm rollback instructions are understood and executable.
- Confirm removing the config script and loader script disables the widget.
- Confirm backend remains untouched during rollback.

## Gate

```text
REAL_DOMAIN_SMOKE_STATUS=NOT_EXECUTED_PENDING_APPROVED_EMBED
PUBLIC_LAUNCH_STATUS=NO_GO
```

Passing this smoke later does not automatically approve public launch.
