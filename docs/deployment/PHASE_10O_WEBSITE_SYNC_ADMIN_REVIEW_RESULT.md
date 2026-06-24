# Phase 10O Website Sync Admin Review Result

## Feature Summary

Phase 10O polishes the Website Sync admin review workflow before any backend deployment of the 10M-10O stack.

Implemented:

- richer review/diff response for preview runs
- high-risk review flags
- approved content archive filtering
- rollback/archive safety checks
- Settings UI review diff panel
- stronger tests for review, diff, high-risk flags, archive filtering, and retrieval safety

No deployment was performed.

## Diff/Review Improvements

`GET /api/knowledge/sync/website/diff/{run_id}` now returns review metadata beyond the raw preview run:

- `run_id`
- `source_url`
- `canonical_url`
- `page_title`
- `status`
- `freshness_class`
- `source_group_guess`
- `risk_flags`
- `public_usable`
- `chunks_preview`
- `old_approved_content`
- `detected_changes`
- `conflicts`
- `added_lines`
- `removed_lines`
- `unchanged_summary`
- `content_hash_changed`
- `approval_allowed`
- `rejection_allowed`
- `archive_available`

The MVP diff compares normalized text lines from the draft preview against active approved content for the same canonical URL and source group.

## High-Risk Flags

Preview runs now include clearer high-risk flags for review-sensitive content:

- dates
- deadlines
- tuition/fees/prices
- grants/scholarships
- admissions rules
- academic calendar
- program requirements
- ECTS/credits
- legal/privacy text
- contact details
- year-specific content
- fixture/test input

High-risk content remains locally approvable, but the API and Settings UI label it for review.

## Archive/Rollback Behavior

`POST /api/knowledge/sync/website/rollback/{version_id}` archives approved chunks for a version/run by setting:

- `status=archived`
- `public_usable=false`

`GET /api/knowledge/sync/website/approved` now excludes archived chunks by default.

`GET /api/knowledge/sync/website/approved?include_archived=true` returns archived chunks for admin inspection.

Archived content is not used by `/api/knowledge/ask` or `/chat/message`.

## Settings UI Changes

Settings -> Knowledge -> Website Sync now includes:

- source list with source metadata and last preview marker
- preview result with draft status, freshness class, source group, risk flags, public usability, extracted text, and chunks
- approve/reject actions where allowed
- review diff panel with added/removed summaries, hash-change status, high-risk warning, old approved count, and action state
- approved content list with source label, freshness class, priority, public usability, and archive action

Safety notices remain:

- draft content is never used publicly
- only approved website content can be used
- archived content is not used publicly
- variable information uses website-first priority after approval

Local/admin UI only. No Netlify production deployment was performed.

## Retrieval Safety

Confirmed by tests:

- draft content is never used by `/api/knowledge/ask`
- draft content is never used by `/chat/message`
- archived content is never used by `/api/knowledge/ask`
- approved content is used only when `status=approved` and `public_usable=true`
- archived chunks are excluded from the default approved listing
- raw internal IDs are not exposed in public labels
- Georgian website sync answers remain readable
- no lead/customer/task records are created by Website Sync tests

## Tests Added

Added:

- `backend/app/tests/test_phase_10o_website_sync_admin_review.py`

Updated:

- `backend/app/tests/test_phase_10n_website_sync_approval_publish.py`

Coverage includes:

- diff endpoint review shape
- draft approval/rejection flags
- old approved content comparison
- added/removed text summary
- content hash change detection
- high-risk flags for deadline/date/year content
- high-risk flags for tuition/price content
- stable program fixture risk boundaries
- archive default filtering
- `include_archived=true` inspection
- retrieval blocked after archive/rollback
- no contact-flow writes

## Validation Results

Run from `C:\tmp\alte-ai-crm\backend` with `.\.venv\Scripts\python.exe`.

- `python -m compileall app`: PASS
- `pytest app/tests/test_phase_10m_website_sync_preview_mvp.py --basetemp .pytest_tmp_10o_10m`: 7 passed
- `pytest app/tests/test_phase_10n_website_sync_approval_publish.py --basetemp .pytest_tmp_10o_10n`: 9 passed
- `pytest app/tests/test_phase_10o_website_sync_admin_review.py --basetemp .pytest_tmp_10o`: 4 passed
- `pytest --basetemp .pytest_tmp_10o_full`: 1173 passed
- `python -m app.scripts.verify_phase_9be_academic_calendar_fixes`: PASS
- `python -m app.scripts.local_phase_9be_academic_calendar_fixes_qa`: 30/30 PASS
- `pytest app/tests/test_phase_9bf_georgian_control_fixes.py app/tests/test_phase_9bg_public_widget_source_display_cleanup.py --basetemp .pytest_tmp_10o_9bf_9bg`: 12 passed
- `node --check frontend/app.js`: PASS

## Deploy Decision

Not deployed.

Reasons:

- Phase 10O is a local/admin polish phase.
- Phase 10M/10N/10O have not been approved for backend deployment yet.
- No real crawl occurred.
- No production KB replacement occurred.
- Public launch remains NO-GO.

Current production backend remains:

- Revision: `alte-ai-crm-backend-00065-l8r`
- Traffic: 100%
- Health: 200

## Safety Status

- Real crawl occurred: NO
- Production KB changed: NO
- Real site changed: NO
- Netlify production changed: NO
- DB/schema changed: NO
- Secret/CORS/Bridge Hub changed: NO
- Contact-flow status: BLOCKED
- Public launch: NO-GO
- Chat-only embed readiness: READY_FOR_APPROVAL

## Safety Confirmations

Confirmed:

- no real `alte.edu.ge` or `join.alte.edu.ge` changes
- no Netlify production changes
- no unintended DB/schema changes
- no Secret Manager changes
- no CORS changes
- no Bridge Hub changes
- no contact-flow enablement
- no contact creation flow run
- no lead/customer/task creation by Website Sync tests
- no secrets/tokens/passwords/DATABASE_URL printed

## Next Recommended Step

Recommended next step is either:

- backend-only staging/production deploy approval for the 10M-10O Website Sync stack, or
- Phase 10P production-safe website sync QA before deployment approval.

