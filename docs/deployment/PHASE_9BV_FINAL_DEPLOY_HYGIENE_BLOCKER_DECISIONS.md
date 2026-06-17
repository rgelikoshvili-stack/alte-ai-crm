# Phase 9BV Final Deploy Hygiene Blocker Decisions

Date: 2026-06-14

Branch: `phase-9s-agent-preview-cors-note`

Current production revision: `alte-ai-crm-backend-00052-mjq`

Traffic: 100% to `alte-ai-crm-backend-00052-mjq`

Current status: `NOT_DEPLOYED_DEPLOY_HYGIENE_BLOCKERS_REMAIN_BILLING_NOT_CONFIRMED`

Public launch: `NO-GO`

## Scope

This package gives owner-safe decisions for the remaining dirty worktree files after Phases 9BQ, 9BR, 9BS, 9BT, and 9BU.

No blocker file was modified, deleted, reverted, staged, or committed. No sensitive/private content was copied into this document.

## Current Dirty Summary

- Modified tracked files: 1
- Untracked files: 15
- Backend deploy retry from this checkout: NO, until owner decisions are executed or a clean verified checkout is used.

## Blocker Decision Table

| Path | Tracked/untracked | Current status | Origin/phase | Sensitivity risk | Deploy-hygiene blocker | Recommended action | Exact command if owner approves | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `backend/app/tests/test_phase_9ay_program_catalog_source_routing.py` | tracked | modified | Phase 9AY / Program Catalog regression | none | yes | commit now | `git add backend/app/tests/test_phase_9ay_program_catalog_source_routing.py` | Safe test-only change. Adds Georgian and English assertions that Bachelor program-list answers include all 10 catalog programs and do not expose source/page noise. Validate with compileall, full pytest, and focused Program Catalog tests after commit. |
| `backend/app/scripts/verify_phase_9x_browser_smoke_contact_safety.py` | untracked | new | Phase 9X browser smoke/contact safety verifier | low | yes | delete after owner approval, or fix in separate phase | `git clean -f -- backend/app/scripts/verify_phase_9x_browser_smoke_contact_safety.py` | Do not commit as-is. Phase 9BR direct run failed on a stale/current contact-safety assertion: `Forbidden premature contact request string found: Please confirm your contact details`. |
| `MANUS_CONTEXT.md` | untracked | new | unknown/manual context | private context | yes | keep local only outside repo or delete after owner approval | `git clean -f -- MANUS_CONTEXT.md` | Do not commit. Contents were not exposed. Owner should inspect privately and either move outside the repo or approve deletion. |
| `backend/app/scripts/production_kb_source_coverage_qa.py` | untracked | new | Phase 9U / production KB source coverage | possible secret | yes | archive outside repo or commit later only after manual review | `git clean -f -- backend/app/scripts/production_kb_source_coverage_qa.py` | Production-facing QA script. Do not commit without explicit safety review for live endpoint, auth, DB, or private context handling. |
| `backend/app/scripts/production_phase_9aq_chat_operator_alignment_qa.py` | untracked | new | Phase 9AQ / production operator alignment QA | possible secret | yes | archive outside repo or commit later only after manual review | `git clean -f -- backend/app/scripts/production_phase_9aq_chat_operator_alignment_qa.py` | Production-facing QA script. Do not commit without explicit owner approval and safety review. |
| `backend/app/scripts/verify_phase_9aq_chat_operator_alignment.py` | untracked | new | Phase 9AQ verifier | low, tied to production script | yes | commit after review only if paired production script is approved, otherwise delete after approval | `git add backend/app/scripts/verify_phase_9aq_chat_operator_alignment.py` | Verifier depends on the production-facing 9AQ QA script. Keep paired with the owner decision for that script. |
| `backend/app/tests/test_phase_9aq_chat_operator_alignment.py` | untracked | new | Phase 9AQ tests | low, tied to production script | yes | commit after review only if paired verifier/script is approved, otherwise delete after approval | `git add backend/app/tests/test_phase_9aq_chat_operator_alignment.py` | Test imports the 9AQ verifier, which depends on a production-facing QA script. Do not commit separately. |
| `backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.json` | untracked | new | Phase 9U production KB evidence | private context / internal metadata | yes | archive outside repo or delete after owner approval | `git clean -f -- backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.json` | Large production evidence artifact. Manual review needed for internal source metadata and repo size before any commit. |
| `backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.md` | untracked | new | Phase 9U production KB evidence summary | private context / internal metadata | yes | archive outside repo, move to reviewed docs, or delete after owner approval | `git clean -f -- backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.md` | Misplaced under `backend/docs`; owner should decide whether it belongs in root docs, an archive, or local-only storage. |
| `docs/deployment/FULL_PROJECT_AUDIT_2026_05_30.md` | untracked | new | broad project audit | unknown | yes | commit after owner review or archive outside repo | `git add docs/deployment/FULL_PROJECT_AUDIT_2026_05_30.md` | Broad audit may contain stale or sensitive claims. Needs owner review before commit. |
| `docs/deployment/PHASE_9AY_FINAL_APPROVAL_READINESS_UPDATE.md` | untracked | new | Phase 9AY approval readiness note | low / unknown | yes | commit after owner review or delete after owner approval | `git add docs/deployment/PHASE_9AY_FINAL_APPROVAL_READINESS_UPDATE.md` | May be historically useful, but owner should confirm it is not stale relative to billing-blocked status. |
| `docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.csv` | untracked | new | production KB inventory | private context / internal metadata | yes | archive outside repo or delete after owner approval | `git clean -f -- docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.csv` | Production inventory may expose internal source metadata. Do not commit without data review. |
| `docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.md` | untracked | new | production KB inventory summary | private context / internal metadata | yes | archive outside repo or delete after owner approval | `git clean -f -- docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.md` | Production inventory may expose internal source metadata. Do not commit without data review. |
| `frontend/package-lock.json` | untracked | new | accidental/minimal frontend lockfile | low | yes for clean worktree; no for backend behavior if using clean SHA | delete after owner approval | `git clean -f -- frontend/package-lock.json` | No frontend/Netlify change is intended. Do not commit without an explicit frontend dependency phase. |
| `generate_manual.py` | untracked | new | local manual generator | private context | yes for clean worktree; no for backend behavior if using clean SHA | keep local only outside repo or delete after owner approval | `git clean -f -- generate_manual.py` | Local utility with possible private content. Do not commit now. Owner should move outside repo or approve deletion. |
| `generate_training.py` | untracked | new | local training generator | private context | yes for clean worktree; no for backend behavior if using clean SHA | keep local only outside repo or delete after owner approval | `git clean -f -- generate_training.py` | Local utility with possible private content. Do not commit now. Owner should move outside repo or approve deletion. |

