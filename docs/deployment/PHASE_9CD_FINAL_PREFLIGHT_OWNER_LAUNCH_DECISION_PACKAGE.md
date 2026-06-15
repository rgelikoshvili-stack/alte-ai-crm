# Phase 9CD Final Preflight Owner Launch Decision Package

Date: 2026-06-15

Branch: `phase-9s-agent-preview-cors-note`

Decision: `FINAL_PREFLIGHT_PREPARED_OWNER_APPROVAL_PENDING_PUBLIC_LAUNCH_NO_GO`

Public launch: `NO-GO`

## Source Documents

- `docs/deployment/PHASE_9BZ_POST_DEPLOY_FINAL_AUDIT_AND_APPROVAL_GATES.md`: FOUND
- `docs/deployment/PHASE_9CA_LAUNCH_APPROVAL_GATES_REFRESH.md`: FOUND
- `docs/deployment/PHASE_9CB_PRIVACY_LEGAL_CONTACT_FLOW_APPROVAL_PACKAGE.md`: FOUND
- `docs/deployment/PHASE_9CC_REAL_SITE_EMBED_PLAN_NO_EXECUTION.md`: FOUND
- `docs/deployment/PHASE_9AZ_FINAL_APPROVAL_PACKAGE.md`: NOT_FOUND
- `docs/deployment/FINAL_PREFLIGHT_GATE.md`: FOUND
- `docs/deployment/PHASE_9P_PUBLIC_LAUNCH_DECISION.md`: FOUND

## A. Backend Readiness

Cloud Run service:

- Service: `alte-ai-crm-backend`
- Region: `europe-west1`
- Current revision: `alte-ai-crm-backend-00054-m6r`
- Traffic: `alte-ai-crm-backend-00054-m6r=100%`
- Health: PASS, HTTP 200
- Backend API base URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Cloud Run service URL reported by `gcloud run services describe`: `https://alte-ai-crm-backend-oobzrmikna-ew.a.run.app`
- Image tag: `v0.9-phase-9by-calendar-hotfix`
- Image digest: `sha256:b456378796a91c2ca2140935affbcdc0bd7edabc18b3a694e8a25761e9234fb3`
- Rollback target: `alte-ai-crm-backend-00053-pbz`

Rollback command:

```powershell
gcloud run services update-traffic alte-ai-crm-backend --region europe-west1 --to-revisions alte-ai-crm-backend-00053-pbz=100 --quiet
```

Repository state before Phase 9CD doc creation:

- `git status --short --branch`: clean on `phase-9s-agent-preview-cors-note`
- `git rev-parse HEAD`: `518966421b3a19acd0bc6070e8c91f4708145915`

Local validation run from `C:\tmp\alte-ai-crm\backend`:

| Check | Result |
| --- | --- |
| `python -m compileall app` | PASS |
| `pytest --basetemp .pytest_tmp_9cd_final_preflight` | PASS, 1112/1112 |
| `python -m app.scripts.verify_phase_9be_academic_calendar_fixes` | PASS |
| `python -m app.scripts.local_phase_9be_academic_calendar_fixes_qa` | PASS, 30/30 |
| `pytest app/tests/test_phase_9bf_georgian_control_fixes.py app/tests/test_phase_9bg_public_widget_source_display_cleanup.py --basetemp .pytest_tmp_9cd_9bf_9bg` | PASS, 12/12 |

Production-safe QA evidence from Phase 9BZ/9CA:

| Gate | Status | Evidence |
| --- | --- | --- |
| Backend deployed | COMPLETE | Revision `alte-ai-crm-backend-00054-m6r` |
| Backend health | COMPLETE | HTTP 200 |
| Traffic allocation | COMPLETE | 100% to `alte-ai-crm-backend-00054-m6r` |
| Full 9AS | COMPLETE | PASS, 53/53 |
| Focused 9AT | COMPLETE | PASS, 7/7 |
| Operator alignment | COMPLETE | PASS, 7/7 |
| Program Catalog source QA | COMPLETE | PASS, 10/10 available production source QA |
| 9BE Academic Calendar | COMPLETE | Local 30/30 PASS; production 9AS academic-calendar 9/9 |
| 9BF/9BG focused | COMPLETE | PASS, 12/12 |
| Worktree/deploy hygiene | COMPLETE | Clean at launch-gate baseline |
| Contact-flow execution | NOT_EXECUTED | No real contact data sent; no lead/customer/task created |

