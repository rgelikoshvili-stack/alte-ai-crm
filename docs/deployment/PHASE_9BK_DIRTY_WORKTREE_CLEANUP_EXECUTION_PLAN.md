# Phase 9BK Dirty Worktree Cleanup Execution Plan

Plan date: 2026-06-14

Current branch: `phase-9s-agent-preview-cors-note`

Current production backend revision: `alte-ai-crm-backend-00052-mjq`

Current production traffic: `100%` to `alte-ai-crm-backend-00052-mjq`

Current decision state: `BACKEND_DEPLOY_BLOCKED_BILLING_PENDING_RETRY`

Public launch: `NO-GO`

Source docs:

- `docs/deployment/PHASE_9BI_DIRTY_WORKTREE_AND_DEPLOY_QUEUE_AUDIT.md`
- `docs/deployment/PHASE_9BJ_DIRTY_WORKTREE_OWNER_DECISION_PLAN.md`

This is a plan only. No dirty files were deleted, reverted, or committed by this plan.

## A. Deploy Queue Summary

Ready but not deployed commits:

| Phase | Commit | Status |
| --- | --- | --- |
| 9BF/9BG implementation | `ece82c6f72d6be4ddec7243b4644b7de75862266` | Ready, not deployed |
| 9BF/9BG commit readiness | `551e9db3c4889817a8b8c7fcf885a064ccd68d56` | Ready, not deployed |
| 9BH visual QA | `e74e9e0a21ab145d0a49e03c49d4d3bcae2b4bf5` | Ready, not deployed |
| 9BF/9BG deploy audit | `c4ef3d9833e1a341b769ba551da3b8336346aeb0` | Recorded blocked deploy attempt |
| Billing retry checklist | `6c6986766bff683c44632be8336acbd13f781993` | Ready for billing-restored retry |
| 9BE Academic Calendar fixes | `eb07df605c1609ba1249a070332e25d05809aa28` | Ready, not deployed |
| 9BI dirty worktree audit | `c424fcc61c0d27358b7de5fad332e1c9428e51c9` | Audit committed |
| 9BJ owner-decision plan | `d69fe2c868f035bbf807b9aad706c47905dafc67` | Owner-decision plan committed |

Billing remains the backend deploy blocker. Production remains unchanged on `alte-ai-crm-backend-00052-mjq` with `100%` traffic.

Public launch remains `NO-GO`.

## B. Cleanup Goals

- Clean the worktree before any billing-restored backend deploy retry.
- Preserve valuable QA/deploy history in scoped commits.
- Avoid committing scratch, cache, generated screenshots, generated lockfiles, or local utility files by accident.
- Avoid losing potentially important owner files by requiring explicit approval before delete/revert actions.
- Keep the deploy queue commits intact and avoid changing backend deploy scope.

## C. Proposed Action Buckets

### Bucket 1 - Commit As Historical QA/Deploy Docs

Proposed commit message:

```text
phase 9 historical: record qa and deployment evidence
```

Files:

