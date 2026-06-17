# Phase 9BJ Dirty Worktree Owner Decision Plan

Plan date: 2026-06-14

Current branch: `phase-9s-agent-preview-cors-note`

Current production backend revision: `alte-ai-crm-backend-00052-mjq`

Current production traffic: `100%` to `alte-ai-crm-backend-00052-mjq`

Current decision state: `BACKEND_DEPLOY_BLOCKED_BILLING_PENDING_RETRY`

Public launch: `NO-GO`

Source audit: `docs/deployment/PHASE_9BI_DIRTY_WORKTREE_AND_DEPLOY_QUEUE_AUDIT.md`

## Deploy Queue Position

Code and docs required for the current backend deploy queue are already committed through Phase 9BE:

- 9BF/9BG implementation: `ece82c6f72d6be4ddec7243b4644b7de75862266`
- 9BF/9BG commit readiness: `551e9db3c4889817a8b8c7fcf885a064ccd68d56`
- 9BH visual QA: `e74e9e0a21ab145d0a49e03c49d4d3bcae2b4bf5`
- 9BF/9BG deploy audit: `c4ef3d9833e1a341b769ba551da3b8336346aeb0`
- Billing retry checklist: `6c6986766bff683c44632be8336acbd13f781993`
- 9BE Academic Calendar fixes: `eb07df605c1609ba1249a070332e25d05809aa28`
- 9BI dirty worktree/deploy queue audit: `c424fcc61c0d27358b7de5fad332e1c9428e51c9`

Billing remains the main deploy blocker. The dirty worktree should still be reconciled before a billing-restored deploy retry so the retry starts from a clean, controlled checkout.

## Current Inventory Scope

This plan covers every Phase 9BI category C, D, and E file. Category A/B generated artifacts are intentionally excluded from the per-file owner-decision table, except where mentioned in summary guidance.

Category C/D/E total: `43`

| Category | Count |
| --- | ---: |
| C relevant deploy/QA docs not committed | 27 |
| D potentially important code/data change not committed | 15 |
| E unknown / requires owner decision | 1 |

## Owner Decision Table

