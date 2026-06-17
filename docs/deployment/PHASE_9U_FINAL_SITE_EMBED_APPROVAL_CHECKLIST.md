# Phase 9U Final Site Embed Approval Checklist

PHASE_9U_FINAL_SITE_EMBED_APPROVAL_STATUS=NO_GO_PENDING_EXPLICIT_FINAL_SITE_EMBED_APPROVAL

Decision state:
BACKEND_DEPLOYED_OFFICIAL_KB_BROWSER_VERIFIED_PENDING_FINAL_SITE_EMBED_APPROVAL

## Current State

- Phase 9U Netlify-origin production smoke: PASSED `8/8`
- Production backend: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Cloud Run revision verified in Phase 9U: `alte-ai-crm-backend-00027-4lk`
- Netlify test page verified in browser-origin mode: `https://nimble-croissant-2f66e8.netlify.app/join.html`
- Actual `alte.edu.ge` embed executed: NO
- Actual `join.alte.edu.ge` embed executed: NO
- Public launch: NO-GO until explicit final approval and real-domain smoke pass

## 1. Embed Snippet

Final asset to upload to an Alte-controlled static path:

```text
dist/widget/alte-ai-chat-widget.js
```

Recommended final asset URL:

```text
https://alte.edu.ge/assets/alte-ai-chat-widget.js
```

If the website team selects another Alte-controlled URL, replace only the `script src` value and record the approved final URL before embed.

For `alte.edu.ge`:

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
    sourceDomain: "alte.edu.ge",
    defaultLanguage: "ka",
    widgetVariant: "safe_pro_sidebar"
  };
</script>
<script src="https://alte.edu.ge/assets/alte-ai-chat-widget.js" defer></script>
```

For `join.alte.edu.ge`:

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
    sourceDomain: "join.alte.edu.ge",
    defaultLanguage: "en",
    widgetVariant: "safe_pro_sidebar"
  };
</script>
<script src="https://alte.edu.ge/assets/alte-ai-chat-widget.js" defer></script>
```

Required architecture checks:

- Browser calls only Cloud Run FastAPI backend.
- Allowed browser endpoints: `/chat/session/start`, `/chat/message`, public chat polling/contact endpoints only after approved flow.
- Browser must not call `api.anthropic.com`.
- Browser must not contain `ANTHROPIC_API_KEY`, Claude keys, backend secrets, DB URLs, or system prompts.

## 2. Pages To Verify

Minimum real-domain smoke pages after explicit embed approval:

- `https://alte.edu.ge/`
- `https://alte.edu.ge/ka`
- `https://alte.edu.ge/en`
- Main admissions/applicant landing page if separate from home.
- Program listing page.
- Bachelor program detail page.
- Master program detail page.
- Academic calendar or student information page if public.
- Contact/help page.
- `https://join.alte.edu.ge/` or the approved admissions landing page.

If the site owner chooses a staged rollout, start with one hidden/staging page or one low-risk public page, then expand only after smoke passes.

## 3. Desktop/Mobile Visual QA

Desktop checks:

- Widget launcher is visible but does not cover navigation, CTAs, cookie banner, forms, or footer controls.
- Expanded modal/panel fits at `1366x768`, `1440x900`, and wide desktop.
- Sidebar, message area, source cards, handover card, and composer do not overlap.
- Georgian and English text fit inside buttons, chips, cards, and composer.
- Page scroll remains usable while widget is closed and open.
- Widget z-index does not block dropdown menus or site modals unexpectedly.
- Close/minimize/reset/language controls work.
- No layout shift breaks the host page.

Mobile checks:

- Verify at `390x844`, `375x667`, and `430x932`.
- Launcher remains reachable and does not cover primary mobile nav or important form buttons.
- Expanded widget fits viewport; no horizontal scrolling.
- Keyboard opening does not hide the composer permanently.
- Sidebar/navigation collapses or remains usable without text clipping.
- Messages, source cards, and handover/contact cards are readable.
- Tap targets are large enough and not stacked on top of each other.
- Close/minimize works reliably.

Functional visual checks:

- KA/EN language toggle works.
- Sources/trust bar renders when source-backed answers return.
- Operator/handover card may appear, but typed chat must not directly ask for name/phone/email before approved contact flow.
- Loading, error, retry, and offline states are readable and do not expose internal errors.