| Path | Why commit |
| --- | --- |
| `docs/evaluation/PHASE_9AS_FULL_KNOWLEDGE_COVERAGE_QA_RESULT.md` | Records later 9AS full knowledge PASS result. |
| `docs/evaluation/PHASE_9AS_OPERATOR_CRM_ALIGNMENT_QA_RESULT.md` | Records later 9AS operator alignment timestamp/result. |
| `docs/evaluation/PHASE_9AT_KNOWLEDGE_FIXES_QA_RESULT.md` | Records later 9AT production QA timestamp/result. |
| `docs/deployment/PHASE_9AO_FULL_CHATBOT_FUNCTIONALITY_QA_RESULT.md` | Historical Phase 9AO QA result. |
| `docs/deployment/PHASE_9AQ_CHATBOT_OPERATOR_ALIGNMENT_QA_RESULT.json` | Historical Phase 9AQ QA artifact. |
| `docs/deployment/PHASE_9AQ_CHATBOT_OPERATOR_CRM_ALIGNMENT_QA_RESULT.md` | Historical Phase 9AQ QA result. |
| `docs/deployment/PHASE_9AR_FIX_INFORMATIONAL_HANDOVER_POLLUTION_QA_RESULT.json` | Historical Phase 9AR QA artifact. |
| `docs/deployment/PHASE_9AS_40_QUESTION_GEORGIAN_CONTROL_QA_RESULT.md` | Source report for committed Phase 9BF Georgian control fixes. |
| `docs/deployment/PHASE_9AS_FULL_KNOWLEDGE_AND_OPERATOR_VERIFICATION_RESULT.md` | Historical Phase 9AS full knowledge/operator verification. |
| `docs/deployment/PHASE_9X_BROWSER_SMOKE_AND_CONTACT_SAFETY_RESULT.md` | Historical Phase 9X browser smoke/contact safety result. |
| `docs/evaluation/PHASE_9AS_ACTIVE_KNOWLEDGE_INVENTORY.md` | Historical Phase 9AS active knowledge inventory. |
| `docs/evaluation/PHASE_9AW_9AS_CASE_DETAILS.json` | Historical Phase 9AW/9AS case detail artifact. |
| `docs/evaluation/PHASE_9BA_PROGRAM_CATALOG_FILE_QA_RESULT.md` | Program Catalog file QA provenance. |
| `docs/evaluation/PHASE_9BD_ACADEMIC_CALENDAR_FILE_QA_RESULT.md` | Academic Calendar file QA provenance for Phase 9BE. |
| `docs/evaluation/PHASE_9BD_ACADEMIC_CALENDAR_FILE_QA_SET.md` | Academic Calendar QA set provenance for Phase 9BE. |

Risk:

- Some docs are historical and may not reflect the current billing-blocked decision state. The commit should be clearly framed as historical evidence only.

### Bucket 2 - Commit As Tests/Scripts Only After Owner Confirms

These files may be useful, but they change the repository test/script surface and should be committed only after owner approval and a full test run.

| Path | Phase inferred | Why useful | Risk | Proposed commit message |
| --- | --- | --- | --- | --- |
| `backend/app/tests/test_phase_9ay_program_catalog_source_routing.py` | 9AY | Adds useful Program Catalog Bachelor list regression coverage. | Modified tracked test outside current 9BE deploy scope; may be stale/local-only. | `phase 9ay: add program catalog list regression tests` |
| `backend/app/scripts/production_kb_source_coverage_qa.py` | 9U / production KB | Production KB source coverage QA utility. | Production-facing and imports Cloud SQL/Auth libraries; needs safety review before commit or run. | `phase 9u: add production kb source coverage qa script` |
| `backend/app/scripts/production_phase_9aq_chat_operator_alignment_qa.py` | 9AQ | Production operator alignment QA utility. | Production-facing; must not be run without explicit approval. | `phase 9aq: add operator alignment qa script` |
| `backend/app/scripts/verify_phase_9aq_chat_operator_alignment.py` | 9AQ | Local verifier for 9AQ docs/results. | Historical verifier outside current deploy queue. | `phase 9aq: add operator alignment verifier` |
| `backend/app/scripts/verify_phase_9as_full_knowledge_operator_verification.py` | 9AS | Local verifier for 9AS full knowledge/operator verification. | Historical verifier outside current deploy queue. | `phase 9as: add full knowledge operator verifier` |
| `backend/app/scripts/verify_phase_9ba_program_catalog_file_qa.py` | 9BA | Verifier for Program Catalog file QA. | Should be paired with 9BA docs/tests. | `phase 9ba: add program catalog file qa verifier` |
| `backend/app/scripts/verify_phase_9bd_academic_calendar_file_qa.py` | 9BD | Verifier for Academic Calendar file QA. | Should be paired with 9BD docs/tests. | `phase 9bd: add academic calendar file qa verifier` |
| `backend/app/scripts/verify_phase_9x_browser_smoke_contact_safety.py` | 9X | Verifier for browser smoke/contact safety docs. | Historical verifier outside current deploy queue. | `phase 9x: add browser smoke contact safety verifier` |
| `backend/app/tests/test_phase_9aq_chat_operator_alignment.py` | 9AQ | Regression tests for operator alignment. | Changes full pytest surface. | `phase 9aq: add chat operator alignment tests` |
| `backend/app/tests/test_phase_9as_full_knowledge_operator_verification.py` | 9AS | Regression tests for 9AS verification docs. | Changes full pytest surface. | `phase 9as: add full knowledge operator verification tests` |
| `backend/app/tests/test_phase_9ba_program_catalog_file_qa.py` | 9BA | Regression tests for Program Catalog file QA docs. | Changes full pytest surface. | `phase 9ba: add program catalog file qa tests` |
| `backend/app/tests/test_phase_9bd_academic_calendar_file_qa.py` | 9BD | Regression tests for Academic Calendar file QA docs. | Changes full pytest surface. | `phase 9bd: add academic calendar file qa tests` |

