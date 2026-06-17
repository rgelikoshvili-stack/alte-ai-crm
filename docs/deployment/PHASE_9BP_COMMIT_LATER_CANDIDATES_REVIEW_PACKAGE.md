# Phase 9BP Commit-Later Candidates Review Package

Date: 2026-06-14

Branch: `phase-9s-agent-preview-cors-note`

Production revision: `alte-ai-crm-backend-00052-mjq`

Traffic: 100% to `alte-ai-crm-backend-00052-mjq`

Decision state: `BACKEND_DEPLOY_BLOCKED_BILLING_PENDING_RETRY`

Deploy status: `NOT_DEPLOYED_BLOCKED_BY_GCP_BILLING`

Public launch: `NO-GO`

Source docs:

- `docs/deployment/PHASE_9BM_OWNER_REVIEW_FILE_INSPECTION_REPORT.md`
- `docs/deployment/PHASE_9BN_SAFE_CLEANUP_APPROVAL_PACKAGE.md`
- `docs/deployment/PHASE_9BO_LOW_RISK_DIRTY_CLEANUP_RESULT.md`

This package reviews only the remaining commit-later candidates. No candidate, sensitive/manual, frontend, generated utility, or local context file was modified, deleted, reverted, or committed.

## Current Commit-Later Candidate Set

Current candidate count: 10

| Path | Tracked/untracked | Type | Likely phase/purpose | Overlaps committed work | Why useful | Risk if committed | Risk if left uncommitted | Recommendation | Proposed commit group | Proposed commit message | Deploy retry blocker |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `backend/app/tests/test_phase_9ay_program_catalog_source_routing.py` | tracked, modified | test | Phase 9AY Program Catalog source routing and public answer cleanup regression coverage | Overlaps committed 9AY/9BA Program Catalog work by adding two Bachelor program-list assertions | Adds Georgian and English checks that Bachelor program-list replies include all 10 catalog programs and avoid source/page noise | Changes an existing tracked test file and full pytest surface; should be reviewed before commit | Keeps the worktree dirty and blocks clean deploy retry from this checkout | commit later after review | Phase 9AY regression test | `phase 9ay: add bachelor program list regression tests` | yes |
| `backend/app/scripts/verify_phase_9aq_chat_operator_alignment.py` | untracked | script | Phase 9AQ operator alignment result verifier | Overlaps committed 9AQ docs and depends on untracked production-facing 9AQ QA script | Preserves historical checks for 9AQ result docs, safety claims, and public launch NO-GO state | References `production_phase_9aq_chat_operator_alignment_qa.py`, which remains sensitive/manual hold; committing verifier first could create dangling or unsafe expectations | Keeps untracked script dirty; should not be committed until the production script decision is made | reclassify to sensitive/manual | Phase 9AQ manual-hold pair | hold; if approved later: `phase 9aq: preserve operator alignment verifier` | yes |
| `backend/app/scripts/verify_phase_9as_full_knowledge_operator_verification.py` | untracked | script | Phase 9AS full knowledge/operator verification result verifier | Overlaps committed 9AS evaluation/deploy docs and dataset | Verifies 9AS inventory, QA dataset size/categories, safety claims, and no public launch GO | Adds a historical verifier script; low production risk but expands repo maintenance surface | Leaves historical verification logic untracked and dirty | commit now | Phase 9AS historical verifier/test | `phase 9as: preserve full knowledge verification tests` | yes |
| `backend/app/scripts/verify_phase_9ba_program_catalog_file_qa.py` | untracked | script | Phase 9BA Program Catalog file QA verifier | Overlaps committed 9BA file QA result docs | Verifies 20-row Program Catalog file QA evidence and safety/no-secret claims | Low runtime risk; mostly documentation verification | Leaves useful historical QA verifier untracked | commit now | Phase 9BA/9BD file QA verifier/test | `phase 9ba 9bd: preserve file qa verifiers and tests` | yes |
| `backend/app/scripts/verify_phase_9bd_academic_calendar_file_qa.py` | untracked | script | Phase 9BD Academic Calendar file QA verifier | Overlaps committed 9BD QA set/result docs and later 9BE calendar fixes | Verifies calendar QA docs, expected dates, unsupported cases, and safety claims | Low runtime risk; contains historical mojibake strings copied from docs, so review should accept preserving historical evidence as-is | Leaves useful historical QA verifier untracked | commit now | Phase 9BA/9BD file QA verifier/test | `phase 9ba 9bd: preserve file qa verifiers and tests` | yes |
| `backend/app/scripts/verify_phase_9x_browser_smoke_contact_safety.py` | untracked | script | Phase 9X browser smoke/contact safety verifier | Overlaps committed Phase 9X result docs and active frontend/widget safety claims | Verifies contact-safety wording and frontend endpoint expectations against active files | Reads active frontend/dist/widget files and old status docs; needs code review because it may be stale relative to current 9BF-9BE queue | Keeps a potentially useful but stale verifier untracked | commit later after review | Phase 9X verifier | `phase 9x: preserve browser smoke contact safety verifier` | yes |
| `backend/app/tests/test_phase_9aq_chat_operator_alignment.py` | untracked | test | Phase 9AQ operator alignment tests | Overlaps committed 9AQ docs and depends on the untracked 9AQ verifier/production script | Adds regression tests for operator alignment result evidence | Imports a verifier that references a production-facing QA script still on manual hold; should not be committed separately | Keeps untracked test dirty; should wait for production script decision | reclassify to sensitive/manual | Phase 9AQ manual-hold pair | hold; if approved later: `phase 9aq: preserve operator alignment tests` | yes |
| `backend/app/tests/test_phase_9as_full_knowledge_operator_verification.py` | untracked | test | Phase 9AS full knowledge/operator verification tests | Overlaps committed 9AS dataset/docs | Adds dataset structure, category, source-group, and safety tests for 9AS evidence | Expands full pytest surface, but does not call production services | Leaves useful historical regression tests untracked | commit now | Phase 9AS historical verifier/test | `phase 9as: preserve full knowledge verification tests` | yes |
| `backend/app/tests/test_phase_9ba_program_catalog_file_qa.py` | untracked | test | Phase 9BA Program Catalog file QA tests | Overlaps committed 9BA docs | Adds importability and QA-result structure checks for Program Catalog evidence | Low; preserves historical QA expectations, including existing encoded text in docs | Leaves useful file-QA tests untracked | commit now | Phase 9BA/9BD file QA verifier/test | `phase 9ba 9bd: preserve file qa verifiers and tests` | yes |
| `backend/app/tests/test_phase_9bd_academic_calendar_file_qa.py` | untracked | test | Phase 9BD Academic Calendar file QA tests | Overlaps committed 9BD docs and current 9BE calendar work | Adds importability, expected-date, question-presence, and safety checks for 9BD evidence | Low; preserves historical QA expectations, including existing encoded text in docs | Leaves useful file-QA tests untracked | commit now | Phase 9BA/9BD file QA verifier/test | `phase 9ba 9bd: preserve file qa verifiers and tests` | yes |

