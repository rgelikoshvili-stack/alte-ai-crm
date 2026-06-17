# Phase 10B Topic Switch and Source Display Result

## Decision

`BACKEND_DEPLOYED_AND_VERIFIED_CHAT_ONLY_EMBED_READY_FOR_APPROVAL_PUBLIC_LAUNCH_NO_GO`

Public launch remains **NO-GO**. Contact-flow remains blocked pending privacy/legal and real-write approval.

## Root Cause

Manual widget review found two issues:

1. Computer Science topic switching needed explicit regression coverage to ensure current prompt intent wins over prior conversation context.
2. Public widget responses still exposed multiple `used_sources` values. The backend already returned a clean `public_source_label`, but public-mode clients could still render raw or noisy source chips from `used_sources`.

During production QA after the first 10B deploy, a related Program Catalog retrieval gap was found:

* English `Tell me about the Computer Science program` selected `program_catalog_sources`, but production retrieval returned no approved source when the available catalog evidence was Georgian-scoped.

## Files Changed

* `backend/app/services/chat_service.py`
* `backend/app/tests/test_phase_10b_topic_switch_source_display.py`
* `backend/app/tests/test_phase_9at_knowledge_coverage_fixes.py`
* `backend/app/tests/test_phase_9av_claude_intent_router.py`

## Implementation Summary

* Added public response `used_sources` sanitization for public widget mode.
* Public-mode responses now return at most one clean public label in `used_sources`.
* If a source group is not safely mappable, public-mode `used_sources` returns an empty list rather than raw internal IDs.
* Internal persisted message metadata still keeps raw source provenance for operator/audit use.
* Added exact source-group retrieval fallback from language-scoped search to cross-language search when a selected source group has no same-language match.
* The fallback remains constrained by source-group identity filtering, so it does not broaden into unrelated KB.

## Tests Added/Updated

* Added Phase 10B endpoint regression tests for:
  * registration clarification -> Bachelor spring registration -> Computer Science program
  * program clarification -> Computer Science spring registration
  * Computer Science program -> registration -> program context switching
  * KA/EN Computer Science program vs registration intent split
  * English Computer Science program using KA-only Program Catalog evidence
  * public payload source-display cleanup
* Updated older 9AT/9AV tests to assert the new public response contract:
  * public payloads expose a clean label or no label
  * raw source IDs remain hidden from public responses

## Local Validation

* `python -m compileall app`: PASS
* Focused Phase 10B tests: PASS, 5/5
* Full backend pytest: PASS, 1129/1129
* Phase 9BE verifier: PASS
* Phase 9BE local QA: PASS, 30/30
* 9BE over-capture regression: PASS, 23/23
* 9BE fallback over-capture regression: PASS, 7/7
* 9BE stale-date regression: PASS, 4/4
* 9BF/9BG focused tests: PASS, 12/12
* Local Phase 10A/9CF-style behavior review: PASS, 14/14

## Deploy Result

Backend-only deploy completed.

* Image tag: `v1.0-phase-10b-topic-switch-source-display`
* Image digest: `sha256:b8ec4d794e3832d687fc21308812428ae6ff8405da60477e25cbe6d78c3d70f4`
* Cloud Run revision: `alte-ai-crm-backend-00060-zm6`
* Traffic: 100%
* Previous rollback target: `alte-ai-crm-backend-00058-wss`
* Rollback command:

```powershell
gcloud run services update-traffic alte-ai-crm-backend --region europe-west1 --to-revisions alte-ai-crm-backend-00058-wss=100
```

## Production QA

* Health check: PASS, 200
* Manual Phase 10B production sequence probe: PASS, 10/10
* Source display/public payload check: PASS
  * no `full_alte_local_kb`
  * no `selected_alte_45_doc`
  * no `official_alte_8_pdf_kb`
  * no raw chunk/source identifiers
  * at most one clean public source label
* Direct Computer Science program KA: PASS, `program_catalog_sources`
* Direct Computer Science program EN: PASS, `program_catalog_sources`
* Direct Computer Science spring registration KA: PASS, `academic_calendar_2025_2026`
* Direct Computer Science spring registration EN: PASS, `academic_calendar_2025_2026`
* 9AS production QA: PASS, 53/53
* 9AT production QA: PASS, 7/7
* Operator alignment production QA: PASS, 7/7
* Program Catalog source production QA: PASS, 10/10
* 9BE local/verifier after deploy: PASS
* 9BF/9BG focused after deploy: PASS, 12/12

## Manual Sequence Results

Sequence 1:

* `რეგისტრაცია როდისაა?`: PASS, clarification
* `ბაკალავრიატის გაზაფხულის რეგისტრაცია როდის არის?`: PASS, Bachelor spring registration calendar answer
* `მითხარი Computer Science პროგრამაზე`: PASS, Program Catalog answer

Sequence 2:

* `პროგრამებზე მითხარი`: PASS, program clarification
* `Computer Science-ის გაზაფხულის რეგისტრაცია როდის არის?`: PASS, Computer Science spring registration calendar answer

Sequence 3:

* `მითხარი Computer Science პროგრამაზე`: PASS, Program Catalog
* `Computer Science-ის გაზაფხულის რეგისტრაცია როდის არის?`: PASS, Academic Calendar
* `მითხარი Computer Science პროგრამაზე`: PASS, Program Catalog again

## Static Widget Refresh

Static widget refresh needed: **NO** for this backend hotfix.

The backend now sanitizes public `used_sources`, so existing public widget clients that render that field receive no raw internal IDs. No Netlify deploy or real-site asset change was performed.

## Safety Confirmation

* Real `alte.edu.ge` / `join.alte.edu.ge` modified: NO
* Netlify production changed: NO
* Frontend assets uploaded or embedded: NO
* DB/schema/migration/seed/import changed: NO
* Secret Manager changed: NO
* CORS changed: NO
* Bridge Hub changed: NO
* Contact flow run: NO
* Lead/customer/task created: NO
* Secrets/tokens/passwords/DATABASE_URL printed: NO
* Public launch: NO-GO