Backend phases currently live:

- Phase 9BF: Georgian control fixes
- Phase 9BG: public widget source-display cleanup
- Phase 9BE: Academic Calendar routing and exact-date fixes
- Phase 9BY: Georgian Bachelor spring registration production hotfix

## B. Privacy And Contact-Flow Readiness

Confirmed data fields from Phase 9CB:

- Session/conversation context: `conversation_id`, `session_id`, `channel`, `source_domain`, `language`, `widget_variant`, `metadata`, `page_url`.
- User chat content: chat `message`, contact-form `message`, `question`, `note`.
- Contact identity: `first_name`, `last_name`, `full_name`, `phone`, `email`.
- Interest/routing: `interest_area`, `selected_department`, `selected_topic`, `department_id`, `source_domain`, `source_channel`.
- CRM records that can be created after approved contact submission: customer, lead, conversation, message, operator task, audit/operator context.
- Consent status: contact submission requires consent and stores `explicit_chat_contact_request` on the customer record.

Privacy/legal gates:

| Gate | Status | Notes |
| --- | --- | --- |
| User-facing privacy notice | PENDING | No final approved privacy notice URL is recorded in 9CB/9CC. |
| Consent wording before contact submission | PENDING | Exact public wording still requires owner/legal approval. |
| Data retention policy | PENDING | Retention duration and deletion/correction process still require approval. |
| Access control for leads/tasks | PENDING | Operator/admin access scope still requires approval. |
| Deletion/correction request process | PENDING | Must be defined before contact writes are approved. |
| Legal basis for processing | PENDING | Legal owner sign-off required. |
| Minors/student data caution | PENDING | Handling guidance still requires approval. |
| Human operator handoff wording | PENDING | Public wording still requires approval. |
| No-spam/no-unwanted-contact wording | PENDING | Public wording still requires approval. |

Contact-flow gates:

| Gate | Status | Notes |
| --- | --- | --- |
| Dry-run/safety contact-flow QA | PENDING | Not run in 9CB/9CD. |
| Real write approval | PENDING | No approval for real contact/customer/lead/task writes. |
| Operator notification approval | PENDING | Operator workflow approval still required. |
| CRM lead/customer/task mapping approval | PENDING | Field mapping and task behavior still require approval. |
| No-spam/no-unwanted-contact wording approval | PENDING | Required before public collection. |
| Rollback/disable-contact-flow plan | PENDING | Disable/rollback procedure needs owner sign-off. |
| Support/operator handoff approval | PENDING | Support readiness still pending. |

Current contact-flow launch posture:

- Real contact creation: NOT_APPROVED
- Real lead/customer/task creation: NOT_APPROVED
- Public launch contact flow: PENDING

## C. Real-Site Embed Readiness

Candidate domains/pages from Phase 9CC:

- `https://alte.edu.ge` homepage or approved Georgian admissions/program page.
- `https://join.alte.edu.ge` homepage or approved English/international admissions landing page.

Candidate widget asset:

- `widget/alte-chat-widget.v0.8.js`

Candidate asset host:

- Preferred: Alte website/CMS/static asset hosting controlled by the web team.
- Alternative: approved static asset host such as Cloud Storage/CDN only after a separate owner-approved hosting decision.

Candidate backend API base URL:

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

Candidate production origins:

```text
https://alte.edu.ge
https://join.alte.edu.ge
```

Real-site embed gates:

