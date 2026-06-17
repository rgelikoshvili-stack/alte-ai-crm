# Phase 9AE Final Preflight Approval Package

PHASE_9AE_FINAL_PREFLIGHT_APPROVAL_STATUS=NO_GO_PENDING_PRIVACY_CONTACT_ASSET_EMBED_AND_REAL_DOMAIN_SMOKE

Decision state:

```text
BACKEND_DEPLOYED_WIDGET_MOBILE_RESPONSIVE_VISUAL_QA_PASSED_PENDING_PRIVACY_AND_EMBED_APPROVAL
```

Public launch: NO-GO

site embed status: NOT_EXECUTED

## Scope

- Production backend: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Active backend revision from Phase 9AD: `alte-ai-crm-backend-00032-lzq`
- Netlify test site: `https://nimble-croissant-2f66e8.netlify.app/join.html`
- Real `alte.edu.ge` modified: NO
- Real `join.alte.edu.ge` modified: NO
- Backend behavior changed in this phase: NO
- CORS changed in this phase: NO
- Secret Manager changed in this phase: NO
- Production DB changed in this phase: NO
- Migration/seed run in this phase: NO
- Contact details sent: NO
- Lead/task/customer created: NO

## Passing Technical Checks

- Official KB browser/source-backed QA: PASSED.
- Integrated routing QA: PASSED `18/18`.
- Official KB answer QA: PASSED `6/6`.
- Auto-routing QA: PASSED `10/10`.
- Handover/contact safety QA: PASSED `2/2`.
- Operator CRM local login/dashboard/inbox: PASSED.
- No direct phone/email/name request found in approved no-contact QA.
- No lead/task/customer created during informational/no-contact QA.
- Netlify widget visual QA:
  - Desktop `1440x900`: PASS.
  - Mobile `430x932`: PASS, `sidebarVisible=false`.
  - Mobile `390x844`: PASS, `sidebarVisible=false`.
  - Mobile `375x667`: PASS, `sidebarVisible=false`.
- Live Netlify asset contains the mobile responsive guard:

```text
@media (max-width: 1024px)
```

Official KB guardrails remain required:

- Bachelor completion: `240 ECTS`, not `180`.
- Master program: `120 ECTS`.
- Student status suspension: maximum total `5 years`.
- Unsupported questions must return no approved source / conservative operator confirmation, not invented facts.
- Informational questions must not create lead/task/customer.

## Remaining Approvals

| Approval | Current Status | Required Before Real Embed/Public Launch |
| --- | --- | --- |
| Official privacy URL | PENDING | Record the approved Alte privacy policy URL and replace any placeholder. |
| Privacy/data final approval | APPROVED_IN_PRINCIPLE_PENDING_OFFICIAL_PRIVACY_URL | Final sign-off after official URL and copy are approved. |
| Contact-flow approval | NOT_APPROVED_SEPARATE_GATE | Separate approval required before testing or enabling real contact details. |
| Final widget asset URL | PENDING_APPROVAL_AND_UPLOAD | Website team must approve and publish the final asset URL. |
| Staged real-site embed approval | NOT_EXECUTED_PENDING_EXPLICIT_APPROVAL | User/site owner must approve exact pages/templates before any real-site change. |
| Real-domain smoke | NOT_EXECUTED | Must run after approved embed on the actual domain. |
| Dirty tree reconciliation | PENDING | Unrelated modified/untracked files need owner decision. |
| Final public launch approval | NO-GO | Must remain separate from embed smoke. |

## Privacy URL Status

Official privacy URL status:

```text
OFFICIAL_PRIVACY_URL_STATUS=PENDING
```

Current known privacy state:

- Privacy/data approval exists only in principle.
- Final privacy/data launch sign-off remains pending.
- The approved official privacy URL has not been recorded.
- The widget must not ship to the real site with `#privacy-policy-pending` or any placeholder privacy URL.