### Bucket 3 - Revert Tracked Modifications After Approval

These tracked modifications look stale, status-only, local-only, or generated. They should be reverted only after explicit owner approval.

| Path | Reason |
| --- | --- |
| `README.md` | Historical Phase 9X status update appears stale relative to current billing-blocked state. |
| `docs/NEXT_PHASES.md` | Historical Phase 9X status update appears stale relative to current queue. |
| `docs/deployment/FINAL_PREFLIGHT_GATE.md` | Launch/preflight gate wording is sensitive and should not remain dirty. |
| `docs/deployment/PHASE_9AN_OWNER_HANDOFF_ASSET_UPLOAD_AND_STAGED_EMBED.md` | Older handoff doc mixed with later 9AY status. |
| `docs/deployment/PHASE_9AX_FINAL_TECHNICAL_VERIFICATION_SUMMARY.md` | Older summary doc mixed with later 9AY status. |
| `docs/deployment/PHASE_9P_PUBLIC_LAUNCH_DECISION.md` | Public launch decision doc is sensitive and must remain NO-GO. |
| `docs/deployment/visual_qa/netlify_widget_desktop_1440x900_phase_9ab.png` | Tracked generated screenshot changed locally. |
| `docs/deployment/visual_qa/netlify_widget_mobile_375x667_phase_9ab.png` | Tracked generated screenshot changed locally. |
| `docs/deployment/visual_qa/netlify_widget_mobile_390x844_phase_9ab.png` | Tracked generated screenshot changed locally. |
| `docs/deployment/visual_qa/netlify_widget_mobile_430x932_phase_9ab.png` | Tracked generated screenshot changed locally. |

Note: `backend/app/tests/test_phase_9ay_program_catalog_source_routing.py` is not included in this revert bucket because it may contain useful regression coverage. It belongs in Bucket 2 pending owner decision.

### Bucket 4 - Delete Untracked Temp/Cache/Generated Files After Approval

These appear generated or misplaced. Delete only after approval using explicit paths.

| Path | Reason |
| --- | --- |
| `docs/deployment/visual_qa/netlify_widget_desktop_1440x900.png` | Generated visual QA screenshot. |
| `docs/deployment/visual_qa/netlify_widget_desktop_1440x900_wait.png` | Generated visual QA screenshot. |
| `docs/deployment/visual_qa/netlify_widget_mobile_430x932.png` | Generated visual QA screenshot. |
| `docs/deployment/visual_qa/netlify_widget_mobile_430x932_wait.png` | Generated visual QA screenshot. |
| `docs/knowledge_evidence/uploaded_pro_v2_zip_source/deploy/package-lock.json` | Generated lockfile inside extracted evidence folder. |

### Bucket 5 - Owner Must Inspect Manually Before Any Action

These files are unknown, potentially sensitive, frontend-related, broad-scope, or local utility files. Do not commit/delete/revert until the owner chooses.

