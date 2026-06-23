# Phase 10M Website Sync Settings Preview Result

Date: 2026-06-23

## Feature Summary

Phase 10M added a preview-only Website Sync MVP for the CRM operator/admin workspace. The feature lets an admin configure an approved official website source and run a single-URL draft preview extraction. It does not publish synced website content, replace production KB, or make draft website content available to public chatbot retrieval.

Feature commit:

- `b69c7e6a15f4aeae079850011eb20c8e75b50463`

## Settings UI Summary

Local/static CRM Settings now includes:

- `Settings -> Knowledge - Website Sync`
- Add Source fields:
  - source name
  - base URL
  - allowed paths
  - source group hint
  - enabled/disabled
- Sources list:
  - name
  - base URL
  - enabled status
  - allowed paths
  - source group hint
  - preview status
- Preview Sync:
  - select configured source
  - enter single URL or fixture URL
  - run preview
- Preview result:
  - page title
  - canonical URL
  - language
  - freshness class
  - source group guess
  - risk flags
  - extracted text preview
  - chunk previews
  - `public_usable=false`

Safety notice shown in Settings:

`Draft website sync content is not used by the public chatbot until approved in a later approval phase.`

No production Netlify deploy was performed.

## Internal API Summary

Added preview-only internal/admin API endpoints:

- `POST /api/knowledge/sync/website/sources`
- `GET /api/knowledge/sync/website/sources`
- `POST /api/knowledge/sync/website/preview`
- `GET /api/knowledge/sync/website/runs`
- `GET /api/knowledge/sync/website/diff/{run_id}`
- `POST /api/knowledge/sync/website/approve/{run_id}` returns `501` with `Approval/publish is planned for Phase 10N/10O.`

Storage model:

- in-memory preview store only
- no DB migration
- no production KB writes
- no public retrieval integration

URL safety:

- approved hosts only:
  - `alte.edu.ge`
  - `www.alte.edu.ge`
  - `join.alte.edu.ge`
- fixture URLs allowed for tests/local preview only
- external domains rejected
- localhost/private IPs rejected outside fixture mode
- blocked paths rejected:
  - `/admin`
  - `/login`
  - `/wp-admin`
  - `/dashboard`
  - `/api`
- preview requires `dry_run=true`
- single-URL mode only
- no cookies or auth headers
- safe user-agent
- timeout and size limit

## Freshness Classifier Summary

Implemented `classify_freshness(text) -> variable | stable | unknown`.

Variable markers include:

- Georgian deadline/calendar/tuition/grant markers from Phase 10L
- English deadline/calendar/tuition/grant/current markers from Phase 10L
- year-specific terms such as `2026`, `2027`, `2028`
- date patterns
- currency/price patterns
- schedule/period/contact/office-hours language

Stable markers include:

- general program descriptions
- program level/type
- ECTS/credits when not paired with variable markers
- academic integrity principles
- library/student service general rules
- ombudsman/policy-style descriptions

If text includes dates/prices/admissions/contact-style current information, it is classified as variable.

## Source Priority Model Status

Phase 10M does not implement public website-first retrieval. It prepares draft metadata needed for later phases:

- `source_group_guess`
- `freshness_class`
- `risk_flags`
- `public_usable=false`
- `status=draft`

The Phase 10L source priority model remains planned for Phase 10P retrieval implementation:

1. `approved_website_sync`, priority 100
2. `approved_structured_kb`, priority 80
3. `approved_uploaded_file`, priority 60
4. `archived_historical`, priority 20
5. `unapproved_draft`, not usable by public chatbot

## Draft/Public Isolation Confirmation

- Preview runs always return `status=draft`.
- Preview runs always return `public_usable=false`.
- Preview source/runs are not stored in `knowledge_sources` or `knowledge_snippets`.
- Public `/chat/message` retrieval does not read website sync preview state.
- Public `/api/knowledge/ask` remains deterministic and does not read website sync preview state.
- Approval/publish is disabled and returns `501`.
- Draft website content cannot affect public chatbot answers in Phase 10M.

## Tests Added

Added:

- `backend/app/tests/test_phase_10m_website_sync_preview_mvp.py`

Coverage:

- add/list website source
- reject unapproved domain
- reject admin/login/private paths
- preview fixture produces draft run
- extractor removes nav/footer/header/script/style
- freshness classifier variable cases
- freshness classifier stable cases
- draft preview returns `public_usable=false`
- `/api/knowledge/ask` still returns `used_claude=false`
- public chatbot does not use draft fixture content
- no lead/customer/task creation

## Validation Results

- `python -m compileall app`: PASS
- `pytest app/tests/test_phase_10m_website_sync_preview_mvp.py --basetemp .pytest_tmp_10m_focused`: 7 passed
- `pytest --basetemp .pytest_tmp_10m_website_sync_mvp`: 1160 passed
- `python -m app.scripts.verify_phase_9be_academic_calendar_fixes`: PASS
- `python -m app.scripts.local_phase_9be_academic_calendar_fixes_qa`: 30/30 PASS
- `pytest app/tests/test_phase_9bf_georgian_control_fixes.py app/tests/test_phase_9bg_public_widget_source_display_cleanup.py --basetemp .pytest_tmp_10m_9bf_9bg`: 12 passed
- `node --check frontend/app.js`: PASS

Frontend test framework:

- No `frontend/package.json` or frontend test runner exists.
- Static UI validation was limited to source inspection and JavaScript syntax check.

## Deploy Result

Deployment skipped.

Reason:

- Phase 10M is a preview-only/admin MVP.
- It includes local/static operator UI changes and no production Netlify deploy is approved.
- Draft content is intentionally not public usable.
- Production backend is unchanged.

Current production remains:

- Revision: `alte-ai-crm-backend-00065-l8r`
- Traffic: 100%
- Health: 200
- Image tag: `v1.0-phase-10h-topic-override-chat-only-cta`

## Crawl And KB Status

- Real crawl occurred: NO
- Real `alte.edu.ge` or `join.alte.edu.ge` scraped: NO
- Tests used local mocked fixtures only.
- Production KB changed: NO
- Production KB replaced: NO
- Draft website content can affect public chatbot: NO

## Safety Confirmation

- No real site changes.
- No upload/embed asset changes.
- No production Netlify changes.
- No production KB replacement.
- No DB/schema/migration changes.
- No Secret Manager/CORS/Bridge Hub changes.
- Contact-flow remains BLOCKED.
- No contact creation flow was run.
- No lead/customer/task creation was performed.
- No real personal data was submitted.
- No secrets/tokens/passwords/`DATABASE_URL` values were printed.
- Public launch remains NO-GO.
