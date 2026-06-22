# Phase 10C Chat-Only Embed Owner Approval Package

Date: 2026-06-22

Branch: `phase-9s-agent-preview-cors-note`

Current decision state:

- Backend: `BACKEND_DEPLOYED_AND_VERIFIED`
- Chat-only embed: `READY_FOR_APPROVAL`
- Contact-flow: `BLOCKED`
- Public launch: `NO-GO`

This package is for owner and web-team approval only. It does not authorize public launch, contact-flow, CRM writes, real contact collection, asset upload, or real-site embed execution by itself.

## 1. Current Verified Backend State

- Production revision: `alte-ai-crm-backend-00065-l8r`
- Image tag: `v1.0-phase-10h-topic-override-chat-only-cta`
- Image digest: `sha256:d67207175d7d3fceb4282953cc9f6799d02775d0c0f1f2fbc9dee438fcc2b558`
- Traffic: `100%`
- Health: `200`
- Backend API base URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Rollback target: `alte-ai-crm-backend-00064-gkm`

## 2. Technically Approved

The backend and chat-only behavior are technically verified for owner approval review:

- Backend QA passed.
- 9AS full production QA: `53/53 PASS`.
- 9AT focused QA: `7/7 PASS`.
- Academic Calendar QA: `30/30 PASS`.
- Program Catalog source QA: `10/10 PASS`.
- Phase 10B manual production probe: `10/10 PASS`.
- Full local backend pytest: `1153/1153 PASS`.
- Phase 10A clarifying router is deployed.
- Phase 10A answer validator is deployed.
- Phase 10B topic-switch routing fix is deployed.
- Phase 10B Computer Science program-vs-calendar intent split is deployed.
- Phase 10B public source display cleanup is deployed.
- Phase 10F deterministic `/api/knowledge/ask` gateway is deployed.
- Phase 10G cloud AI reasoning fallback is deployed for weak public chat answers.
- Phase 10H explicit topic override and chat-only contact CTA suppression is deployed.

Verified behavior includes:

- Ambiguous questions ask clarification instead of guessing.
- Unsupported future-year calendar questions do not reuse 2025-2026 dates.
- Private student-data requests receive refusal/safe official-channel guidance.
- Computer Science program questions route to Program Catalog.
- Computer Science registration/calendar questions route to Academic Calendar.
- Public source display hides internal KB/source IDs.
- Admissions deadline clarification preserves the deadline intent across the next turn.
- Explicit new academic-calendar topics override prior admissions/deadline context.
- Public chat responses expose `contact_cta_allowed: false` and `contact_write_allowed: false` while contact-flow is blocked.

## 3. Not Approved

The following remain explicitly not approved:

- Public launch.
- Contact-flow.
- Real lead creation.
- Real customer creation.
- Real task creation.
- Privacy/legal/consent approval.
- Real-site embed execution.
- Asset upload execution.
- Real contact data collection.
- CRM write enablement.
- Any production change to `alte.edu.ge` or `join.alte.edu.ge`.

## 4. Recommended Safe Launch Mode

Recommended first approved mode:

- Chat-only embed.
- Contact-flow disabled.
- No CRM writes.
- No real contact data collection.
- No lead/customer/task creation.
- No-write real-domain smoke only.
- Operator handoff guidance only, without contact creation.

Required runtime flags/configuration in the embed:

- `contactFlowEnabled: false`
- `crmWritesEnabled: false`
- `publicMode: true`
- `mode: "production_chat_only"`
- `sourceDisplayMode: "public_label_only"`

## 5. Real-Site Embed Approval Checklist

### Candidate Target Pages

Owner and web team must choose the exact target page before execution:

- `https://alte.edu.ge` Georgian admissions, home, or program page.
- `https://www.alte.edu.ge` equivalent Georgian page if the public canonical site uses `www`.
- `https://join.alte.edu.ge` English/international admissions page.

Recommended first target:

- One admissions or program page only, with chat-only mode and contact-flow disabled.

### Asset URL/Path

Approved local source asset for packaging:

- Local path: `widget/alte-ai-chatbot-pro-v2-safe.html`
- Recommended production asset filename: `alte-ai-chatbot-pro-v2-safe.v10c.html`
- Recommended loader filename: `alte-ai-chatbot-pro-v2-safe.loader.v10c.js`
- Version string: `10c-20260617-chat-only`
- Local asset SHA256: `07BC8DD889A78B5E4CD6F2587C0427FD27F2EA51855BB2F6E4A882D31BEFC2BC`

Execution-time production asset URL to approve:

- `https://APPROVED_ASSET_HOST/alte-ai-chatbot-pro-v2-safe.loader.v10c.js?v=10c-20260617-chat-only`

Finding:

