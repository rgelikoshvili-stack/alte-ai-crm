# Phase 9AN Owner Handoff: Asset Upload And Staged Embed

This document is for the Alte site owner or non-developer approval owner. It explains what is ready, what must still be approved, which upload artifact to use, how to embed the widget on staged pages, how to smoke test, and how to rollback.

No asset upload, real-site embed, deployment, database change, Secret Manager change, CORS change, or contact creation flow has been executed for this handoff.

## 1. Current Readiness Summary

Backend status:

- Production backend is deployed and working.
- Backend URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Official KB/routing behavior is ready for owner review.

Widget bundle status:

- Final upload bundle is ready.
- Verified ZIP path: `dist/final_alte_widget_upload.zip`
- The bundle includes the JavaScript loader, HTML shell, and complete `variants` directory.

Visual QA status:

- Netlify desktop visual QA: PASSED.
- Netlify mobile visual QA: PASSED.
- Georgian text rendering: PASSED.

KB/routing status:

- Official source-backed answers work.
- Broad questions ask clarification questions.
- Unsupported questions do not hallucinate and route toward operator handover.
- Operator handover and "Wait for operator" UI are available.

Public launch status:

```text
PUBLIC_LAUNCH_STATUS=NO_GO
```

## 2. Final Upload Artifact

Use this exact ZIP only after owner approval:

```text
dist/final_alte_widget_upload.zip
```

Verified SHA256:

```text
EEE750AA2E960BECC71E840C75C57D58C4E02CECAE63AAD8C72769A87F32FE2A
```

Verified files inside the ZIP:

```text
alte-ai-chat-widget.js
alte-ai-chat-widget.html
variants/pro-v2-chat.jsx
variants/pro-v2-icons.jsx
variants/pro-v2-modals.jsx
variants/pro-v2-page.jsx
variants/pro-v2-strings.jsx
variants/tweaks-panel.jsx
```

Recommended target upload structure:

```text
/assets/alte-ai-chat-widget.js
/assets/alte-ai-chat-widget.html
/assets/variants/pro-v2-chat.jsx
/assets/variants/pro-v2-icons.jsx
/assets/variants/pro-v2-modals.jsx
/assets/variants/pro-v2-page.jsx
/assets/variants/pro-v2-strings.jsx
/assets/variants/tweaks-panel.jsx
```

Important upload note:

The script tag alone is not enough. The upload must include:

- `alte-ai-chat-widget.js`
- `alte-ai-chat-widget.html`
- the full `variants/` directory

The loader script fetches the HTML shell, and the HTML shell loads the variant files.

## 3. Embed Plan

Use this exact embed snippet only after staged embed approval:

```html
<script src="https://alte.edu.ge/assets/alte-ai-chat-widget.js" defer></script>
```

First staged pages:

- `join.alte.edu.ge` admissions/landing page.
- One approved `alte.edu.ge` program/admissions page.

Do not embed globally yet. Global embed should wait until staged real-domain smoke passes and final public launch approval is recorded.

## 4. Approval Gates

The owner must approve each gate before moving forward:

- Privacy URL approval.
- Contact-flow approval.
- Asset upload approval.
- Staged embed approval.
- Real-domain smoke approval.
- Final public launch GO.

Current approval state:

```text
PRIVACY_URL_STATUS=PENDING
CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED
ASSET_UPLOAD_STATUS=NOT_EXECUTED_PENDING_APPROVAL
STAGED_EMBED_STATUS=NOT_EXECUTED_PENDING_APPROVAL
REAL_DOMAIN_SMOKE_STATUS=NOT_EXECUTED
PUBLIC_LAUNCH_STATUS=NO_GO
```

## 5. Smoke Checklist After Staged Embed

Run this checklist only after the owner approves asset upload and staged embed:

- Widget loads on the staged page.
- `https://alte.edu.ge/assets/alte-ai-chat-widget.js` loads with `200`.
- `https://alte.edu.ge/assets/alte-ai-chat-widget.html` loads with `200`.
- Variant files under `https://alte.edu.ge/assets/variants/` load with `200`.
- Desktop visual check passes.
- Mobile visual check passes.
- Georgian text displays correctly.
- Source-backed answer check passes.
- Unsupported answer check passes without hallucinated facts.
- Clarification question check passes for broad questions.
- Contact form includes the question/message textarea.
- "Wait for operator" is visible.
- Informational questions do not create lead/task/customer records.
- Contact flow remains disabled unless separately approved.

Passing staged smoke does not automatically approve public launch.

## 6. Rollback Plan

If rollback is needed:

- Remove the embed snippet from the staged page.
- Restore the previous asset version or remove uploaded widget assets.
- Clear CDN/cache.
- Verify the widget no longer loads.
- Confirm backend is unaffected.

Backend rollback is not required for a site embed rollback. Do not change Cloud Run, database, Secret Manager, CORS, or KB/routing logic as part of this rollback.

## 7. Open Risks

- `pollOperatorMessages()` currently returns `[]`; "Wait for operator" marks backend/CRM waiting state, but visitor-side live operator reply polling is not active in the final bundle.
- Official Privacy URL is still pending.
- Contact creation is not approved.
- Dirty working tree reconciliation is still pending.

## 8. Final Recommendation

Ready for owner review:

```text
YES
```

Ready for public launch:

```text
NO-GO
```

Recommended next action: owner reviews this handoff, approves or rejects the asset upload and staged embed plan, and assigns smoke and rollback owners. Public launch must remain blocked until all approval gates are complete.