Required approval record before embed:

```text
OFFICIAL_PRIVACY_URL=<approved Alte privacy policy URL>
PRIVACY_DATA_FINAL_APPROVAL_STATUS=APPROVED
```

## Contact-Flow Approval Status

Contact-flow status:

```text
CONTACT_CREATION_FLOW_STATUS=NOT_APPROVED_FOR_REAL_CONTACT_DATA_TEST
```

Allowed before approval:

- Ask normal informational chatbot questions.
- Trigger operator/handover intent without contact details.
- Confirm the UI shows safe consent/contact copy.
- Confirm no lead/task/customer is created without approved details and explicit consent.

Not allowed before approval:

- Sending real phone/email/name or other personal data.
- Using real applicant contact details.
- Creating production lead/task/customer records through contact-flow testing.
- Marking contact creation launch-ready.

Separate approval text required:

```text
Approve Phase 9AE contact creation flow test with synthetic contact data only.
```

## Proposed Final Widget Asset URL

Recommended Alte-controlled static asset URL:

```text
https://alte.edu.ge/assets/alte-ai-chat-widget.js
```

Current status:

```text
FINAL_WIDGET_ASSET_URL_STATUS=PENDING_APPROVAL_AND_UPLOAD
FINAL_WIDGET_ASSET_URL_PROPOSED=https://alte.edu.ge/assets/alte-ai-chat-widget.js
```

The current deployable asset source is:

```text
dist/widget/alte-ai-chat-widget.js
```

If the website team chooses a different approved Alte-controlled URL, only the `script src` value should change, and the approved final URL must be recorded before embed.

## Proposed Embed Snippet

Preparation only. Do not apply this to `alte.edu.ge` or `join.alte.edu.ge` without separate explicit approval.

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

Required frontend contract:

- Browser calls only Cloud Run FastAPI.
- Required chat endpoints remain `/chat/session/start` and `/chat/message`.
- Browser must not call `/api/chat`.
- Browser must not call `api.anthropic.com`.
- Browser must not include `ANTHROPIC_API_KEY`, `sk-ant`, database URLs, tokens, or hashes.

## Staged Target Pages

Recommended staged rollout after explicit approval:

1. Hidden/staging page or a low-risk public test page controlled by the website team.
2. `https://join.alte.edu.ge/` or approved admissions landing page.
3. `https://alte.edu.ge/`
4. `https://alte.edu.ge/ka`
5. `https://alte.edu.ge/en`
6. Program listing page.
7. Bachelor program detail page.
8. Master program detail page.
9. Academic calendar or student information page if public.
10. Contact/help page.

Do not expand beyond the first approved page until real-domain smoke passes.

## Real-Domain Smoke Checklist

Run only after approved real-site embed.

Service checks:

- `GET /health`: `200`.
- `GET /version`: `200`.
- `GET /diagnostics/ai`: `200`.
- Unauthenticated `/dashboard/overview`: `401`.

Browser and visual checks:

- Widget launcher visible and tappable.
- Desktop `1440x900` and `1366x768` layout passes.
- Mobile `430x932`, `390x844`, and `375x667` layout passes.
- No horizontal scroll.
- Header visible.
- Composer visible.
- Source-backed answer UI displays source/trust information.
- Unsupported answer UI clearly states no approved source / operator confirmation needed.
- Loading/error states are readable and do not expose internal errors.

Official KB smoke:

- Bachelor completion returns `240 ECTS`, not `180`.
- Master program returns `120 ECTS`.
- Student status suspension returns maximum total `5 years`.
- Computer Science spring registration returns `9-14 March`; semester starts `30 March`.
- Master admissions documents match the official checklist.
- Unsupported `2031` scholarship question returns no approved source, not invented details.

Contact safety:

- Operator request may show handover/contact card.
- Assistant text must not ask the user to type phone/email/name directly before approved contact flow.
- No lead/task/customer created during no-contact smoke.
- Contact creation flow remains blocked unless separately approved with synthetic data only.

