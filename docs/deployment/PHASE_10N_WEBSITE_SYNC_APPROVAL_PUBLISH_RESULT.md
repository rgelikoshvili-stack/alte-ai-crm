# Phase 10N Website Sync Approval Publish Result

## Feature Summary

Phase 10N adds a safe approval and publish layer on top of the Phase 10M Website Sync preview MVP.

The workflow is now:

1. Admin adds an approved website source.
2. Admin runs a preview-only single URL sync.
3. Preview run remains `status=draft` and `public_usable=false`.
4. Admin can approve or reject the draft run.
5. Approved chunks are copied into an approved website knowledge store with `priority=100`, `status=approved`, and `public_usable=true`.
6. Approved website content can be searched by `/api/knowledge/ask` and `/chat/message`.
7. Draft and rejected content remains unavailable to public retrieval.
8. Approved versions can be archived/rolled back by marking chunks `status=archived` and `public_usable=false`.

## Approval/Publish Model

Approval is explicit and admin-triggered. Draft preview runs are not automatically published.

Approved chunk fields include:

- `approved_chunk_id`
- `run_id`
- `source_id`
- `source_url`
- `canonical_url`
- `page_title`
- `language`
- `content_hash`
- `approved_at`
- `approved_by`
- `version`
- `source_group`
- `freshness_class`
- `priority=100`
- `status=approved`
- `chunk_text`
- `chunk_index`
- `risk_flags`
- `public_usable=true`
- `clean_source_label`

Draft records remain `public_usable=false` and are not searched by public gateways.

## Storage Model

No DB migration was added. The Phase 10N MVP uses the existing Phase 10M in-memory/local service pattern:

- preview sources: in-memory
- preview runs: in-memory
- approved website chunks: in-memory

This is appropriate for local/admin MVP validation and avoids unintended production KB replacement.

## APIs Implemented

New or updated internal Website Sync APIs:

- `POST /api/knowledge/sync/website/approve/{run_id}`
- `POST /api/knowledge/sync/website/reject/{run_id}`
- `GET /api/knowledge/sync/website/approved`
- `POST /api/knowledge/sync/website/rollback/{version_id}`
- `GET /api/knowledge/sync/website/diff/{run_id}` now reports approval readiness, risk flags, freshness class, source group guess, and public usability.

Existing Phase 10M APIs remain:

- `POST /api/knowledge/sync/website/sources`
- `GET /api/knowledge/sync/website/sources`
- `POST /api/knowledge/sync/website/preview`
- `GET /api/knowledge/sync/website/runs`

## Settings UI Changes

CRM Settings -> Knowledge -> Website Sync now supports:

- review of preview runs
- approve button
- reject button
- approved content list
- archive/rollback button
- status, freshness class, source group, priority, chunk count, and public usability display

The UI safety notice now states that draft content is never used by the public chatbot and that only approved website content can be used.

This was a local/admin UI change only. No Netlify production deployment was performed.

## Retrieval Integration

Approved website content is now available to:

- `/api/knowledge/ask`
- `/chat/message`

Behavior:

- variable/freshness-sensitive questions can use approved website content first
- approved website chunks carry `priority=100`
- draft/rejected/archived chunks are not searchable
- `/api/knowledge/ask` remains deterministic and returns `used_claude=false`
- public chat skips Cloud AI fallback and finance exact-amount guard when an answer comes from approved website content
- public source label is clean: `ალტეს ოფიციალური ვებგვერდი`

Stable questions continue to use the existing structured KB/files unless approved website content is a stronger direct match.

## Draft/Public Isolation

Confirmed:

- draft preview runs are `public_usable=false`
- rejected runs are not searchable
- archived approved chunks are `public_usable=false`
- public chatbot cannot answer from draft content
- `/api/knowledge/ask` cannot answer from draft content
- only approved chunks with `status=approved` and `public_usable=true` can be returned

## Approved Website Priority Behavior

Validated with local fixture content:

- approved website tuition content answered a variable tuition question
- approved website answer included the fixture amount only after explicit approval
- rejected and archived content did not affect public answers
- stable Medicine program info still used structured KB and returned program/ECTS information rather than the approved finance fixture

## Tests Added

Added:

- `backend/app/tests/test_phase_10n_website_sync_approval_publish.py`

Updated:

- `backend/app/tests/test_phase_10m_website_sync_preview_mvp.py`

Coverage includes:

- approve draft run
- reject draft run
- archive approved version
- draft isolation from `/api/knowledge/ask`
- draft isolation from `/chat/message`
- approved website retrieval for variable tuition question
- clean source label safety
- stable structured KB regression
- domain and private-path guards
- no lead/customer/task creation

## Validation Results

Run from `C:\tmp\alte-ai-crm\backend` with `.\.venv\Scripts\python.exe`.

- `python -m compileall app`: PASS
- `pytest app/tests/test_phase_10m_website_sync_preview_mvp.py app/tests/test_phase_10n_website_sync_approval_publish.py --basetemp .pytest_tmp_10n_focused`: 14 passed
- `pytest --basetemp .pytest_tmp_10n_website_sync_approval`: 1167 passed
- `python -m app.scripts.verify_phase_9be_academic_calendar_fixes`: PASS
- `python -m app.scripts.local_phase_9be_academic_calendar_fixes_qa`: 30/30 PASS
- `pytest app/tests/test_phase_9bf_georgian_control_fixes.py app/tests/test_phase_9bg_public_widget_source_display_cleanup.py --basetemp .pytest_tmp_10n_9bf_9bg`: 12 passed
- `node --check frontend/app.js`: PASS

## Deploy Decision

Deployment was skipped.

Reason:

- Phase 10N is a local/admin MVP approval layer with an in-memory approved store.
- No real crawl occurred.
- No production KB replacement occurred.
- No explicit deployment approval was requested after validation.
- Production remains unchanged.

Current production backend remains:

- Revision: `alte-ai-crm-backend-00065-l8r`
- Traffic: 100%
- Health: 200

No image tag or digest was created for Phase 10N.

## Real Crawl / Production KB Status

- Real crawl occurred: NO
- Production KB changed: NO
- Approved website content exists in production: NO
- Approved website content exists only in local test runtime: YES, fixture-only during tests
- Draft content can affect public chatbot: NO

## Readiness And Safety

- Chat-only embed readiness: READY_FOR_APPROVAL
- Contact-flow status: BLOCKED
- Public launch: NO-GO

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
- no real personal data submitted
- no secrets/tokens/passwords/DATABASE_URL printed