| Path | Reason |
| --- | --- |
| `MANUS_CONTEXT.md` | Unknown local context file. Narrow secret-pattern scan in 9BJ did not flag common markers, but owner review is still required. |
| `generate_manual.py` | Local document/manual generator utility; project ownership unclear. |
| `generate_training.py` | Local training-material generator utility; project ownership unclear. |
| `frontend/package-lock.json` | Untracked frontend lockfile; likely accidental local npm artifact, but frontend owner should confirm before delete. |
| `docs/deployment/FULL_PROJECT_AUDIT_2026_05_30.md` | Broad project audit; owner should decide whether to preserve. |
| `docs/deployment/PHASE_9AY_FINAL_APPROVAL_READINESS_UPDATE.md` | Approval-readiness doc may be useful but must be checked against current billing-blocked state. |
| `docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.csv` | Production KB inventory artifact; owner should decide data exposure/repo size. |
| `docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.md` | Production KB inventory doc; pair with CSV decision. |
| `backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.json` | Located under `backend/docs`; owner should decide whether to move/archive or delete. |
| `backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.md` | Located under `backend/docs`; owner should decide whether to move/archive or delete. |

## D. Exact Recommended Command Plan

Do not run these commands until the owner approves each bucket. All commands use explicit paths only. No `git reset --hard`, no broad `git clean -fd`, and no wildcard delete.

### 1. Commit Historical QA/Deploy Docs

```powershell
git add docs/evaluation/PHASE_9AS_FULL_KNOWLEDGE_COVERAGE_QA_RESULT.md
git add docs/evaluation/PHASE_9AS_OPERATOR_CRM_ALIGNMENT_QA_RESULT.md
git add docs/evaluation/PHASE_9AT_KNOWLEDGE_FIXES_QA_RESULT.md
git add docs/deployment/PHASE_9AO_FULL_CHATBOT_FUNCTIONALITY_QA_RESULT.md
git add docs/deployment/PHASE_9AQ_CHATBOT_OPERATOR_ALIGNMENT_QA_RESULT.json
git add docs/deployment/PHASE_9AQ_CHATBOT_OPERATOR_CRM_ALIGNMENT_QA_RESULT.md
git add docs/deployment/PHASE_9AR_FIX_INFORMATIONAL_HANDOVER_POLLUTION_QA_RESULT.json
git add docs/deployment/PHASE_9AS_40_QUESTION_GEORGIAN_CONTROL_QA_RESULT.md
git add docs/deployment/PHASE_9AS_FULL_KNOWLEDGE_AND_OPERATOR_VERIFICATION_RESULT.md
git add docs/deployment/PHASE_9X_BROWSER_SMOKE_AND_CONTACT_SAFETY_RESULT.md
git add docs/evaluation/PHASE_9AS_ACTIVE_KNOWLEDGE_INVENTORY.md
git add docs/evaluation/PHASE_9AW_9AS_CASE_DETAILS.json
git add docs/evaluation/PHASE_9BA_PROGRAM_CATALOG_FILE_QA_RESULT.md
git add docs/evaluation/PHASE_9BD_ACADEMIC_CALENDAR_FILE_QA_RESULT.md
git add docs/evaluation/PHASE_9BD_ACADEMIC_CALENDAR_FILE_QA_SET.md
git diff --cached --name-only
git commit -m "phase 9 historical: record qa and deployment evidence"
```

### 2. Commit Selected Tests/Scripts

Only after owner confirms exact files:

```powershell
git add backend/app/tests/test_phase_9ay_program_catalog_source_routing.py
git add backend/app/scripts/verify_phase_9ba_program_catalog_file_qa.py
git add backend/app/tests/test_phase_9ba_program_catalog_file_qa.py
git add backend/app/scripts/verify_phase_9bd_academic_calendar_file_qa.py
git add backend/app/tests/test_phase_9bd_academic_calendar_file_qa.py
git diff --cached --name-only
git commit -m "phase 9ba 9bd: preserve file qa verifiers and tests"
```

Production-facing scripts require a separate approval:

```powershell
git add backend/app/scripts/production_kb_source_coverage_qa.py
git add backend/app/scripts/production_phase_9aq_chat_operator_alignment_qa.py
git diff --cached --name-only
git commit -m "phase 9 production qa: preserve reviewed qa scripts"
```

### 3. Revert Tracked Stale/Generated Modifications

Only after owner approval:

