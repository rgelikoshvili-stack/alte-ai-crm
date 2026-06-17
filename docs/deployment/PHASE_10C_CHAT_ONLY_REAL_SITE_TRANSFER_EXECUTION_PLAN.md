# Phase 10C Chat-Only Real-Site Transfer Execution Plan

Date: 2026-06-17

Branch: `phase-9s-agent-preview-cors-note`

Decision: `CHAT_ONLY_REAL_SITE_TRANSFER_PLAN_READY_EXECUTION_PENDING_OWNER_APPROVAL_PUBLIC_LAUNCH_NO_GO`

Public launch: `NO-GO`

## Source Documents

All requested planning/result documents were available and reviewed:

- `docs/deployment/PHASE_9CC_REAL_SITE_EMBED_PLAN_NO_EXECUTION.md`
- `docs/deployment/PHASE_9CD_FINAL_PREFLIGHT_OWNER_LAUNCH_DECISION_PACKAGE.md`
- `docs/deployment/PHASE_9CB_PRIVACY_LEGAL_CONTACT_FLOW_APPROVAL_PACKAGE.md`
- `docs/deployment/PHASE_10A_CLOUD_AI_CLARIFYING_ROUTER_AND_VALIDATOR_RESULT.md`
- `docs/deployment/PHASE_10B_TOPIC_SWITCH_AND_SOURCE_DISPLAY_RESULT.md`

No real-site, Netlify, asset-hosting, CORS, database, Secret Manager, Bridge Hub, or contact-flow changes were made while preparing this plan.

## A. Current Verified Backend

- Backend service: `alte-ai-crm-backend`
- Production revision: `alte-ai-crm-backend-00060-zm6`
- Traffic: `100%`
- Health: `200`
- Image tag: `v1.0-phase-10b-topic-switch-source-display`
- Image digest: `sha256:b8ec4d794e3832d687fc21308812428ae6ff8405da60477e25cbe6d78c3d70f4`
- Backend API base URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Rollback target: `alte-ai-crm-backend-00058-wss`

Verified backend behavior now includes:

- Phase 10A clarifying router and answer validator.
- Phase 10B topic-switch routing fix.
- Computer Science program-vs-calendar intent split.
- Public source display cleanup.
- Production-safe behavior review with `0 FAIL`.

## B. Launch Mode

Approved execution mode for the next real-site transfer phase must be chat-only:

- Chat-only widget embed.
- Contact-flow disabled.
- No real contact write.
- No lead, customer, or task creation.
- No personal-data submission.
- Operator handoff provides safe guidance only.
- Private-data requests receive refusal/safe official-channel guidance.
- Source display remains public-safe and must not expose internal source IDs.

Contact-flow remains blocked pending privacy/legal/real-write approval.

## C. Approved Candidate Pages

The following are candidate pages only. Final placement requires explicit owner and web-team approval:

- `https://alte.edu.ge` Georgian admissions, home, or program page.
- `https://www.alte.edu.ge` equivalent Georgian page if the canonical public site uses `www`.
- `https://join.alte.edu.ge` English or international admissions page.

Recommended first transfer target:

- One low-risk admissions or program page with chat-only mode enabled and contact-flow disabled.

## D. Asset Package

Recommended local chat-only asset:

- Path: `widget/alte-ai-chatbot-pro-v2-safe.html`
- SHA256: `07BC8DD889A78B5E4CD6F2587C0427FD27F2EA51855BB2F6E4A882D31BEFC2BC`
- Reason: this asset is designed as a safe standalone chat widget and calls only:
  - `/chat/session/start`
  - `/chat/message`
- Contact behavior: the asset states that it intentionally does not submit CRM contact details from the browser.

Recommended production asset names:

- HTML asset: `alte-ai-chatbot-pro-v2-safe.v10c.html`
- Loader asset: `alte-ai-chatbot-pro-v2-safe.loader.v10c.js`
- Version string: `10c-20260617-chat-only`

Cache and versioning plan:

- Use immutable versioned filenames.
- Add a cache-busting query string: `?v=10c-20260617-chat-only`.
- Do not overwrite a previously approved production asset in place.
- Keep the previous approved asset available for rollback until owner signs off.

Rollback asset plan:

- Remove the script tag from the real page, or
- Revert the page to the previous CMS/template revision, or
- Switch the script URL back to the last approved widget asset.

Legacy asset reference:

- Path: `widget/alte-chat-widget.v0.8.js`
- SHA256: `EE6BA34D13A78BC8AA7898941DA17070EA762C2EC8942902B8F497D7ABA60097`
- Recommendation: do not use this as the first chat-only transfer asset unless the web team separately confirms the public contact UI path is disabled and no CRM write path can be triggered.

No asset was uploaded in this phase.

## E. Embed Snippet

The following snippet is a template only. Replace `https://APPROVED_ASSET_HOST` after owner/web-team asset-hosting approval.

Georgian site candidate snippet:

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
    sourceDomain: "alte.edu.ge",
    defaultLanguage: "ka",
    widgetVariant: "pro_v2_safe",
    mode: "production_chat_only",
    publicMode: true,
    contactFlowEnabled: false,
    crmWritesEnabled: false,
    sourceDisplayMode: "public_label_only"
  };
