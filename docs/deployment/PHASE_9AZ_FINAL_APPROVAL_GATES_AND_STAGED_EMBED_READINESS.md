# Phase 9AZ Final Approval Gates and Staged Real-Site Embed Readiness

`PHASE_9AZ_STATUS=READY_FOR_OWNER_APPROVAL_REVIEW`

Decision state:

`BACKEND_DEPLOYED_FULL_KNOWLEDGE_AND_PUBLIC_ANSWER_CLEANUP_VERIFIED_PENDING_APPROVALS`

Public launch:

`NO-GO`

## 1. Current Verified Backend State

- Backend revision: `alte-ai-crm-backend-00051-btg`
- Backend image tag: `v0.9-phase-9ax-9ay-final-routing-cleanup3`
- Traffic: 100%
- Focused Phase 9AT QA: `7/7 PASS`
- Full Phase 9AS QA: `53/53 PASS`
- Operator alignment QA: `7/7 PASS`
- Browser/API answer-cleanliness QA: `7/7 PASS`
- Backend pytest: `1046 passed`
- Remaining failures/gaps: none
- Public launch: `NO-GO`

Technical backend chatbot/operator status is verified, but public launch remains blocked until the owner approval gates below are completed and recorded.

## 2. Remaining Approval Gates

- Official Privacy URL approval
- Contact-flow approval
- Asset upload approval
- Staged real-site embed approval
- Real-domain smoke approval
- Dirty tree reconciliation
- Final public launch GO

## 3. Privacy URL Gate

- Status: `PENDING`
- Required owner input: official privacy URL
- Contact form behavior: must remain blocked until the official privacy URL and consent behavior are approved.
- Public launch impact: blocking.

## 4. Contact-Flow Gate

- Status: `NOT_APPROVED`
- No real contact data submitted.
- No contact flow executed.
- No lead/customer/task created.
- Required approval: owner must approve consent copy, data collection fields, and CRM creation behavior before any real contact-flow execution.
- Public launch impact: blocking.

## 5. Final Asset Upload Gate

- Proposed asset URL: `https://alte.edu.ge/assets/alte-ai-chat-widget.js`
- Upload status: `NOT_EXECUTED_PENDING_APPROVAL`
- Prepared bundle path from prior handoff evidence: `dist/widget/alte-ai-chat-widget.js`
- Prepared bundle SHA256: `A5083446ADE39513D77969115FE0CEF21A4BF8EF3F588551BC87EFDD4E2C2B73`
- HTML preview/fallback path: `dist/widget/alte-ai-chat-widget.html`
- HTML preview/fallback SHA256: `654CAF34BFDA3DA43F040CE8836F39E582F53C3686E64395389F3DD5C1F8D6E7`
- Asset upload executed: NO
- Public launch impact: blocking.

Do not upload assets until the owner explicitly approves the final asset path and upload execution.

## 6. Staged Embed Gate

- Status: `NOT_EXECUTED_PENDING_APPROVAL`
- Staged pages:
  - `join.alte.edu.ge` admissions/landing page
  - one approved `alte.edu.ge` program/admissions page
- Global embed: NOT approved
- Global embed: NOT executed
- Staged embed executed: NO

Approved staged embed snippet after asset upload approval:

```html
<script src="https://alte.edu.ge/assets/alte-ai-chat-widget.js" defer></script>
```

Do not add this snippet to the real site until the owner explicitly approves staged embed execution.

## 7. Real-Domain Smoke Checklist

Run only after staged real-site embed approval and execution.

- Widget loads on the approved staged pages.
- Desktop layout works.
- Mobile layout works.
- Georgian text renders cleanly.
- Bachelor ECTS question returns `240 ECTS`.
- Master ECTS question returns `120 ECTS`.
- Computer Science spring calendar returns `9-14 March` and `30 March`.
- Unsupported prompts do not hallucinate.
- Explicit operator handover works.
- Informational questions do not create lead/customer/task records.
- Contact flow remains disabled unless separately approved.
- Public launch remains `NO-GO` until final launch approval is recorded.

## 8. Rollback Plan

If staged embed causes an issue:

1. Remove the staged embed snippet from the affected page.
2. If an asset was replaced, restore the previously approved asset version.
3. Verify the widget no longer loads on the affected real-domain page.
4. Keep backend service unchanged unless a backend issue is separately identified.
5. Record rollback time, page, asset URL, and verification result.

## 9. Dirty Tree Status

Current unrelated dirty/untracked files remain outside this phase and were not modified by this approval package.

Observed dirty tree categories include:

- Existing documentation updates outside Phase 9AZ.
- Existing visual QA image modifications.
- Existing evaluation result documents modified by production-safe QA scripts.
- Existing untracked QA/audit scripts and result files.
- Existing package-lock and generated helper files.

Owner decision required:

- Reconcile, commit, archive, or discard unrelated dirty/untracked files before final public launch.
- Do not mix unrelated dirty files into the final launch approval commit.

## 10. Final Recommendation

- Ready for owner approval review: YES
- Ready for public launch: NO-GO
- Next action: owner must provide/approve the official privacy URL and approve staged asset upload/embed execution.

## Safety Confirmation

- Real `alte.edu.ge` modified: NO
- Real `join.alte.edu.ge` modified: NO
- Assets uploaded: NO
- Embed executed: NO
- Frontend/Netlify changed: NO
- Contact flow submitted: NO
- Real contact data sent: NO
- Lead/customer/task created: NO
- DB schema/migration/seed/import changed or run: NO
- Secret Manager changed: NO
- CORS changed: NO
- Bridge Hub touched: NO
- Public launch: NO-GO