## Required Specific Decisions

### A. Phase 9AY Program Catalog Test

File: `backend/app/tests/test_phase_9ay_program_catalog_source_routing.py`

Decision: safe to commit as test-only in the next phase if owner approves.

Recommended next action: commit now in Phase 9BW.

Exact command if approved:

```powershell
git add backend/app/tests/test_phase_9ay_program_catalog_source_routing.py
git commit -m "phase 9ay: add bachelor program list regression tests"
```

Validation required after commit:

```powershell
cd C:\tmp\alte-ai-crm\backend
.venv\Scripts\python.exe -m compileall app
.venv\Scripts\python.exe -m pytest app/tests/test_phase_9ay_program_catalog_source_routing.py --basetemp .pytest_tmp_9bw_9ay_focused
.venv\Scripts\python.exe -m pytest --basetemp .pytest_tmp_9bw_after_9ay_commit
```

### B. Phase 9X Contact Safety Verifier

File: `backend/app/scripts/verify_phase_9x_browser_smoke_contact_safety.py`

Decision: DO NOT COMMIT AS-IS.

Recommended next action: delete after owner approval, keep local only, or fix in a separate approved phase.

Exact delete command if approved:

```powershell
git clean -f -- backend/app/scripts/verify_phase_9x_browser_smoke_contact_safety.py
```