```powershell
git restore -- README.md
git restore -- docs/NEXT_PHASES.md
git restore -- docs/deployment/FINAL_PREFLIGHT_GATE.md
git restore -- docs/deployment/PHASE_9AN_OWNER_HANDOFF_ASSET_UPLOAD_AND_STAGED_EMBED.md
git restore -- docs/deployment/PHASE_9AX_FINAL_TECHNICAL_VERIFICATION_SUMMARY.md
git restore -- docs/deployment/PHASE_9P_PUBLIC_LAUNCH_DECISION.md
git restore -- docs/deployment/visual_qa/netlify_widget_desktop_1440x900_phase_9ab.png
git restore -- docs/deployment/visual_qa/netlify_widget_mobile_375x667_phase_9ab.png
git restore -- docs/deployment/visual_qa/netlify_widget_mobile_390x844_phase_9ab.png
git restore -- docs/deployment/visual_qa/netlify_widget_mobile_430x932_phase_9ab.png
```

### 4. Delete Generated/Temp Untracked Files

Only after owner approval:

```powershell
git clean -f -- docs/deployment/visual_qa/netlify_widget_desktop_1440x900.png
git clean -f -- docs/deployment/visual_qa/netlify_widget_desktop_1440x900_wait.png
git clean -f -- docs/deployment/visual_qa/netlify_widget_mobile_430x932.png
git clean -f -- docs/deployment/visual_qa/netlify_widget_mobile_430x932_wait.png
git clean -f -- docs/knowledge_evidence/uploaded_pro_v2_zip_source/deploy/package-lock.json
```

### 5. Manual Owner Inspection Files

No command should be run until the owner decides:

```powershell
# owner review required before any action
# MANUS_CONTEXT.md
# generate_manual.py
# generate_training.py
# frontend/package-lock.json
# docs/deployment/FULL_PROJECT_AUDIT_2026_05_30.md
# docs/deployment/PHASE_9AY_FINAL_APPROVAL_READINESS_UPDATE.md
# docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.csv
# docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.md
# backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.json
# backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.md
```

### 6. Final Verification After Approved Cleanup

```powershell
git status --short --branch
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\python.exe -m compileall app
.\.venv\Scripts\python.exe -m pytest --basetemp .pytest_tmp_dirty_cleanup_final
```

## E. Deploy Retry Readiness After Cleanup

Clean enough for billing-restored backend deploy retry means:

- No unresolved category D or E files remain dirty/untracked.
- Approved historical docs are committed in scoped doc commits.
- Approved tests/scripts are committed in scoped test/script commits and full pytest passes.
- Approved generated/temp files are deleted or ignored.
- Deploy queue commits from 9BF/9BG through 9BE remain intact.
- Current production remains unchanged until an explicitly approved retry.
- Billing is restored separately.

Deploy retry should still be executed from a clean checkout or explicitly verified commit SHA.

## F. Approval Checklist

Owner decisions required:

- [ ] Approve Bucket 1 doc-only historical QA/deploy commit.
- [ ] Approve selected Bucket 2 tests/scripts commit.
- [ ] Approve whether production-facing QA scripts may be committed.
- [ ] Approve Bucket 3 tracked revert list.
- [ ] Approve Bucket 4 untracked delete list.
- [ ] Review and decide Bucket 5 manual inspection files.
- [ ] Confirm no frontend/Netlify changes are intended.
- [ ] Confirm billing is restored.
- [ ] Approve backend deploy retry after cleanup and predeploy tests.

## Safety Confirmations

- Deploy performed: NO
- GCP billing/cloud build/artifact push retried: NO
- Dirty files deleted/reverted: NO
- Dirty code/test/docs committed by this plan: NO
- Real `alte.edu.ge` modified: NO
- Real `join.alte.edu.ge` modified: NO
- Assets uploaded or embedded: NO
- Frontend/Netlify changed: NO
- DB/schema/migration/seed/import changed: NO
- Secret Manager/CORS/Bridge Hub changed: NO
- Contact flow submitted: NO
- Lead/customer/task created: NO
- Secrets/tokens/passwords/DATABASE_URL printed: NO
- Public launch marked GO: NO

Public launch remains: `NO-GO`
