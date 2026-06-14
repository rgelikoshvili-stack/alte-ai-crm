# Phase 9BN Safe Cleanup Approval Package

Package date: 2026-06-14

Current branch: `phase-9s-agent-preview-cors-note`

Current production backend revision: `alte-ai-crm-backend-00052-mjq`

Current production traffic: `100%` to `alte-ai-crm-backend-00052-mjq`

Current decision state: `BACKEND_DEPLOY_BLOCKED_BILLING_PENDING_RETRY`

Public launch: `NO-GO`

Source report: `docs/deployment/PHASE_9BM_OWNER_REVIEW_FILE_INSPECTION_REPORT.md`

This is an approval package only. No cleanup was performed.

## A. Low-Risk Revert Candidates

These are tracked modified files that Phase 9BM marked safe to revert after approval. They exclude potentially sensitive/private-context files.

Count: `10`

| Path | Reason |
| --- | --- |
| `README.md` | Historical Phase 9X status update appears stale relative to current billing-blocked queue. |
| `docs/NEXT_PHASES.md` | Historical Phase 9X roadmap/status update appears stale. |
| `docs/deployment/FINAL_PREFLIGHT_GATE.md` | Launch/preflight gate wording is sensitive and should not remain dirty. |
| `docs/deployment/PHASE_9AN_OWNER_HANDOFF_ASSET_UPLOAD_AND_STAGED_EMBED.md` | Older handoff doc mixed with later 9AY details. |
| `docs/deployment/PHASE_9AX_FINAL_TECHNICAL_VERIFICATION_SUMMARY.md` | Older verification summary mixed with later 9AY details. |
| `docs/deployment/PHASE_9P_PUBLIC_LAUNCH_DECISION.md` | Public launch decision doc must remain controlled and NO-GO. |
| `docs/deployment/visual_qa/netlify_widget_desktop_1440x900_phase_9ab.png` | Tracked generated screenshot changed locally. |
| `docs/deployment/visual_qa/netlify_widget_mobile_375x667_phase_9ab.png` | Tracked generated screenshot changed locally. |
| `docs/deployment/visual_qa/netlify_widget_mobile_390x844_phase_9ab.png` | Tracked generated screenshot changed locally. |
| `docs/deployment/visual_qa/netlify_widget_mobile_430x932_phase_9ab.png` | Tracked generated screenshot changed locally. |

Exact command plan, after owner approval only:

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

No broad restore commands are approved by this package.

## B. Low-Risk Delete Candidates

These are untracked generated/temp files that Phase 9BM marked safe to delete after approval. They exclude potentially sensitive/private-context files.

Count: `6`

| Path | Reason |
| --- | --- |
| `docs/deployment/visual_qa/netlify_widget_desktop_1440x900.png` | Generated visual QA screenshot not tied to current approved evidence package. |
| `docs/deployment/visual_qa/netlify_widget_desktop_1440x900_wait.png` | Generated visual QA screenshot not tied to current approved evidence package. |
| `docs/deployment/visual_qa/netlify_widget_mobile_430x932.png` | Generated visual QA screenshot not tied to current approved evidence package. |
| `docs/deployment/visual_qa/netlify_widget_mobile_430x932_wait.png` | Generated visual QA screenshot not tied to current approved evidence package. |
| `docs/knowledge_evidence/uploaded_pro_v2_zip_source/deploy/package-lock.json` | Generated npm lockfile inside extracted evidence folder. |
| `frontend/package-lock.json` | Empty/minimal untracked frontend npm lockfile; no frontend/Netlify change is approved. |

Exact command plan, after owner approval only:

```powershell
git clean -f -- docs/deployment/visual_qa/netlify_widget_desktop_1440x900.png
git clean -f -- docs/deployment/visual_qa/netlify_widget_desktop_1440x900_wait.png
git clean -f -- docs/deployment/visual_qa/netlify_widget_mobile_430x932.png
git clean -f -- docs/deployment/visual_qa/netlify_widget_mobile_430x932_wait.png
git clean -f -- docs/knowledge_evidence/uploaded_pro_v2_zip_source/deploy/package-lock.json
git clean -f -- frontend/package-lock.json
```

No `git clean -fd`, wildcard clean, or directory-wide clean is approved by this package.

## C. Commit-Later Candidates

These files were recommended for later commit after owner confirmation. They are not required for the current backend deploy queue and deploy retry can proceed without them if they are removed/archived or kept outside the dirty worktree.

Count: `10`

### Proposed grouping 1: Phase 9AY regression test

Proposed commit message:

```text
phase 9ay: add program catalog list regression tests
```

| Path | Why useful | Deploy retry can proceed without it |
| --- | --- | --- |
| `backend/app/tests/test_phase_9ay_program_catalog_source_routing.py` | Adds complete Bachelor program list regression coverage in Georgian and English. | yes, if reverted or separately committed before retry |

### Proposed grouping 2: Phase 9AQ/9AS historical verifiers and tests

Proposed commit message:

```text
phase 9aq 9as: preserve historical verification tests
```

| Path | Why useful | Deploy retry can proceed without it |
| --- | --- | --- |
| `backend/app/scripts/verify_phase_9aq_chat_operator_alignment.py` | Verifies Phase 9AQ operator alignment docs/results. | yes |
| `backend/app/scripts/verify_phase_9as_full_knowledge_operator_verification.py` | Verifies Phase 9AS full knowledge/operator docs/results. | yes |
| `backend/app/tests/test_phase_9aq_chat_operator_alignment.py` | Regression tests for Phase 9AQ operator alignment evidence. | yes |
| `backend/app/tests/test_phase_9as_full_knowledge_operator_verification.py` | Regression tests for Phase 9AS verification evidence. | yes |