Rollback readiness:

- Rollback owner named.
- Smoke owner named.
- Remove config script and widget script tag to disable the widget.
- Clear site/CDN cache if used.
- Confirm no backend calls from rolled-back pages.

## Dirty Tree Triage

Do not delete, revert, or commit unrelated files without explicit owner approval.

Modified files:

| Path | Classification | Recommendation |
| --- | --- | --- |
| `README.md` | leave pending | Existing unrelated documentation change; do not commit in Phase 9AE without owner approval. |
| `docs/NEXT_PHASES.md` | leave pending | Existing unrelated planning change; do not commit in Phase 9AE without owner approval. |
| `docs/deployment/FINAL_PREFLIGHT_GATE.md` | leave pending | Existing unrelated gate update; do not commit in Phase 9AE without owner approval. |
| `docs/deployment/PHASE_9P_PUBLIC_LAUNCH_DECISION.md` | leave pending | Existing unrelated launch-decision update; do not commit in Phase 9AE without owner approval. |

Untracked files:

| Path | Classification | Recommendation |
| --- | --- | --- |
| `MANUS_CONTEXT.md` | leave pending | External/context note; owner should decide whether to keep or ignore. |
| `backend/app/scripts/production_kb_source_coverage_qa.py` | leave pending | Potential useful QA script; needs separate review before commit. |
| `backend/app/scripts/verify_phase_9x_browser_smoke_contact_safety.py` | leave pending | Potential Phase 9X verifier; needs separate review before commit. |
| `backend/docs/` | leave pending | Generated/backend-local docs; review before commit. |
| `docs/deployment/FULL_PROJECT_AUDIT_2026_05_30.md` | leave pending | Audit source-of-truth candidate; owner should approve whether to commit. |
| `docs/deployment/PHASE_9X_BROWSER_SMOKE_AND_CONTACT_SAFETY_RESULT.md` | leave pending | Phase 9X evidence; review before commit. |
| `docs/deployment/visual_qa/netlify_widget_desktop_1440x900.png` | leave pending | Older screenshot evidence; likely superseded by `_phase_9ab` screenshots. |
| `docs/deployment/visual_qa/netlify_widget_desktop_1440x900_wait.png` | leave pending | Older screenshot evidence; likely superseded by `_phase_9ab` screenshots. |
| `docs/deployment/visual_qa/netlify_widget_mobile_430x932.png` | leave pending | Older screenshot evidence; likely superseded by `_phase_9ab` screenshots. |
| `docs/deployment/visual_qa/netlify_widget_mobile_430x932_wait.png` | leave pending | Older failure evidence; keep only if owner wants historical record. |
| `docs/knowledge_evidence/uploaded_pro_v2_zip_source/deploy/package-lock.json` | leave pending | Generated package lock; review before commit. |
| `frontend/package-lock.json` | leave pending | Generated package lock; review before commit. |
| `generate_manual.py` | leave pending | Generated/helper script; review before commit. |
| `generate_training.py` | leave pending | Generated/helper script; review before commit. |

Phase 9AE commit scope:

```text
commit only:
- docs/deployment/PHASE_9AE_FINAL_PREFLIGHT_APPROVAL_PACKAGE.md
- backend/app/scripts/verify_phase_9ae_final_preflight_approval_package.py
- backend/app/tests/test_phase_9ae_final_preflight_approval_package.py
```

## Final Recommendation

```text
PUBLIC_LAUNCH_RECOMMENDATION=NO_GO_PENDING_PRIVACY_URL_CONTACT_FLOW_APPROVAL_FINAL_ASSET_URL_STAGED_REAL_SITE_EMBED_REAL_DOMAIN_SMOKE_AND_FINAL_PUBLIC_LAUNCH_APPROVAL
```

Do not modify the real Alte site until explicit staged embed approval is provided.
