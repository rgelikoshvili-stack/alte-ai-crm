# Phase 9BF + 9BG Commit Ready Pending Deploy

Status: COMMITTED_PENDING_DEPLOY

Public launch: NO-GO

## Commit

- Combined commit: `ece82c6` - `phase 9bf 9bg: fix georgian controls and public source display`
- Combined commit used because `backend/app/services/chat_service.py` contains shared Phase 9BF Georgian control logic and Phase 9BG public source-label metadata changes that should not be split mechanically.

## Tests Run

- `python -m compileall app` - PASS
- `pytest --basetemp .pytest_tmp_9bf_9bg_precommit` - PASS, 1108/1108
- `pytest app/tests/test_phase_9bf_georgian_control_fixes.py app/tests/test_phase_9bg_public_widget_source_display_cleanup.py --basetemp .pytest_tmp_9bf_9bg_focused` - PASS, 12/12
- `pytest app/tests/test_phase_9ai_knowledge_source_routing_clarification.py --basetemp .pytest_tmp_9bf_related` - PASS, 17/17

## Source Display Safety

- Public renderer does not read `backend.used_sources` for source display.
- Public renderer does not read `backend.snippet_titles` for source display.
- `response_public_source_label()` has no raw `used_sources` fallback.
- `public_source_label` is derived only from trusted source-group mapping or exact public-label whitelist.
- Internal source IDs, chunk/page IDs, and raw source-key values are not exposed through the public source line.

## Deploy Gate

- Deploy status: NOT_DEPLOYED
- Browser visual QA: REQUIRED BEFORE DEPLOY
- Remaining deploy blocker: rebuild widget artifact and run desktop/mobile visual QA.

## Safety Confirmation

- Real `alte.edu.ge` / `join.alte.edu.ge` modified: NO
- Upload/embed assets changed: NO
- Contact flow run: NO
- DB/schema/migration/seed/import changed: NO
- Secret Manager/CORS/Bridge Hub changed: NO
- Lead/customer/task created: NO
- Public launch: NO-GO