| Path | Status | 9BI category | Likely origin/phase | Risk if left dirty | Recommended action | Owner decision needed | Safe before billing retry |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `README.md` | modified | C | Phase 9X status update | May communicate stale decision state compared with current billing-blocked queue. | preserve for owner review | yes | no |
| `backend/app/tests/test_phase_9ay_program_catalog_source_routing.py` | modified | D | Phase 9AY Program Catalog regression coverage | Useful-looking test coverage can be lost or accidentally bundled with unrelated work; code/test change outside current deploy queue. | investigate before deploy retry | yes | no |
| `docs/NEXT_PHASES.md` | modified | C | Phase 9X next-phase status update | May conflict with current Phase 9BF/9BG/9BE deploy queue and billing-blocked state. | preserve for owner review | yes | no |
| `docs/deployment/FINAL_PREFLIGHT_GATE.md` | modified | C | Phase 9X/preflight status update | Launch/preflight wording is high risk if stale; could confuse GO/NO-GO gates. | preserve for owner review | yes | no |
| `docs/deployment/PHASE_9AN_OWNER_HANDOFF_ASSET_UPLOAD_AND_STAGED_EMBED.md` | modified | C | Phase 9AN handoff doc with later Phase 9AY updates | Old handoff doc mixed with newer verification details may be misleading. | preserve for owner review | yes | no |
| `docs/deployment/PHASE_9AX_FINAL_TECHNICAL_VERIFICATION_SUMMARY.md` | modified | C | Phase 9AX summary with Phase 9AY updates | Historical summary changed after the fact; should be validated before commit. | preserve for owner review | yes | no |
| `docs/deployment/PHASE_9P_PUBLIC_LAUNCH_DECISION.md` | modified | C | Phase 9P launch decision with Phase 9X update | Public launch docs must remain NO-GO and should not be casually edited. | preserve for owner review | yes | no |
| `docs/evaluation/PHASE_9AS_FULL_KNOWLEDGE_COVERAGE_QA_RESULT.md` | modified | C | Phase 9AS production QA rerun | Changes failed-to-passed state; useful but needs provenance check. | commit as historical QA docs | yes | no |
| `docs/evaluation/PHASE_9AS_OPERATOR_CRM_ALIGNMENT_QA_RESULT.md` | modified | C | Phase 9AS operator alignment rerun | Timestamp/result provenance should be confirmed. | commit as historical QA docs | yes | no |
| `docs/evaluation/PHASE_9AT_KNOWLEDGE_FIXES_QA_RESULT.md` | modified | C | Phase 9AT production QA rerun | Timestamp/result provenance should be confirmed. | commit as historical QA docs | yes | no |
| `MANUS_CONTEXT.md` | untracked | E | Unknown local context file | Unknown context may contain planning notes or sensitive/private material; narrow secret-pattern scan did not flag common markers, but contents still need owner review. | preserve for owner review | yes | no |
| `backend/app/scripts/production_kb_source_coverage_qa.py` | untracked | D | Phase 9U/production KB source coverage QA | Production-facing script imports Cloud SQL/Auth libraries; should not be committed or run without owner/safety review. | investigate before deploy retry | yes | no |
| `backend/app/scripts/production_phase_9aq_chat_operator_alignment_qa.py` | untracked | D | Phase 9AQ operator alignment production QA | Production QA script could touch live endpoints if run; commit only after safety review. | investigate before deploy retry | yes | no |
| `backend/app/scripts/verify_phase_9aq_chat_operator_alignment.py` | untracked | D | Phase 9AQ verifier | Likely useful verifier, but historical and not part of current deploy queue. | commit as historical QA docs | yes | no |
| `backend/app/scripts/verify_phase_9as_full_knowledge_operator_verification.py` | untracked | D | Phase 9AS verifier | Likely useful verifier, but historical and not part of current deploy queue. | commit as historical QA docs | yes | no |
| `backend/app/scripts/verify_phase_9ba_program_catalog_file_qa.py` | untracked | D | Phase 9BA verifier | Overlaps Program Catalog file QA provenance; likely useful if paired with 9BA docs/tests. | commit as historical QA docs | yes | no |
| `backend/app/scripts/verify_phase_9bd_academic_calendar_file_qa.py` | untracked | D | Phase 9BD verifier | Overlaps Academic Calendar file QA provenance; likely useful if paired with 9BD docs/tests. | commit as historical QA docs | yes | no |
| `backend/app/scripts/verify_phase_9x_browser_smoke_contact_safety.py` | untracked | D | Phase 9X verifier | Historical browser/contact safety verifier; useful only if Phase 9X docs are retained. | commit as historical QA docs | yes | no |
| `backend/app/tests/test_phase_9aq_chat_operator_alignment.py` | untracked | D | Phase 9AQ tests | Historical test file; can change full pytest surface if committed. | commit as historical QA docs | yes | no |
| `backend/app/tests/test_phase_9as_full_knowledge_operator_verification.py` | untracked | D | Phase 9AS tests | Historical test file; can change full pytest surface if committed. | commit as historical QA docs | yes | no |
| `backend/app/tests/test_phase_9ba_program_catalog_file_qa.py` | untracked | D | Phase 9BA tests | Overlaps Program Catalog file QA; likely useful provenance if committed with matching docs/verifier. | commit as historical QA docs | yes | no |
| `backend/app/tests/test_phase_9bd_academic_calendar_file_qa.py` | untracked | D | Phase 9BD tests | Overlaps Academic Calendar file QA; likely useful provenance if committed with matching docs/verifier. | commit as historical QA docs | yes | no |
| `backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.json` | untracked | C | Phase 9U production KB source coverage result | Located under `backend/docs` rather than root `docs`; may be duplicate/misplaced. | move to archive/docs | yes | no |
| `backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.md` | untracked | C | Phase 9U production KB source coverage result | Located under `backend/docs` rather than root `docs`; may be duplicate/misplaced. | move to archive/docs | yes | no |
| `docs/deployment/FULL_PROJECT_AUDIT_2026_05_30.md` | untracked | C | Full project audit | Useful historical record, but broad scope requires owner acceptance. | preserve for owner review | yes | no |
| `docs/deployment/PHASE_9AO_FULL_CHATBOT_FUNCTIONALITY_QA_RESULT.md` | untracked | C | Phase 9AO QA result | Historical QA record; likely safe to archive/commit after provenance review. | commit as historical QA docs | yes | no |
| `docs/deployment/PHASE_9AQ_CHATBOT_OPERATOR_ALIGNMENT_QA_RESULT.json` | untracked | C | Phase 9AQ QA artifact | Historical JSON artifact; should be paired with markdown doc or archived. | commit as historical QA docs | yes | no |
| `docs/deployment/PHASE_9AQ_CHATBOT_OPERATOR_CRM_ALIGNMENT_QA_RESULT.md` | untracked | C | Phase 9AQ QA result | Historical QA record; likely useful provenance. | commit as historical QA docs | yes | no |
| `docs/deployment/PHASE_9AR_FIX_INFORMATIONAL_HANDOVER_POLLUTION_QA_RESULT.json` | untracked | C | Phase 9AR QA artifact | Historical JSON artifact; should be paired with result docs or archived. | commit as historical QA docs | yes | no |
| `docs/deployment/PHASE_9AS_40_QUESTION_GEORGIAN_CONTROL_QA_RESULT.md` | untracked | C | Phase 9AS Georgian control QA | Source-of-truth input for committed Phase 9BF; should be committed as provenance if approved. | commit as historical QA docs | yes | no |
| `docs/deployment/PHASE_9AS_FULL_KNOWLEDGE_AND_OPERATOR_VERIFICATION_RESULT.md` | untracked | C | Phase 9AS full knowledge/operator verification | Historical verification record; likely useful provenance. | commit as historical QA docs | yes | no |
| `docs/deployment/PHASE_9AY_FINAL_APPROVAL_READINESS_UPDATE.md` | untracked | C | Phase 9AY final approval readiness | May be useful, but should be checked against current billing-blocked deploy queue. | preserve for owner review | yes | no |
| `docs/deployment/PHASE_9X_BROWSER_SMOKE_AND_CONTACT_SAFETY_RESULT.md` | untracked | C | Phase 9X browser smoke/contact safety | Historical browser smoke record; likely useful if Phase 9X status updates are accepted. | commit as historical QA docs | yes | no |
| `docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.csv` | untracked | C | Production KB inventory audit | Useful evidence artifact; commit only if owner accepts repository size/data exposure. | preserve for owner review | yes | no |
| `docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.md` | untracked | C | Production KB inventory audit | Useful evidence doc; pair with CSV decision. | preserve for owner review | yes | no |
| `docs/evaluation/PHASE_9AS_ACTIVE_KNOWLEDGE_INVENTORY.md` | untracked | C | Phase 9AS active knowledge inventory | Historical evaluation inventory; likely useful after review. | commit as historical QA docs | yes | no |
| `docs/evaluation/PHASE_9AW_9AS_CASE_DETAILS.json` | untracked | C | Phase 9AW/9AS case details | Historical evaluation artifact; commit/archive depends on owner preference for JSON evidence. | commit as historical QA docs | yes | no |
| `docs/evaluation/PHASE_9BA_PROGRAM_CATALOG_FILE_QA_RESULT.md` | untracked | C | Phase 9BA Program Catalog file QA | Direct provenance for Program Catalog work; should be committed if approved. | commit as historical QA docs | yes | no |
| `docs/evaluation/PHASE_9BD_ACADEMIC_CALENDAR_FILE_QA_RESULT.md` | untracked | C | Phase 9BD Academic Calendar file QA | Direct provenance for committed Phase 9BE fixes; should be committed if approved. | commit as historical QA docs | yes | no |
| `docs/evaluation/PHASE_9BD_ACADEMIC_CALENDAR_FILE_QA_SET.md` | untracked | C | Phase 9BD Academic Calendar file QA set | Direct provenance for committed Phase 9BE fixes; should be committed if approved. | commit as historical QA docs | yes | no |
| `frontend/package-lock.json` | untracked | D | Frontend local npm install artifact | Likely generated accidentally because no frontend/Netlify change is approved; could imply frontend dependency drift. | ignore/delete after approval | yes | yes |
| `generate_manual.py` | untracked | D | Local Word/manual generator utility | Looks like a local document generator using `python-docx`; unclear project ownership. | preserve for owner review | yes | yes |
| `generate_training.py` | untracked | D | Local training-material generator utility | Looks like a local generation script; unclear project ownership and not deploy-critical. | preserve for owner review | yes | yes |