## Grouped Recommendations

### A. Safe Doc/Test Commit Group

Recommended commit-now count: 6

These are documentation/evidence verifiers and matching tests that do not call production services and do not require sensitive/manual hold files:

- `backend/app/scripts/verify_phase_9as_full_knowledge_operator_verification.py`
- `backend/app/tests/test_phase_9as_full_knowledge_operator_verification.py`
- `backend/app/scripts/verify_phase_9ba_program_catalog_file_qa.py`
- `backend/app/tests/test_phase_9ba_program_catalog_file_qa.py`
- `backend/app/scripts/verify_phase_9bd_academic_calendar_file_qa.py`
- `backend/app/tests/test_phase_9bd_academic_calendar_file_qa.py`

Proposed commits:

- `phase 9as: preserve full knowledge verification tests`
- `phase 9ba 9bd: preserve file qa verifiers and tests`

Deploy retry can proceed without these only if they are either committed, deleted after approval, or kept outside the dirty worktree. From this checkout, they remain deploy hygiene blockers while untracked.

### B. Needs Code Review Before Commit

Needs review count: 2

- `backend/app/tests/test_phase_9ay_program_catalog_source_routing.py`
  - Reason: modifies a tracked test file by adding Bachelor program-list assertions. Likely useful, but should be reviewed as a scoped 9AY regression commit.
  - Proposed commit message after approval: `phase 9ay: add bachelor program list regression tests`

- `backend/app/scripts/verify_phase_9x_browser_smoke_contact_safety.py`
  - Reason: reads active frontend/dist/widget files and historical status docs. It may be useful, but should be checked for stale assumptions before commit.
  - Proposed commit message after approval: `phase 9x: preserve browser smoke contact safety verifier`