### Proposed grouping 3: Phase 9BA/9BD file QA verifiers and tests

Proposed commit message:

```text
phase 9ba 9bd: preserve file qa verifiers and tests
```

| Path | Why useful | Deploy retry can proceed without it |
| --- | --- | --- |
| `backend/app/scripts/verify_phase_9ba_program_catalog_file_qa.py` | Verifier for committed Program Catalog file QA result. | yes |
| `backend/app/scripts/verify_phase_9bd_academic_calendar_file_qa.py` | Verifier for committed Academic Calendar file QA result/set. | yes |
| `backend/app/tests/test_phase_9ba_program_catalog_file_qa.py` | Tests Program Catalog file QA docs. | yes |
| `backend/app/tests/test_phase_9bd_academic_calendar_file_qa.py` | Tests Academic Calendar file QA docs. | yes |

### Proposed grouping 4: Phase 9X verifier

Proposed commit message:

```text
phase 9x: preserve browser smoke contact safety verifier
```

| Path | Why useful | Deploy retry can proceed without it |
| --- | --- | --- |
| `backend/app/scripts/verify_phase_9x_browser_smoke_contact_safety.py` | Verifier for committed Phase 9X browser smoke/contact safety evidence. | yes |

## D. Sensitive/Manual-Review Hold List

These files must be preserved until owner inspection. Sensitive contents are not printed here.

Count: `11`

| Path | Reason for hold | Recommendation | Deploy retry blocker |
| --- | --- | --- | --- |
| `MANUS_CONTEXT.md` | Unknown local context file; contents not quoted; owner must inspect manually. | owner inspect manually before commit/delete/revert | yes |
| `backend/app/scripts/production_kb_source_coverage_qa.py` | Production-facing QA script; keyword-pattern match present; may use DB/auth/live endpoints. | owner/safety review before commit or delete | yes |
| `backend/app/scripts/production_phase_9aq_chat_operator_alignment_qa.py` | Production-facing QA script; keyword-pattern match present; may call live backend. | owner/safety review before commit or delete | yes |
| `backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.json` | Large production evidence artifact under `backend/docs`; potential metadata exposure/repo size. | owner inspect manually; move/archive/commit/delete decision | yes |
| `backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.md` | Production result summary under `backend/docs`; path decision needed. | owner inspect manually; move/archive/commit/delete decision | yes |
| `docs/deployment/FULL_PROJECT_AUDIT_2026_05_30.md` | Broad project audit; may contain stale or sensitive claims. | owner inspect manually before commit/delete | yes |
| `docs/deployment/PHASE_9AY_FINAL_APPROVAL_READINESS_UPDATE.md` | Approval-readiness doc may be stale relative to billing-blocked deploy queue. | owner inspect manually before commit/delete | yes |
| `docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.csv` | Production KB inventory artifact; possible internal metadata exposure. | owner inspect manually before commit/delete | yes |
| `docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.md` | Production KB inventory document; possible internal metadata exposure. | owner inspect manually before commit/delete | yes |
| `generate_manual.py` | Local generator utility; keyword-pattern match present; unclear project ownership. | keep local only unless owner approves archive/delete | no |
| `generate_training.py` | Local generator utility; keyword-pattern match present; unclear project ownership. | keep local only unless owner approves archive/delete | no |

`frontend/package-lock.json` was moved to the low-risk delete list because it is an empty/minimal generated lockfile and no frontend/Netlify change is approved. Owner approval is still required before deletion.

## E. Proposed Phased Cleanup Order

1. Owner approves the low-risk revert list.
2. Owner approves the low-risk delete list.
3. Execute low-risk cleanup in a separate phase using only the explicit commands above.
4. Re-run:
   - `python -m compileall app`
   - `pytest --basetemp .pytest_tmp_after_low_risk_cleanup`
5. Re-check dirty tree with:
   - `git status --short --branch`
   - `git diff --name-only`
   - `git ls-files --others --exclude-standard`
6. Decide commit-later scripts/tests:
   - commit selected groups in scoped commits, or
   - delete/keep local after approval.
7. Manually inspect sensitive/manual-review hold files.
8. Resolve all deploy blockers or use a clean checkout/verified commit SHA.
9. Only then approve backend deploy retry after billing is restored.

## Approval Checklist

Owner must explicitly approve:

- [ ] Low-risk revert list.
- [ ] Low-risk delete list.
- [ ] Commit-later list and any selected commit grouping.
- [ ] Whether production-facing QA scripts may be committed.
- [ ] Handling for `MANUS_CONTEXT.md`.
- [ ] Handling for production KB inventory/evidence files.
- [ ] Handling for local generator scripts.
- [ ] Confirmation that no frontend/Netlify changes are intended.
- [ ] Backend deploy retry after billing is restored and predeploy checks pass.

## Deploy-Readiness Conclusion

Current backend code queue is committed through Phase 9BE.

Billing remains the external deploy blocker.

The dirty worktree remains a deploy hygiene blocker until cleanup decisions are executed, unless deploy retry is run from a clean checkout or explicitly verified commit SHA.

Production remains unchanged on `alte-ai-crm-backend-00052-mjq` with `100%` traffic.

Public launch remains: `NO-GO`

## Safety Confirmations

- Deploy performed: NO
- GCP billing/cloud build/artifact push retried: NO
- Dirty files modified: NO
- Dirty files deleted/reverted: NO
- Code/test/script/frontend/package-lock/MANUS_CONTEXT changes committed: NO
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