## Special Decisions

### Program Catalog Test File

`backend/app/tests/test_phase_9ay_program_catalog_source_routing.py` contains useful-looking regression coverage for complete Bachelor program lists in Georgian and English. Because it is a modified tracked test outside the current 9BE deploy queue, the recommended action is owner review before deploy retry:

- If accepted: commit it in a dedicated Program Catalog regression commit and rerun full pytest.
- If rejected: revert it after explicit approval.
- Do not leave it dirty during a billing-restored deploy retry.

### Untracked Scripts And Tests

Most untracked backend scripts/tests are prior-phase verification assets. They do not overlap directly with committed 9BE/9BF/9BG implementation code, but they affect repository/test surface if committed. Recommended grouping:

- Phase 9AQ: commit/archive `production_phase_9aq_chat_operator_alignment_qa.py`, `verify_phase_9aq_chat_operator_alignment.py`, and `test_phase_9aq_chat_operator_alignment.py` together after safety review.
- Phase 9AS: commit/archive `verify_phase_9as_full_knowledge_operator_verification.py` and `test_phase_9as_full_knowledge_operator_verification.py` with matching 9AS docs.
- Phase 9BA: commit `verify_phase_9ba_program_catalog_file_qa.py` and `test_phase_9ba_program_catalog_file_qa.py` with `PHASE_9BA_PROGRAM_CATALOG_FILE_QA_RESULT.md` if owner approves provenance retention.
- Phase 9BD: commit `verify_phase_9bd_academic_calendar_file_qa.py` and `test_phase_9bd_academic_calendar_file_qa.py` with the 9BD QA set/result if owner approves provenance retention.
- Phase 9X: commit/archive `verify_phase_9x_browser_smoke_contact_safety.py` with the Phase 9X browser smoke doc if owner approves.
- `production_kb_source_coverage_qa.py`: investigate before deploy retry because it is production-facing and imports Cloud SQL/Auth libraries.