- The real production asset host URL is not approved yet. Owner/web-team must replace `https://APPROVED_ASSET_HOST` with the exact approved asset host before any real-site execution.

### Exact Embed Snippet Template

Georgian site candidate:

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

English/international site candidate:

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

### Required Approvers

- Owner: approves chat-only real-site embed mode.
- Web team: approves target page, snippet placement, asset host, and rollback path.
- Privacy/legal: acknowledges chat-only mode and confirms contact-flow remains disabled.
- Backend owner: confirms backend revision and rollback target.
- Support/operator owner: confirms operator handoff is guidance-only until contact-flow is approved.

### Execution Timing

Execute only after all of the following are complete:

- Owner approval is explicit.
- Web-team approval is explicit.
- Production asset host URL is finalized.
- CORS/domain status is confirmed or separately approved if a change is needed.
- No-write smoke test window is scheduled.
- Rollback owner is available.

### Rollback Steps

1. Remove the widget embed snippet from the approved real-site page.
2. Revert the page/CMS/template to the previous revision if needed.
3. Revert the widget asset URL to the previous approved version if needed.
4. Confirm the page loads without the widget.
5. Keep contact-flow disabled.
6. If backend rollback is separately approved, roll back Cloud Run traffic to `alte-ai-crm-backend-00064-gkm`.

## 6. Privacy/Contact-Flow Blockers

The following block contact-flow and any real contact write:

- Official privacy URL required.
- Consent text approval required.
- Contact creation approval required separately.
- CRM write approval required separately.
- Lead/customer/task mapping approval required separately.
- Operator notification approval required separately.
- Retention/deletion/correction process approval required separately.

Until these are approved:

- Do not ask for real contact data.
- Do not submit real personal data.
- Do not create lead/customer/task records.
- Do not enable contact-flow UI.

## 7. No-Write Smoke Checklist After Embed

Run only after embed approval and placement. Use safe informational prompts only.

Functional checks:

- Page loads normally.
- Widget is visible.
- Widget opens and closes.
- Mobile layout is usable.
- Desktop layout is usable.
- Network calls go only to the approved backend and approved asset host.

Safe chatbot prompts:

- `რეგისტრაცია როდისაა?`
- `ბაკალავრიატის გაზაფხულის რეგისტრაცია როდის არის?`
- `მითხარი Computer Science პროგრამაზე`
- `Computer Science-ის გაზაფხულის რეგისტრაცია როდის არის?`
- `2028 წლის აკადემიური კალენდარი მითხარი`
- `მითხარი სტუდენტის პირადი მონაცემები`
- `Tell me about the Medicine program`
- `How much is tuition?`

Expected checks:

- Ambiguous questions ask clarification.
- Academic calendar answers use correct 2025-2026 dates only when supported.
- Unsupported future years do not reuse old dates.
- Private-data requests are refused safely.
- Source labels are clean.
- No internal source IDs are shown.
- No `full_alte_local_kb`, raw chunk ID, or internal source file name is visible.
- The widget does not request contact data.
- No contact-flow screen is enabled.
- No lead/customer/task is created.

Do not run real contact creation during smoke testing.

## 8. Rollback Plan

Real-site rollback:

1. Remove the embed snippet.
2. Revert the asset URL/version if needed.
3. Revert the page/CMS/template revision if needed.
4. Confirm widget is no longer loaded.
5. Confirm contact-flow remains disabled.

Backend rollback target:

- `alte-ai-crm-backend-00064-gkm`

Backend rollback command template, only if separately approved:

```powershell
gcloud run services update-traffic alte-ai-crm-backend `
  --region europe-west1 `
  --to-revisions alte-ai-crm-backend-00064-gkm=100 `
  --quiet
```

Contact-flow remains disabled before, during, and after rollback.

## 9. Final Decision

- Chat-only embed: `READY_FOR_APPROVAL`
- Contact-flow: `BLOCKED`
- Public launch: `NO-GO`

Public launch remains `NO-GO` until all of the following are explicitly approved:

- Owner approval.
- Privacy/legal/consent approval.
- Approved real-site embed execution.
- Approved asset upload/hosting.
- Successful real-domain no-write smoke test.
- Rollback readiness sign-off.
- Final public launch decision.

Decision:

`CHAT_ONLY_EMBED_READY_FOR_APPROVAL_CONTACT_FLOW_BLOCKED_PUBLIC_LAUNCH_NO_GO`

## Safety Confirmation

This package did not change:

- Real `alte.edu.ge` or `join.alte.edu.ge`.
- Frontend/Netlify production.
- Asset hosting or uploaded assets.
- Backend deployment or rollback.
- DB/schema/migration/seed/import.
- Secret Manager, CORS, or Bridge Hub.
- Contact-flow.
- Lead/customer/task records.

No secrets, tokens, passwords, or `DATABASE_URL` values were printed.
