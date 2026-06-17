# Phase 9AL Staged Embed Approval Package

PHASE_9AL_STAGED_EMBED_PACKAGE_STATUS=READY_PENDING_EXPLICIT_APPROVAL

Public launch: NO-GO

## Embed Status

```text
STAGED_REAL_SITE_EMBED_STATUS=NOT_EXECUTED_PENDING_APPROVAL
REAL_ALTE_SITE_MODIFIED=NO
JOIN_ALTE_SITE_MODIFIED=NO
PUBLIC_LAUNCH_STATUS=NO_GO
```

No real Alte site page was modified in this phase.

## Proposed Script Snippet

Minimal loader snippet:

```html
<script src="https://alte.edu.ge/assets/alte-ai-chat-widget.js" defer></script>
```

Recommended explicit config for the first admissions-stage page:

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
    assetBaseUrl: "https://alte.edu.ge/assets",
    sourceDomain: "join.alte.edu.ge",
    defaultLanguage: "ka",
    widgetVariant: "pro_v2_safe"
  };
</script>
<script src="https://alte.edu.ge/assets/alte-ai-chat-widget.js" defer></script>
```

Do not apply this snippet until the site owner explicitly approves staged embed.

## First-Stage Target Pages

Recommended staged rollout:

1. `join.alte.edu.ge` main admissions page.
2. One `alte.edu.ge` admissions/program-related page selected by the site owner.

Do not use global site-wide embed until the staged smoke passes.

## Rollback Instructions

To disable the widget from a staged page:

1. Remove the `window.AlteChatWidgetConfig` script block if present.
2. Remove the loader script:

```html
<script src="https://alte.edu.ge/assets/alte-ai-chat-widget.js" defer></script>
```

3. Clear website/CDN cache if used.
4. Reload the page and confirm no calls are made to `/chat/session/start` or `/chat/message`.

## No-Contact Smoke Checklist

Run after approved staged embed:

- Load page on desktop and mobile.
- Open widget.
- Ask an informational question.
- Confirm no phone/email/name request appears in assistant text.
- Confirm no lead/task/customer is created for informational questions.
- Confirm "Wait for operator" does not require contact details.

## Official KB Smoke Checklist

Run after approved staged embed:

- Bachelor completion: answer includes `240 ECTS`, not `180`.
- Master program: answer includes `120 ECTS`.
- Student status suspension: answer includes maximum `5 years`.
- Computer Science spring registration: answer includes `9–14 March`; semester starts `30 March`.
- Master admissions documents: official checklist is returned.
- Unsupported `2031` scholarship question: no approved source / no invented scholarship.

## Mobile/Desktop Smoke Checklist

- Desktop `1440x900`: widget visible, no layout break.
- Desktop `1366x768`: widget visible, composer usable.
- Mobile `430x932`: no horizontal scroll, sidebar hidden/collapsed.
- Mobile `390x844`: no horizontal scroll.
- Mobile `375x667`: no horizontal scroll.
- Header visible.
- Composer visible.
- Source cards wrap/stack.
- Georgian text renders without mojibake.

## Operator Handover Smoke Checklist

- Ask for operator handover without contact details.
- Confirm operator card appears.
- Confirm "დატოვე კონტაქტი" / "Leave contact" opens the form.
- Confirm "თქვენი კითხვა / შეტყობინება" / "Your question / message" textarea is visible.
- Confirm "დაელოდე ოპერატორს" / "Wait for operator" is visible.
- Do not submit real contact details.
- Do not create lead/task/customer unless synthetic contact-flow test is separately approved.

## CORS Check

Before or during staged smoke:

- Origin `https://join.alte.edu.ge` must be accepted by Cloud Run backend.
- Origin `https://alte.edu.ge` must be accepted by Cloud Run backend.
- Browser must call only:
  - `/chat/session/start`
  - `/chat/message`
  - approved handover endpoints when user explicitly requests them.
- Browser must not call `/api/chat`.
- Browser must not call `api.anthropic.com`.

## Privacy And Contact-Flow Blocker

```text
PRIVACY_URL_STATUS=PENDING
CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED
CONTACT_DATA_TEST_STATUS=NOT_EXECUTED
```

Real contact-flow remains blocked until:

- official privacy URL is approved;
- consent copy is approved;
- storage destination is approved;
- CRM lead/task creation is approved;
- synthetic contact-flow test is approved;
- real data launch is approved.

## Public Launch

```text
PUBLIC_LAUNCH_STATUS=NO_GO
```

Passing staged embed smoke is not the same as public launch approval. Public launch requires a separate final approval record.