### Historical Docs

Historical QA/deploy docs are generally useful provenance, but modified launch/status docs should be reviewed before commit because the current state is billing-blocked and public launch remains NO-GO.

### MANUS_CONTEXT.md

`MANUS_CONTEXT.md` remains an unknown local context file. A narrow scan for common secret markers did not flag `password`, `secret`, `token`, `DATABASE_URL`, API key, private key, or credential terms. The file still requires owner review before commit or deletion because it may contain private operational context.

### Frontend Lockfile

`frontend/package-lock.json` is a tiny untracked lockfile and likely came from an accidental/local npm command. Since no frontend/Netlify change is approved, recommended action is delete after approval or intentionally ignore. It does not need to be committed for the backend deploy retry.

### Local Generator Scripts

`generate_manual.py` and `generate_training.py` look like local document/training generators rather than backend deploy assets. Preserve for owner review; do not commit into the backend deploy queue unless the owner confirms they are project utilities.

## Recommendation Buckets

### Safe To Ignore/Delete After Approval

Count: `1`

- `frontend/package-lock.json`

Category A/B generated visual artifacts and generated package locks from Phase 9BI are also safe candidates for ignore/delete after approval, but they are outside this C/D/E table.

### Should Commit Later

Count: `24`

- `docs/evaluation/PHASE_9AS_FULL_KNOWLEDGE_COVERAGE_QA_RESULT.md`
- `docs/evaluation/PHASE_9AS_OPERATOR_CRM_ALIGNMENT_QA_RESULT.md`
- `docs/evaluation/PHASE_9AT_KNOWLEDGE_FIXES_QA_RESULT.md`
- `backend/app/scripts/verify_phase_9aq_chat_operator_alignment.py`
- `backend/app/scripts/verify_phase_9as_full_knowledge_operator_verification.py`
- `backend/app/scripts/verify_phase_9ba_program_catalog_file_qa.py`
- `backend/app/scripts/verify_phase_9bd_academic_calendar_file_qa.py`
- `backend/app/scripts/verify_phase_9x_browser_smoke_contact_safety.py`
- `backend/app/tests/test_phase_9aq_chat_operator_alignment.py`
- `backend/app/tests/test_phase_9as_full_knowledge_operator_verification.py`
- `backend/app/tests/test_phase_9ba_program_catalog_file_qa.py`
- `backend/app/tests/test_phase_9bd_academic_calendar_file_qa.py`
- `docs/deployment/PHASE_9AO_FULL_CHATBOT_FUNCTIONALITY_QA_RESULT.md`
- `docs/deployment/PHASE_9AQ_CHATBOT_OPERATOR_ALIGNMENT_QA_RESULT.json`
- `docs/deployment/PHASE_9AQ_CHATBOT_OPERATOR_CRM_ALIGNMENT_QA_RESULT.md`
- `docs/deployment/PHASE_9AR_FIX_INFORMATIONAL_HANDOVER_POLLUTION_QA_RESULT.json`
- `docs/deployment/PHASE_9AS_40_QUESTION_GEORGIAN_CONTROL_QA_RESULT.md`
- `docs/deployment/PHASE_9AS_FULL_KNOWLEDGE_AND_OPERATOR_VERIFICATION_RESULT.md`
- `docs/deployment/PHASE_9X_BROWSER_SMOKE_AND_CONTACT_SAFETY_RESULT.md`
- `docs/evaluation/PHASE_9AS_ACTIVE_KNOWLEDGE_INVENTORY.md`
- `docs/evaluation/PHASE_9AW_9AS_CASE_DETAILS.json`
- `docs/evaluation/PHASE_9BA_PROGRAM_CATALOG_FILE_QA_RESULT.md`
- `docs/evaluation/PHASE_9BD_ACADEMIC_CALENDAR_FILE_QA_RESULT.md`
- `docs/evaluation/PHASE_9BD_ACADEMIC_CALENDAR_FILE_QA_SET.md`

