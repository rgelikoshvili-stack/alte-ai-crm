# Phase 9BI Dirty Worktree And Deploy Queue Audit

Audit date: 2026-06-12

Current branch: `phase-9s-agent-preview-cors-note`

Current production backend revision: `alte-ai-crm-backend-00052-mjq`

Current production traffic: `100%` to `alte-ai-crm-backend-00052-mjq`

Current decision state: `BACKEND_DEPLOY_BLOCKED_BILLING_PENDING_RETRY`

Public launch: `NO-GO`

## Deploy Queue

Ready but not deployed commits:

| Phase | Commit | Summary |
| --- | --- | --- |
| 9BF/9BG implementation | `ece82c6f72d6be4ddec7243b4644b7de75862266` | Georgian control fixes and public source display cleanup |
| 9BF/9BG commit readiness | `551e9db3c4889817a8b8c7fcf885a064ccd68d56` | Commit readiness record |
| 9BH visual QA | `e74e9e0a21ab145d0a49e03c49d4d3bcae2b4bf5` | Widget artifact/browser visual QA record |
| 9BF/9BG deploy audit | `c4ef3d9833e1a341b769ba551da3b8336346aeb0` | Production deploy attempt/audit record |
| Billing retry checklist | `6c6986766bff683c44632be8336acbd13f781993` | Billing-restored deploy retry checklist |
| 9BE Academic Calendar fixes | `eb07df605c1609ba1249a070332e25d05809aa28` | Academic Calendar routing and exact-date fixes |

## Deploy Blocker

Backend deploy remains blocked by GCP billing:

- Cloud Build was blocked before upload because billing is disabled/delinquent.
- Artifact Registry push was blocked because billing is required for project `226875230147`.
- No new backend revision was deployed.
- Production remains unchanged.
- Production QA after deploy has not been run because no deploy completed.

Do not retry deploy, Cloud Build, or Artifact Registry push until billing is restored and retry is explicitly approved.

## Dirty And Untracked Inventory

Source commands:

- `git status --short --branch`
- `git diff --name-only`
- `git ls-files --others --exclude-standard`

Total remaining dirty/untracked paths: `52`

Category counts:

| Category | Count | Meaning |
| --- | ---: | --- |
| A | 1 | Already committed / duplicate / safe generated artifact |
| B | 8 | Local cache/temp/test output that should not be committed by default |
| C | 27 | Relevant deploy/QA docs not committed |
| D | 15 | Potentially important code/data change not committed |
| E | 1 | Unknown / requires owner decision |

## Classification Table