Reason: Phase 9BR direct verifier run failed on a stale/current contact-safety assertion. It remains a deploy-hygiene blocker until deleted, fixed and committed, or moved outside the repo.

### C. MANUS Context

File: `MANUS_CONTEXT.md`

Decision: do not commit.

Recommended next action: owner privately inspects and moves outside repo or approves deletion.

Exact delete command if approved:

```powershell
git clean -f -- MANUS_CONTEXT.md
```

No contents are exposed in this package.

### D. Production-Facing QA / Evidence / Inventory

Files:

- `backend/app/scripts/production_kb_source_coverage_qa.py`
- `backend/app/scripts/production_phase_9aq_chat_operator_alignment_qa.py`
- `backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.json`
- `backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.md`
- `docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.csv`
- `docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.md`

Decision: manual review required before any commit.

Recommended next action: archive outside repo or keep local only unless owner explicitly approves commit after reviewing for production/internal metadata.

### E. Frontend Lockfile

File: `frontend/package-lock.json`

Decision: do not commit without explicit frontend approval.

Recommended next action: delete after owner approval.

Exact command if approved:

```powershell
git clean -f -- frontend/package-lock.json
```

No frontend/Netlify change is intended.

### F. Local Generators

Files:

- `generate_manual.py`
- `generate_training.py`

Decision: do not commit now.

Recommended next action: keep local only outside repo, or commit later only after owner review confirms these are project utilities with no private/sensitive content.

Exact delete commands if approved:

```powershell
git clean -f -- generate_manual.py
git clean -f -- generate_training.py
```

## Recommended Phase 9BW Execution Plan

Phase 9BW should execute only owner-approved actions:

1. Commit safe 9AY test if approved.
2. Delete, move outside repo, or fix the stale unsafe 9X contact safety verifier if approved.
3. Move `MANUS_CONTEXT.md` outside repo or delete it after owner approval.
4. Resolve `frontend/package-lock.json` after owner approval.
5. Resolve production evidence/inventory files only after manual review.
6. Resolve local generators after owner review.
7. Re-run:
   - `python -m compileall app`
   - full backend pytest
   - 9BE verifier and local QA
   - focused 9BF/9BG tests
8. Re-check deploy hygiene:
   - `git status --short --branch`
   - `git diff --name-only`
   - `git ls-files --others --exclude-standard`
9. Only after deploy hygiene is clean, check billing and consider backend deploy retry.

## Counts

- Recommended commit now: 1
- Recommended delete after owner approval: 7
- Recommended commit after review: 4
- Recommended archive outside repo / manual production review: 6
- Sensitive/manual keep-local or archive count: 8
- Files that block clean deploy-retry hygiene until resolved: 16

## Safety Confirmations

- Deploy performed: NO
- GCP billing/cloud build/artifact push retried: NO
- Blocker files modified: NO
- Blocker files deleted/reverted: NO
- Blocker files committed: NO
- `MANUS_CONTEXT.md` contents exposed: NO
- Secrets/tokens/passwords/DATABASE_URL printed: NO
- Real `alte.edu.ge` modified: NO
- Real `join.alte.edu.ge` modified: NO
- Assets uploaded or embedded: NO
- Frontend/Netlify changed: NO
- DB/schema/migration/seed/import changed: NO
- Secret Manager/CORS/Bridge Hub changed: NO
- Contact flow submitted: NO
- Lead/customer/task created: NO
- Public launch marked GO: NO

## Final State

Deploy status: `NOT_DEPLOYED_DEPLOY_HYGIENE_BLOCKERS_REMAIN`

Production unchanged: YES

Public launch: `NO-GO`
