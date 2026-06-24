# Phase 10N Website Sync Approval Publish Result

## Feature Summary

Phase 10N adds a safe approval and publish layer on top of the Phase 10M Website Sync preview MVP.

Workflow:

1. Admin adds an approved official website source.
2. Admin runs a preview-only single URL sync.
3. Preview run remains `status=draft` and `public_usable=false`.
4. Admin reviews the draft extraction.
5. Admin approves or rejects the draft run.
6. Approved chunks are copied into an approved website knowledge store.
7. Approved website content can be searched by `/api/knowledge/ask` and `/chat/message`.
8. Draft, rejected, and archived content remains unavailable to public retrieval.

Relevant commits:

- Phase 10M feature: `b69c7e6a15f4aeae079850011eb20c8e75b50463`
- Phase 10M result doc: `47deee491f740984b29a243e7fced00becb86e89`
- Phase 10N approval/publish feature: `5c3c88038f09c11a71b80f27377108e9d4c804b8`
- Georgian encoding guard: `09b66afa88a238b4d5d14ab335884d2d74824558`
- 10N Georgian website retrieval verification: `467a69daae030d5013f9ee8c8958139a385fea1a`

## Approval/Publish Model

Approval is explicit and admin-triggered. Draft preview runs are not automatically published.

Approved content is copied from reviewed preview chunks into a separate approved website store. The source preview run remains separate from the public-usable approved records.

Rejecting a run marks it rejected and keeps all content non-public. Rolling back an approved version archives approved chunks and makes them non-public.

## Approved Website Store Model

No DB migration was added. The Phase 10N MVP uses the Phase 10M local/in-memory service pattern:

- preview sources: in-memory
- preview runs: in-memory
- approved website chunks: in-memory

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

## APIs Implemented

New or updated internal Website Sync APIs:

- `POST /api/knowledge/sync/website/approve/{run_id}`
- `POST /api/knowledge/sync/website/reject/{run_id}`
- `GET /api/knowledge/sync/website/approved`
- `POST /api/knowledge/sync/website/rollback/{version_id}`
- `GET /api/knowledge/sync/website/diff/{run_id}`

Existing Phase 10M APIs remain:

- `POST /api/knowledge/sync/website/sources`
- `GET /api/knowledge/sync/website/sources`
- `POST /api/knowledge/sync/website/preview`
- `GET /api/knowledge/sync/website/runs`

## Settings UI Changes

CRM Settings -> Knowledge -> Website Sync now supports:

- preview run review
- approve action
- reject action
- approved content list
- archive/rollback action
- display of status, freshness class, source group, priority, chunk count, and public usability

The UI safety notice states that draft content is never used by the public chatbot and that only approved website content can be used.

This was a local/admin UI change only. No Netlify production deployment was performed.

## Website-First Retrieval Behavior

Approved website content is available to:

- `/api/knowledge/ask`
- `/chat/message`

Behavior:

- variable/freshness-sensitive questions can use approved website content first
- approved website chunks carry `priority=100`
- draft/rejected/archived chunks are not searchable
- `/api/knowledge/ask` remains deterministic and returns `used_claude=false`
- public chat skips Cloud AI fallback and finance exact-amount guard when an answer comes from approved website content
- public source label is clean and readable: `ალტეს ოფიციალური ვებგვერდი`
- stable questions continue to use existing structured KB/files unless approved website content is a stronger direct match

## Georgian UTF-8 Verification

Georgian Website Sync retrieval was verified after the approval/publish implementation.

Confirmed:

- `/api/knowledge/sync/website/approved` returns readable Georgian chunk text.
- approved chunks use readable `clean_source_label`: `ალტეს ოფიციალური ვებგვერდი`.
- `/api/knowledge/ask` returns readable Georgian from the approved website path for `მიღების ვადები როდის არის?`.
- `/chat/message` returns readable Georgian from the approved website path for the same question.
- the final `public_source_label` remains readable Georgian.
- no `áƒ` mojibake marker appears in approved chunk text, `/api/knowledge/ask` answer, `/chat/message` reply, or source labels.
- no replacement character `�` appears in those responses.
- no raw internal source IDs are exposed.

PowerShell output can still need UTF-8 console configuration for manual display:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
```

## Draft/Public Isolation

Confirmed:

- draft preview runs are `public_usable=false`
- rejected runs are not searchable
- archived approved chunks are `public_usable=false`
- `/api/knowledge/ask` cannot answer from draft content
- `/chat/message` cannot answer from draft content
- only approved chunks with `status=approved` and `public_usable=true` can be returned

## Approved Website Priority Behavior

Validated with local fixture content:

- approved website tuition content answered a variable tuition question
- approved website admissions/deadline content answered a Georgian variable admissions question
- approved website answer appeared only after explicit approval
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
- approved website retrieval for Georgian admissions/deadline question
- approved store Georgian readability
- `/api/knowledge/ask` Georgian website-first retrieval readability
- `/chat/message` Georgian website-first retrieval readability
- readable Georgian source label assertion
- mojibake and replacement-character rejection
- raw internal source ID rejection
- stable structured KB regression
- domain and private-path guards
- no lead/customer/task creation

## Validation Results

Run from `C:\tmp\alte-ai-crm\backend` with `.\.venv\Scripts\python.exe`.

- `python -m compileall app`: PASS
- `pytest app/tests/test_phase_10m_website_sync_preview_mvp.py --basetemp .pytest_tmp_10n_encoding_10m`: 7 passed
- `pytest app/tests/test_phase_10n_website_sync_approval_publish.py --basetemp .pytest_tmp_10n_encoding`: 9 passed
- `pytest --basetemp .pytest_tmp_10n_encoding_full`: 1169 passed
- `python -m app.scripts.verify_phase_9be_academic_calendar_fixes`: PASS
- `python -m app.scripts.local_phase_9be_academic_calendar_fixes_qa`: 30/30 PASS
- `pytest app/tests/test_phase_9bf_georgian_control_fixes.py app/tests/test_phase_9bg_public_widget_source_display_cleanup.py --basetemp .pytest_tmp_10n_encoding_9bf_9bg`: 12 passed
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

No Phase 10N image tag or digest was created.

## Real Crawl / Production KB Status

- Real crawl occurred: NO
- Production KB changed: NO
- Approved website content exists in production: NO
- Approved website content exists only in local/test runtime: YES, fixture-only during tests
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

