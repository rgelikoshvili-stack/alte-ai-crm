# Phase 9AN Owner Approval Handoff

PHASE_9AN_OWNER_APPROVAL_HANDOFF_STATUS=READY_PENDING_OWNER_APPROVAL

Decision state:

```text
BACKEND_DEPLOYED_OWNER_HANDOFF_READY_PENDING_APPROVALS
```

Public launch: NO-GO

This handoff is for the site owner and approval owners. It explains what is ready, what is still blocked, which files must be uploaded, where they must be placed, how the staged embed should be approved, how to smoke test, and how to rollback.

No files have been uploaded to the real Alte website in this phase. No real-site embed has been applied.

## A. Current Status

- Technical package is ready.
- Final upload bundle is ready.
- Real Alte site has not been modified.
- `join.alte.edu.ge` has not been modified.
- Public launch remains NO-GO.

Current status values:

```text
ASSET_UPLOAD_STATUS=NOT_EXECUTED_PENDING_APPROVAL
STAGED_EMBED_STATUS=NOT_EXECUTED_PENDING_APPROVAL
REAL_DOMAIN_SMOKE_STATUS=NOT_EXECUTED
REAL_ALTE_SITE_MODIFIED=NO
JOIN_ALTE_SITE_MODIFIED=NO
PRIVACY_URL_STATUS=PENDING
CONTACT_FLOW_APPROVAL_STATUS=NOT_APPROVED
PUBLIC_LAUNCH_STATUS=NO_GO
```

## B. What Is Ready

The following items are ready for owner review:

- AI backend.
- Claude/AI backend integration.
- Official Knowledge Base answering.
- ChatGPT-style clarification questions for broad questions.
- Scoped source retrieval.
- Unsupported-question fallback that does not hallucinate unsupported information.
- Operator handover.
- Contact form question/message field.
- Wait for operator.
- Operator CRM inbox.
- Netlify desktop and mobile visual QA.
- Georgian encoding in the public widget.
- Final upload bundle containing the loader, HTML shell, and variants directory.

## C. What Is Still Pending

These items must be completed before public launch:

- Official Privacy URL.
- Contact-flow approval.
- Asset upload approval.
- Staged embed approval.
- Real-domain smoke.
- Final public launch approval.

Contact collection remains blocked until the privacy and contact-flow owners approve the policy, consent copy, storage behavior, and testing scope.

## D. Exact ZIP To Upload

Upload this ZIP only after explicit asset upload approval:

```text
dist/final_alte_widget_upload.zip
```

ZIP SHA256:

```text
EEE750AA2E960BECC71E840C75C57D58C4E02CECAE63AAD8C72769A87F32FE2A
```

The script tag alone is not enough. The ZIP must be extracted with the JavaScript loader, the HTML shell, and the complete `variants` directory.

## E. Required Upload Structure

The ZIP must be extracted so these files exist on the real site:

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

Each file must be served as UTF-8. Georgian text must not be corrupted by upload or CMS processing.

## F. Proposed Embed Snippet

Use this snippet only after staged embed approval:

```html
<script src="https://alte.edu.ge/assets/alte-ai-chat-widget.js" defer></script>
```

Do not embed this globally until the staged smoke passes and the owner explicitly approves wider rollout.

## G. First-Stage Pages

Embed first only on these staged pages:

- `join.alte.edu.ge` main admissions page.
- One `alte.edu.ge` admissions/program-related page selected by the owner.

Do not embed globally until staged smoke passes.

## H. Approval Checklist

Owner approval is required for:

- Official Privacy URL.
- Contact-flow consent copy.
- Contact form fields.
- Contact data storage and CRM creation behavior.
- Synthetic contact-flow test.
- Final asset upload.
- Staged page list.
- Real-domain smoke owner.
- Rollback owner.
- Final public launch owner.

No real contact details may be submitted until contact-flow approval is recorded. No customer, lead, or task should be created unless the approved contact-flow test or launch policy allows it.

## I. Real-Domain Smoke Checklist Summary

After staged embed is approved and applied, verify:

- Widget script loads `200`.
- HTML shell loads `200`.
- Variants load `200`.
- No CORS error.
- `/chat/session/start` works.
- `/chat/message` works.
- Georgian text displays correctly.
- Desktop visual OK.
- Mobile visual OK.
- Bachelor ECTS returns `240`, not `180`.
- Broad question asks a clarification question.
- Unsupported question does not hallucinate.
- Contact form has the question/message field.
- Wait for operator is visible.
- No lead/task/customer is created unless contact-flow approval explicitly allows the tested flow.
- Operator handover routes correctly.

Passing staged smoke does not approve public launch by itself.

## J. Rollback Summary

If rollback is needed:

- Remove the script tag from the staged page.
- Remove or rollback uploaded assets if needed.
- Clear page cache and CDN cache.
- Verify the widget no longer loads.
- Keep backend untouched.

Rollback must not change Cloud Run, Secret Manager, production DB, production migrations, production seeds, CORS, or official KB/routing logic.

## K. Explicit NO-GO Statement

Public launch remains NO-GO until privacy, contact-flow, asset upload, staged embed, real-domain smoke, and final public launch approvals are all complete and recorded.