| Path | State | Category | Recommended action | Notes |
| --- | --- | --- | --- | --- |
| `README.md` | modified | C | needs owner review | Historical status update appears related to Phase 9X; do not include in deploy retry without confirming it is current. |
| `backend/app/tests/test_phase_9ay_program_catalog_source_routing.py` | modified | D | needs owner review | Uncommitted test additions for Program Catalog behavior; code/test change outside 9BE. |
| `docs/NEXT_PHASES.md` | modified | C | needs owner review | Phase 9X status update; verify against current blocked billing state before committing. |
| `docs/deployment/FINAL_PREFLIGHT_GATE.md` | modified | C | needs owner review | Launch/preflight status update; verify it does not supersede current NO-GO/billing-blocked state incorrectly. |
| `docs/deployment/PHASE_9AN_OWNER_HANDOFF_ASSET_UPLOAD_AND_STAGED_EMBED.md` | modified | C | needs owner review | Adds later Program Catalog verification details to an older owner handoff doc. |
| `docs/deployment/PHASE_9AX_FINAL_TECHNICAL_VERIFICATION_SUMMARY.md` | modified | C | needs owner review | Adds Phase 9AY verification to an older Phase 9AX summary. |
| `docs/deployment/PHASE_9P_PUBLIC_LAUNCH_DECISION.md` | modified | C | needs owner review | Public launch doc changes must be reviewed carefully; public launch remains NO-GO. |
| `docs/deployment/visual_qa/netlify_widget_desktop_1440x900_phase_9ab.png` | modified | B | delete or restore after approval | Tracked binary visual artifact changed by a small byte delta; likely local regenerated screenshot. |
| `docs/deployment/visual_qa/netlify_widget_mobile_375x667_phase_9ab.png` | modified | B | delete or restore after approval | Tracked binary visual artifact; no automatic commit. |
| `docs/deployment/visual_qa/netlify_widget_mobile_390x844_phase_9ab.png` | modified | B | delete or restore after approval | Tracked binary visual artifact; no automatic commit. |
| `docs/deployment/visual_qa/netlify_widget_mobile_430x932_phase_9ab.png` | modified | B | delete or restore after approval | Tracked binary visual artifact changed by a small byte delta; likely local regenerated screenshot. |
| `docs/evaluation/PHASE_9AS_FULL_KNOWLEDGE_COVERAGE_QA_RESULT.md` | modified | C | needs owner review | Production QA result changed from failed to passed; verify provenance before commit. |
| `docs/evaluation/PHASE_9AS_OPERATOR_CRM_ALIGNMENT_QA_RESULT.md` | modified | C | needs owner review | Timestamp/result doc update. |
| `docs/evaluation/PHASE_9AT_KNOWLEDGE_FIXES_QA_RESULT.md` | modified | C | needs owner review | Timestamp/result doc update. |
| `MANUS_CONTEXT.md` | untracked | E | needs owner review | Unknown local context file. Do not commit without owner approval. |
| `backend/app/scripts/production_kb_source_coverage_qa.py` | untracked | D | needs owner review | Potential production QA script. Do not commit without confirming phase ownership and safety. |
| `backend/app/scripts/production_phase_9aq_chat_operator_alignment_qa.py` | untracked | D | needs owner review | Potential production QA script. Do not commit without confirming phase ownership and safety. |
| `backend/app/scripts/verify_phase_9aq_chat_operator_alignment.py` | untracked | D | needs owner review | Verification script for older phase. |
| `backend/app/scripts/verify_phase_9as_full_knowledge_operator_verification.py` | untracked | D | needs owner review | Verification script for older phase. |
| `backend/app/scripts/verify_phase_9ba_program_catalog_file_qa.py` | untracked | D | needs owner review | Verification script for Program Catalog file QA. |
| `backend/app/scripts/verify_phase_9bd_academic_calendar_file_qa.py` | untracked | D | needs owner review | Verification script for Phase 9BD. |
| `backend/app/scripts/verify_phase_9x_browser_smoke_contact_safety.py` | untracked | D | needs owner review | Verification script for Phase 9X. |
| `backend/app/tests/test_phase_9aq_chat_operator_alignment.py` | untracked | D | needs owner review | Test file for older phase. |
| `backend/app/tests/test_phase_9as_full_knowledge_operator_verification.py` | untracked | D | needs owner review | Test file for older phase. |
| `backend/app/tests/test_phase_9ba_program_catalog_file_qa.py` | untracked | D | needs owner review | Test file for Program Catalog file QA. |
| `backend/app/tests/test_phase_9bd_academic_calendar_file_qa.py` | untracked | D | needs owner review | Test file for Academic Calendar file QA. |
| `backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.json` | untracked | C | needs owner review | Deployment/QA result under `backend/docs`; may be duplicate or misplaced relative to root `docs/`. |
| `backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.md` | untracked | C | needs owner review | Deployment/QA result under `backend/docs`; may be duplicate or misplaced relative to root `docs/`. |
| `docs/deployment/FULL_PROJECT_AUDIT_2026_05_30.md` | untracked | C | needs owner review | Project audit doc; not part of current deploy retry queue. |
| `docs/deployment/PHASE_9AO_FULL_CHATBOT_FUNCTIONALITY_QA_RESULT.md` | untracked | C | needs owner review | Historical QA result doc. |
| `docs/deployment/PHASE_9AQ_CHATBOT_OPERATOR_ALIGNMENT_QA_RESULT.json` | untracked | C | needs owner review | Historical QA result artifact. |
| `docs/deployment/PHASE_9AQ_CHATBOT_OPERATOR_CRM_ALIGNMENT_QA_RESULT.md` | untracked | C | needs owner review | Historical QA result doc. |
| `docs/deployment/PHASE_9AR_FIX_INFORMATIONAL_HANDOVER_POLLUTION_QA_RESULT.json` | untracked | C | needs owner review | Historical QA result artifact. |
| `docs/deployment/PHASE_9AS_40_QUESTION_GEORGIAN_CONTROL_QA_RESULT.md` | untracked | C | needs owner review | Source report for Phase 9BF; likely useful provenance but already superseded by committed 9BF docs. |
| `docs/deployment/PHASE_9AS_FULL_KNOWLEDGE_AND_OPERATOR_VERIFICATION_RESULT.md` | untracked | C | needs owner review | Historical verification result doc. |
| `docs/deployment/PHASE_9AY_FINAL_APPROVAL_READINESS_UPDATE.md` | untracked | C | needs owner review | Phase 9AY readiness doc; confirm current applicability. |
| `docs/deployment/PHASE_9X_BROWSER_SMOKE_AND_CONTACT_SAFETY_RESULT.md` | untracked | C | needs owner review | Phase 9X browser smoke result; potentially useful but not part of current 9BE commit. |
| `docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.csv` | untracked | C | needs owner review | Production KB inventory artifact. |
| `docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.md` | untracked | C | needs owner review | Production KB inventory doc. |
| `docs/deployment/visual_qa/netlify_widget_desktop_1440x900.png` | untracked | B | delete after approval or commit only with visual QA owner approval | Generated visual QA screenshot. |
| `docs/deployment/visual_qa/netlify_widget_desktop_1440x900_wait.png` | untracked | B | delete after approval or commit only with visual QA owner approval | Generated visual QA screenshot. |
| `docs/deployment/visual_qa/netlify_widget_mobile_430x932.png` | untracked | B | delete after approval or commit only with visual QA owner approval | Generated visual QA screenshot. |
| `docs/deployment/visual_qa/netlify_widget_mobile_430x932_wait.png` | untracked | B | delete after approval or commit only with visual QA owner approval | Generated visual QA screenshot. |
| `docs/evaluation/PHASE_9AS_ACTIVE_KNOWLEDGE_INVENTORY.md` | untracked | C | needs owner review | Knowledge inventory doc. |
| `docs/evaluation/PHASE_9AW_9AS_CASE_DETAILS.json` | untracked | C | needs owner review | Evaluation detail artifact. |
| `docs/evaluation/PHASE_9BA_PROGRAM_CATALOG_FILE_QA_RESULT.md` | untracked | C | needs owner review | Program Catalog file QA result; likely useful provenance. |
| `docs/evaluation/PHASE_9BD_ACADEMIC_CALENDAR_FILE_QA_RESULT.md` | untracked | C | needs owner review | Academic Calendar file QA result; source provenance for 9BE. |
| `docs/evaluation/PHASE_9BD_ACADEMIC_CALENDAR_FILE_QA_SET.md` | untracked | C | needs owner review | Academic Calendar file QA set; source provenance for 9BE. |
| `docs/knowledge_evidence/uploaded_pro_v2_zip_source/deploy/package-lock.json` | untracked | A | ignore or add to `.gitignore` later | Generated package lock inside extracted evidence/source folder. |
| `frontend/package-lock.json` | untracked | D | needs owner review | Frontend dependency lockfile; do not commit without frontend owner approval. |
| `generate_manual.py` | untracked | D | needs owner review | Unknown generated/manual tooling script. |
| `generate_training.py` | untracked | D | needs owner review | Unknown generated/training tooling script. |