| Gate | Status | Notes |
| --- | --- | --- |
| Owner approval for real-site embed | PENDING | Required before modifying real site. |
| Web-team approval | PENDING | Exact pages/CMS method not approved in 9CD. |
| Asset hosting/upload approval | PENDING | No asset upload performed. |
| Final widget asset URL | PENDING | `APPROVED_ASSET_HOST` still placeholder in 9CC. |
| CORS/domain checklist | PENDING | Exact final origins and any `www` variants must be confirmed. |
| CORS change approval if needed | PENDING | No CORS change performed in 9CD. |
| Privacy/consent dependency | PENDING | Phase 9CB gates still pending. |
| Real-domain smoke approval | PENDING | Smoke plan exists; execution not approved or run. |
| Rollback owner/sign-off | PENDING | Rollback command exists; owner/web-team sign-off pending. |
| Final public launch approval | PENDING | No explicit GO recorded. |

Real-domain smoke plan after approved embed:

- Confirm widget loads without layout break.
- Confirm widget opens/closes on desktop/mobile.
- Confirm browser calls go only to the production backend.
- Confirm no direct AI provider calls from browser.
- Confirm backend health/API reachability from approved origin.
- Run safe no-write Georgian and English questions.
- Verify public source display and no internal source noise.
- Verify 9BE Academic Calendar behavior.
- Verify 9BF Georgian control behavior.
- Verify 9BG source-display safety.
- Do not create contacts/leads/customers/tasks unless separately approved.
- Verify rollback by removing script tags or reverting page version.

## D. Owner Launch Decision Checklist

Owner must explicitly decide all of the following before any public launch execution:

| Decision item | Current status | Required owner decision |
| --- | --- | --- |
| Privacy notice and consent wording | PENDING | Approve final public copy and URL/location. |
| Contact-flow mode | PENDING | Choose contact-flow disabled, dry-run only, or enabled after legal approval. |
| Real contact write behavior | PENDING | Approve no real write, or approve a controlled real write test. |
| Asset hosting/upload | PENDING | Approve final host and asset upload process. |
| Real-site embed pages | PENDING | Approve exact `alte.edu.ge` / `join.alte.edu.ge` pages. |
| CORS changes | PENDING | Approve only if final domain check requires backend allowlist change. |
| Real-domain smoke test | PENDING | Approve smoke scope and no-write constraints. |
| Rollback readiness | PENDING | Confirm rollback owner and launch-window rollback command. |
| Support/operator handoff | PENDING | Confirm operators/support are ready for live requests. |
| Final public launch GO | PENDING | Must be a later explicit owner GO task. |

## E. Recommended Safe Launch Mode

Recommended first launch mode:

- Chat-only embed first.
- Contact-flow/contact-form writes disabled or not exercised until privacy/legal/contact-write approvals are complete.
- Run real-domain smoke with no contact creation, no real personal data, and no lead/customer/task creation.
- Keep source display and knowledge-answer behavior enabled because backend QA is verified.
- Keep rollback target `alte-ai-crm-backend-00053-pbz` ready during launch window.
- Enable contact-flow later as a separate approval phase after privacy/legal, CRM mapping, operator handoff, and controlled write-test approval.

Rationale:

- Backend QA is complete, but public website, privacy, contact-write, and operator handoff gates are still pending.
- Chat-only smoke verifies the real site integration without introducing personal-data write risk.
- Contact-flow enablement has a larger privacy and operational surface and should remain a separate decision.

## F. Explicit Decision

`FINAL_PREFLIGHT_PREPARED_OWNER_APPROVAL_PENDING_PUBLIC_LAUNCH_NO_GO`

Backend is deployed and verified. The final owner launch package is prepared. Public launch remains `NO-GO` because owner, privacy/legal, contact-flow, real-site embed, real-domain smoke, rollback sign-off, support handoff, and final GO approvals are still pending.

## Safety Confirmations

- Backend deploy performed in this phase: NO
- Rollback performed in this phase: NO
- Real `alte.edu.ge` modified: NO
- Real `join.alte.edu.ge` modified: NO
- Assets uploaded or embedded: NO
- Frontend/Netlify changed: NO
- DB/schema/migration/seed/import changed: NO
- Secret Manager/CORS changed: NO
- Bridge Hub changed: NO
- Contact flow submitted: NO
- Lead/customer/task created: NO
- Secrets/tokens/passwords/DATABASE_URL printed: NO
- Public launch marked GO: NO
