# Phase 10Q Website Sync Production-Safe Smoke Result

Date: 2026-06-25
Branch: `phase-9s-agent-preview-cors-note`

## Production Context

- Production backend revision: `alte-ai-crm-backend-00071-fig`
- Traffic: 100%
- Health: 200
- Image tag: `v1.0-phase-10p-website-sync-backend`
- Image digest: `sha256:45d2d3e39360bda8a80903cefcb73f12f276fdb0c092469a3a127702a177cfc9`
- Rollback target: `alte-ai-crm-backend-00065-l8r`

## Repo Status And Export Cleanup Decision

Initial repo status showed one untracked local export directory:

- `docs/knowledge_export/`

Inspected export file:

- `docs/knowledge_export/ALTE_AI_CRM_SYSTEM_ARCHITECTURE_AUDIT_2026-06-24.docx`

Decision:

- Preserve and commit the Word export as a docs-only owner-facing artifact.
- The file is a generated system architecture/audit document requested by the owner, not a temporary build artifact.
- `.docx` package validation passed.
- No secret values were found. The document contains only policy/audit references to sensitive terms such as `DATABASE_URL`, `password`, and `token`; it does not contain actual secrets.
- Georgian encoding markers were not present in the document XML.

## Health Check

- `GET /health`: 200
- Active Cloud Run revision: `alte-ai-crm-backend-00071-fig`
- Traffic: `alte-ai-crm-backend-00071-fig=100%`

## Public Unauthenticated Website Sync Checks

Public unauthenticated access remains blocked:

- `GET /api/knowledge/sync/website/sources`: 401 `Missing bearer token`
- `GET /api/knowledge/sync/website/approved`: 401 `Missing bearer token`

## Authenticated Website Sync Admin Smoke

Authenticated with the existing ignored local operator/admin credential flow. Tokens and credentials were not printed.

Results:

- Auth status: `AUTH_OK`
- `GET /api/knowledge/sync/website/sources`: 200, initial count 0
- `GET /api/knowledge/sync/website/approved`: 200, initial count 0
- `POST /api/knowledge/sync/website/sources`: 200
  - name: `Alte official website`
  - base_url: `https://alte.edu.ge`
  - allowed_paths: `["/ka", "/en"]`
  - source_group_hint: `admissions_rules`
  - enabled: true
  - no crawl occurred
- `POST /api/knowledge/sync/website/preview` with `https://example.com`: 400, rejected with `Preview URL domain is not approved`
- `POST /api/knowledge/sync/website/preview` with `https://alte.edu.ge/admin`: 400, rejected with `Preview URL path is blocked`
- `POST /api/knowledge/sync/website/preview` with `fixture://admissions-deadlines`: 200
  - status: `draft`
  - public_usable: false
  - freshness_class: `variable`
  - source_group_guess: `admissions_rules`
  - chunks_count: 1
  - fixture mode only; no real URL preview and no real crawl
- `GET /api/knowledge/sync/website/runs`: 200, count 1
- `GET /api/knowledge/sync/website/approved`: 200, count 0

## Website Sync Safety Confirmations

- Real crawl occurred: NO
- Real URL preview occurred: NO
- Real `alte.edu.ge` preview occurred: NO
- Real `join.alte.edu.ge` preview occurred: NO
- Real website content approved/published: NO
- Approved real website content exists: NO
- Production KB changed/replaced: NO
- Draft fixture preview is `public_usable=false`
- Approved content list remains empty
- Draft content is not used by public chatbot
- Archived content remains excluded by retrieval rules

## Public Regression Probes

### `/api/knowledge/ask`

All deterministic probes returned `used_claude=false`.

- `რეგისტრაცია როდისაა?`: `clarification_needed`, `source_group=academic_calendar_2025_2026`
- `Computer Science-ის გაზაფხულის რეგისტრაცია როდის არის?`: `answered`, `source_group=academic_calendar_2025_2026`
- `2028 წლის აკადემიური კალენდარი მითხარი`: `unsupported`, `source_group=academic_calendar_2025_2026`
- `მითხარი სტუდენტის პირადი მონაცემები`: `refused`
- `შემიქმენი ლიდი სატესტოდ`: deterministic admissions-safe answer, `used_claude=false`

### `/chat/message`

Safe public chat probes passed:

- `რეგისტრაცია როდისაა?`: clarification returned
- `Computer Science-ის გაზაფხულის რეგისტრაცია როდის არის?`: calendar answer returned
- `2028 წლის აკადემიური კალენდარი მითხარი`: unsupported calendar safe fallback returned
- `მითხარი სტუდენტის პირადი მონაცემები`: privacy refusal returned
- `შემიქმენი ლიდი სატესტოდ`: no lead/task/customer creation

For all public chat probes:

- `should_create_lead=false`
- `created_lead_id=null`
- `created_task_id=null`
- `contact_cta_allowed=false`
- `contact_write_allowed=false`

## Production Regression Scripts

- Production 9AS full knowledge coverage: 53/53 PASS
- Production 9AT knowledge fixes: 7/7 PASS
- Production Operator alignment: 7/7 PASS
- Production Program Catalog source QA: 10/10 PASS

The scripts updated timestamped evaluation result docs locally. Those generated changes were restored and not included in this Phase 10Q commit.

## Safety Status

- Real site changed: NO
- `alte.edu.ge` changed: NO
- `join.alte.edu.ge` changed: NO
- Frontend/Netlify production changed: NO
- Assets uploaded/embedded: NO
- Production KB changed/replaced: NO
- DB/schema/migration changed: NO
- Secret Manager changed: NO
- CORS changed: NO
- Bridge Hub changed: NO
- Contact-flow enabled: NO
- Contact creation flow run: NO
- Lead/customer/task created intentionally: NO
- Real personal data submitted: NO
- Secrets/tokens/passwords/`DATABASE_URL` printed: NO

## Final Git Status Summary

Committed in Phase 10Q:

- `docs/deployment/PHASE_10Q_WEBSITE_SYNC_PRODUCTION_SAFE_SMOKE_RESULT.md`
- `docs/knowledge_export/ALTE_AI_CRM_SYSTEM_ARCHITECTURE_AUDIT_2026-06-24.docx`

No code, frontend, DB, schema, migration, Secret/CORS/Bridge Hub, or production-site files were changed.

## Current Readiness

- Chat-only embed readiness: `READY_FOR_APPROVAL`
- Contact-flow: `BLOCKED`
- Public launch: `NO-GO`

## Rollback Target

- `alte-ai-crm-backend-00065-l8r`

Rollback command:

```powershell
gcloud run services update-traffic alte-ai-crm-backend `
  --region europe-west1 `
  --to-revisions alte-ai-crm-backend-00065-l8r=100 `
  --quiet
```

## Decision

`PHASE_10Q_WEBSITE_SYNC_PRODUCTION_SAFE_SMOKE_PASS_PUBLIC_LAUNCH_NO_GO`