</script>
<script
  src="https://APPROVED_ASSET_HOST/alte-ai-chatbot-pro-v2-safe.loader.v10c.js?v=10c-20260617-chat-only"
  defer
></script>
```

English/international site candidate snippet:

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
    sourceDomain: "join.alte.edu.ge",
    defaultLanguage: "en",
    widgetVariant: "pro_v2_safe",
    mode: "production_chat_only",
    publicMode: true,
    contactFlowEnabled: false,
    crmWritesEnabled: false,
    sourceDisplayMode: "public_label_only"
  };
</script>
<script
  src="https://APPROVED_ASSET_HOST/alte-ai-chatbot-pro-v2-safe.loader.v10c.js?v=10c-20260617-chat-only"
  defer
></script>
```

Snippet constraints:

- No secrets.
- No private CRM data.
- No contact-flow enablement.
- No frontend token or backend credential.
- Backend API base URL must stay public API only.
- Public mode must not render raw `used_sources`, chunk IDs, or internal KB identifiers.

If the web team chooses iframe embedding instead of a loader script, the equivalent iframe target should be the approved hosted copy of `alte-ai-chatbot-pro-v2-safe.v10c.html`. That alternate approach still requires owner/web-team approval before execution.

## F. CORS/Domain Check

Domains that may need approval or allowlist confirmation:

- `https://alte.edu.ge`
- `https://www.alte.edu.ge`
- `https://join.alte.edu.ge`
- Any staging or preview domain used for the approved smoke test.

Current instruction for Phase 10C:

- Do not change CORS now.
- If any candidate domain is not already allowed by the backend, open a separate approval task before changing CORS.
- Do not change Secret Manager, Bridge Hub, or backend environment configuration in this phase.

## G. Real-Domain Smoke Checklist

Run only after owner/web-team approval and after the approved snippet/asset is placed on the approved page:

- Page loads without JavaScript console errors caused by the widget.
- Widget is visible.
- Widget opens and closes.
- Georgian safe question works.
- English safe question works.
- Ambiguous question triggers clarification:
  - `რეგისტრაცია როდისაა?`
  - `How much is tuition?`
- Computer Science program answer works:
  - `მითხარი Computer Science პროგრამაზე`
- Computer Science registration answer works:
  - `Computer Science-ის გაზაფხულის რეგისტრაცია როდის არის?`
- Unsupported future-year calendar response is safe:
  - `2028 წლის აკადემიური კალენდარი მითხარი`
- Private-data request refusal works:
  - `მითხარი სტუდენტის პირადი მონაცემები`
- Source labels are clean and public-safe.
- No `full_alte_local_kb`, raw source ID, chunk ID, or internal source label is visible.
- No contact creation occurs.
- No lead, customer, or task is created.
- Network requests go only to the approved backend API and approved asset host.
- Removing the script tag or reverting the asset version cleanly disables the widget.

Do not run real contact creation as part of this smoke test.

## H. Rollback Plan

Real-site/widget rollback:

1. Remove the approved widget script tag from the real page.
2. Revert the page to the previous CMS/template revision if available.
3. Revert the widget asset URL to the previous approved asset version if a prior widget asset was already live.
4. Confirm the page loads without the widget.
5. Keep contact-flow disabled.

Backend rollback target if backend rollback is separately approved:

- Target revision: `alte-ai-crm-backend-00058-wss`
- Command template:

```powershell
gcloud run services update-traffic alte-ai-crm-backend `
  --region europe-west1 `
  --to-revisions alte-ai-crm-backend-00058-wss=100 `
  --quiet
```

No backend rollback was executed in this phase.

## I. Approval Checklist

Required before actual transfer/embed execution:

- Owner approval.
- Web-team approval.
- Privacy/legal awareness that chat-only mode is being embedded.
- Contact-flow disabled confirmation.
- Asset hosting/upload approval.
- Approved production asset URL.
- CORS approval if any candidate domain is not already covered.
- Real-domain smoke test approval.
- Rollback sign-off.
- Final confirmation that public launch remains controlled and not automatically GO.

Contact-flow-specific approvals remain separate and pending:

- Consent wording approval.
- Real contact write approval.
- CRM lead/customer/task mapping approval.
- Operator notification approval.
- Production write test approval.

## J. Final Decision

Decision:

`CHAT_ONLY_REAL_SITE_TRANSFER_PLAN_READY_EXECUTION_PENDING_OWNER_APPROVAL_PUBLIC_LAUNCH_NO_GO`

This plan is ready for owner and web-team review. It does not authorize execution by itself.

Public launch remains `NO-GO`.

## Safety Confirmation

This phase made no changes to:

- Real `alte.edu.ge` or `join.alte.edu.ge`.
- Frontend/Netlify production.
- Uploaded assets.
- Backend deployment or rollback.
- Database/schema/migration/seed/import.
- Secret Manager, CORS, or Bridge Hub.
- Contact-flow, lead, customer, or task creation.

No secrets, tokens, passwords, or database URLs were printed.