### C. Production-Facing Script, Hold For Manual Inspection

Reclassified sensitive/manual count: 2

These files are not production-facing themselves, but they depend on a production-facing script still held for manual review. They should move with the Phase 9AQ production QA script decision:

- `backend/app/scripts/verify_phase_9aq_chat_operator_alignment.py`
- `backend/app/tests/test_phase_9aq_chat_operator_alignment.py`

Do not commit these until `backend/app/scripts/production_phase_9aq_chat_operator_alignment_qa.py` is approved, deleted, or rewritten into a safe local-only verifier dependency.

### D. Keep Local Only

Count: 0

No commit-later candidate is recommended as keep-local-only at this stage. The keep-local-only files from prior reports remain outside this package:

- `generate_manual.py`
- `generate_training.py`

### E. Delete/Revert After Approval

Delete/revert recommendation count: 0

No commit-later candidate is currently recommended for delete or revert as the primary action. If the owner rejects the proposed commits, the fallback is:

- revert `backend/app/tests/test_phase_9ay_program_catalog_source_routing.py` after approval
- delete the selected untracked verifier/test files after approval

## Explicit Non-Actions

The following files are not included in this commit-later package and were not read for content here:

- `MANUS_CONTEXT.md`
- `frontend/package-lock.json`
- `generate_manual.py`
- `generate_training.py`

The following production-facing or production-evidence files remain manual/sensitive hold files and are not included as commit-later candidates:

- `backend/app/scripts/production_kb_source_coverage_qa.py`
- `backend/app/scripts/production_phase_9aq_chat_operator_alignment_qa.py`
- `backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.json`
- `backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.md`
- `docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.csv`
- `docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.md`

## Remaining Deploy-Retry Blockers From Dirty Tree

The backend code queue is committed through Phase 9BE, but this checkout is still not clean enough for a controlled billing-restored deploy retry.

Files that still block deploy retry hygiene from this checkout:

- `backend/app/tests/test_phase_9ay_program_catalog_source_routing.py`
- `MANUS_CONTEXT.md`
- `backend/app/scripts/production_kb_source_coverage_qa.py`
- `backend/app/scripts/production_phase_9aq_chat_operator_alignment_qa.py`
- `backend/app/scripts/verify_phase_9aq_chat_operator_alignment.py`
- `backend/app/scripts/verify_phase_9as_full_knowledge_operator_verification.py`
- `backend/app/scripts/verify_phase_9ba_program_catalog_file_qa.py`
- `backend/app/scripts/verify_phase_9bd_academic_calendar_file_qa.py`
- `backend/app/scripts/verify_phase_9x_browser_smoke_contact_safety.py`
- `backend/app/tests/test_phase_9aq_chat_operator_alignment.py`
- `backend/app/tests/test_phase_9as_full_knowledge_operator_verification.py`
- `backend/app/tests/test_phase_9ba_program_catalog_file_qa.py`
- `backend/app/tests/test_phase_9bd_academic_calendar_file_qa.py`
- `backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.json`
- `backend/docs/deployment/PHASE_9U_PRODUCTION_KB_SOURCE_COVERAGE_QA_RESULT.md`
- `docs/deployment/FULL_PROJECT_AUDIT_2026_05_30.md`
- `docs/deployment/PHASE_9AY_FINAL_APPROVAL_READINESS_UPDATE.md`
- `docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.csv`
- `docs/deployment/PRODUCTION_KB_FULL_SOURCE_INVENTORY_AUDIT.md`

Files that remain dirty but do not affect backend deploy behavior if deploy is run from committed code and the owner accepts a not-fully-clean worktree:

- `frontend/package-lock.json`
- `generate_manual.py`
- `generate_training.py`

Preferred retry posture remains a clean checkout or explicitly verified commit SHA after owner decisions are applied.

## Safety Confirmations

- Deploy performed: NO
- GCP billing/cloud build/artifact push retried: NO
- Candidate files modified: NO
- Candidate files deleted/reverted: NO
- Candidate files committed: NO
- Sensitive/manual hold files touched: NO
- `MANUS_CONTEXT.md` touched: NO
- `frontend/package-lock.json` touched: NO
- `generate_manual.py` / `generate_training.py` touched: NO
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

## Final State

Deploy status: `NOT_DEPLOYED_BLOCKED_BY_GCP_BILLING`

Production unchanged: YES

Public launch: `NO-GO`