### Needs Owner Review

Count: `15`

- `README.md`
- `docs/NEXT_PHASES.md`
- `docs/deployment/FINAL_PREFLIGHT_GATE.md`
- `docs/deployment/PHASE_9AN_OWNER_HANDOFF_ASSET_UPLOAD_AND_STAGED_EMBED.md`
- `docs/deployment/PHASE_9AX_FINAL_TECHNICAL_VERIFICATION_SUMMARY.md`
- `docs/deployment/PHASE_9P_PUBLIC_LAUNCH_DECISION.md`
- `MANUS_CONTEXT.md`
- `docs/deployment/FULL_PROJECT_AUDIT_2026_05_30.md`
- `docs/deployment/PHASE_9AY_FINAL_APPROVAL_READINESS_UPDATE.md`
- `docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.csv`
- `docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.md`
- `generate_manual.py`
- `generate_training.py`
- `backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.json`
- `backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.md`

### Must Be Resolved Before Deploy Retry

Count: `40`

All modified tracked files and all untracked backend/app scripts/tests should be resolved before deploy retry. The frontend lockfile and local generator scripts do not affect backend image behavior directly, but they should still have an owner decision before a clean release checkpoint.

Must-resolve list:

- `README.md`
- `backend/app/tests/test_phase_9ay_program_catalog_source_routing.py`
- `docs/NEXT_PHASES.md`
- `docs/deployment/FINAL_PREFLIGHT_GATE.md`
- `docs/deployment/PHASE_9AN_OWNER_HANDOFF_ASSET_UPLOAD_AND_STAGED_EMBED.md`
- `docs/deployment/PHASE_9AX_FINAL_TECHNICAL_VERIFICATION_SUMMARY.md`
- `docs/deployment/PHASE_9P_PUBLIC_LAUNCH_DECISION.md`
- `docs/evaluation/PHASE_9AS_FULL_KNOWLEDGE_COVERAGE_QA_RESULT.md`
- `docs/evaluation/PHASE_9AS_OPERATOR_CRM_ALIGNMENT_QA_RESULT.md`
- `docs/evaluation/PHASE_9AT_KNOWLEDGE_FIXES_QA_RESULT.md`
- `MANUS_CONTEXT.md`
- all untracked `backend/app/scripts/*` listed in this plan
- all untracked `backend/app/tests/*` listed in this plan
- all untracked historical QA docs listed in this plan except `frontend/package-lock.json`, `generate_manual.py`, and `generate_training.py`

### Does Not Block Deploy Retry If Left Uncommitted

Count: `3`

- `frontend/package-lock.json`
- `generate_manual.py`
- `generate_training.py`

These still need an owner decision for repository hygiene, but they are not backend deploy inputs if backend deploy is run from the committed backend queue and no frontend/Netlify change is performed.

## Deploy Retry Readiness Statement

Code needed for the backend deploy queue is already committed through Phase 9BE. Billing remains the primary external blocker.

Dirty files should be reconciled before deploy retry to avoid accidental packaging, accidental commits, or stale status docs. If billing is restored before reconciliation is complete, deploy retry should use a clean checkout or explicitly verified commit SHA, not the current dirty working tree.

Deploy status: `NOT_DEPLOYED_BLOCKED_BY_GCP_BILLING`

Deploy retry readiness: `PENDING_OWNER_DECISIONS_AND_BILLING_RESTORATION`

Public launch remains: `NO-GO`

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