## 4. Contact Creation Flow Approval Gate

CONTACT_CREATION_FLOW_STATUS=NOT_APPROVED_FOR_REAL_CONTACT_DATA_TEST

Contact creation is a separate approval gate from normal widget embed smoke.

Allowed before this gate:

- Ask general chatbot questions.
- Trigger operator/handover intent without sending contact details.
- Confirm the UI shows safe consent copy.
- Confirm no lead/task/customer is created without contact details and explicit consent.

Not allowed before this gate:

- Sending real phone, email, name, or personal data.
- Using real applicant contact data.
- Calling the contact submission flow with production personal data.
- Marking CRM lead/task/customer creation as launch-ready.

Separate approval required text:

```text
Approve Phase 9U contact creation flow test with synthetic contact data only.
```

When approved, use synthetic data only, record the created CRM records, verify operator CRM visibility, then delete/archive test records only through an approved cleanup process.

## 5. Rollback Plan

Immediate rollback triggers:

- Real-domain CORS failure.
- Widget fails to load or breaks page layout.
- Browser calls Anthropic directly or exposes secrets.
- Incorrect high-risk answer for academic rules, tuition, scholarships, deadlines, recognition, Medicine/Dentistry ECTS, or admissions requirements.
- Direct request for name/phone/email before approved contact flow.
- Unexpected lead/task/customer creation.
- Console errors that affect page behavior.
- Mobile layout blocks navigation, forms, or CTAs.

Rollback steps:

1. Remove the `window.AlteChatWidgetConfig` script block from the affected template/CMS block.
2. Remove the `alte-ai-chat-widget.js` script tag.
3. Restore the previous page/template version through the website deployment or CMS workflow.
4. Clear CDN/site cache if used.
5. Reopen affected pages on desktop and mobile and confirm the widget no longer loads.
6. Confirm no requests go to the Cloud Run backend from the rolled-back pages.
7. Record rollback time, owner, reason, and affected pages.
8. Keep Cloud Run backend running unless a separate backend incident requires rollback to a prior revision.

Backend rollback option, if needed:

```text
gcloud run services update-traffic alte-ai-crm-backend --region europe-west1 --to-revisions PREVIOUS_REVISION=100
```

Use backend rollback only after confirming the issue is backend-related. Do not change Secret Manager, DB schema, or CORS during rollback unless separately approved.

## 6. Launch GO/NO-GO Criteria

GO for final site embed only if all are true:

- Final written embed approval is provided.
- Final asset URL is approved and reachable.
- Website owner confirms exact pages/templates where snippet will be inserted.
- Rollback owner and smoke owner are named.
- Phase 9U official KB smoke remains passing.
- Cloud Run `/health` passes.
- CORS passes for the exact real origin being embedded.
- No direct browser Anthropic/API-key/secret exposure.
- Desktop visual QA passes.
- Mobile visual QA passes.
- Safe no-contact smoke passes on real domain.
- No lead/task/customer is created during no-contact smoke.
- Contact creation flow remains disabled unless separately approved.
- Privacy/consent copy and official privacy URL are approved by site owner.
- Public launch decision remains separate from initial embed smoke.

NO-GO if any are true:

- Final approval is missing or ambiguous.
- Real Alte site access/deployment owner is not confirmed.
- Final asset URL is unknown or outside approved control.
- CORS fails.
- Widget breaks desktop or mobile layout.
- Widget asks directly for name/phone/email before approved consent flow.
- Any high-risk answer is unsupported or contradicts official KB.
- Any unexpected lead/task/customer is created.
- Browser exposes secrets or calls Anthropic directly.
- Rollback owner is missing.
- Real-domain smoke has not been run after embed.

## Required Sign-Offs Before Actual Embed

| Approval | Owner | Status |
| --- | --- | --- |
| Final site embed approval | TBD | PENDING |
| Final asset URL approval | TBD | PENDING |
| Website deployment owner | TBD | PENDING |
| Rollback owner | TBD | PENDING |
| Smoke test owner | TBD | PENDING |
| Privacy/consent approval | TBD | PENDING |
| Contact creation flow approval | TBD | NOT_APPROVED_SEPARATE_GATE |

## Explicit Safety Statement

No real Alte website embed has been executed by this checklist. Do not upload assets or insert snippets into `alte.edu.ge` or `join.alte.edu.ge` until the user gives separate explicit approval.