## Risks

- The worktree is not clean. A deploy retry from this checkout could accidentally package or commit unrelated changes if not controlled.
- Several docs update historical decision states. They may be useful records, but some are stale relative to the current billing-blocked deploy queue and must be reviewed before committing.
- One modified tracked test file and multiple untracked scripts/tests are code changes outside Phase 9BE. They should not be bundled into a billing-restored deploy retry without explicit owner approval.
- Modified tracked screenshots and untracked screenshots should not be committed unless they are intentionally part of a visual QA evidence package.
- The current deploy queue itself is already represented by committed changes through Phase 9BE; the remaining dirty/untracked files are not required for the backend billing retry unless separately approved.

## Recommended Cleanup Path Before Billing-Restored Deploy Retry

1. Keep the committed deploy queue intact:
   - 9BF/9BG implementation and readiness
   - 9BH visual QA
   - deploy audit and billing retry checklist
   - 9BE Academic Calendar fixes
2. Do not deploy from a tree with unrelated dirty files.
3. Ask the owner to decide which category C and D files should become separate provenance commits.
4. After owner approval, either commit selected docs/scripts/tests in scoped phase commits or restore/delete them explicitly.
5. Add generated lockfiles/screenshots to `.gitignore` later only after confirming repo conventions.
6. Re-run predeploy tests after the tree is clean and before any billing-restored backend deploy retry.

## Deploy Retry Readiness

Deploy retry readiness status: `BLOCKED_PENDING_DIRTY_TREE_RECONCILIATION_AND_GCP_BILLING_RESTORATION`

Billing status: `NOT_RESTORED_IN_THIS_TASK`

Backend deploy status: `NOT_DEPLOYED_BLOCKED_BY_GCP_BILLING`

Production status: unchanged.

Public launch: `NO-GO`

## Safety Confirmations

- Real `alte.edu.ge` modified: NO
- Real `join.alte.edu.ge` modified: NO
- Assets uploaded or embedded to real site: NO
- Frontend/Netlify changed or deployed: NO
- DB/schema/migration/seed/import changed: NO
- Secret Manager changed: NO
- CORS changed: NO
- Bridge Hub changed: NO
- Contact flow submitted: NO
- Lead/customer/task created: NO
- Secrets/tokens/passwords/DATABASE_URL printed: NO
- Public launch marked GO: NO
