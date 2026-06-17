# Phase 9BG Public Widget Source Display Cleanup Result

PHASE_9BG_STATUS=LOCAL_READY_PENDING_REVIEW

Final local state: PHASE_9BF_LOCAL_FIXES_PLUS_9BG_SOURCE_UI_CLEANUP_READY_PENDING_REVIEW

Public launch: NO-GO

## Files Changed

- `backend/app/schemas/chat.py`
- `backend/app/services/chat_service.py`
- `backend/app/tests/test_phase_9bg_public_widget_source_display_cleanup.py`
- `test_site/variants/pro-v2-chat.jsx`
- `widget/variants/pro-v2-chat.jsx`
- `docs/deployment/PHASE_9BG_PUBLIC_WIDGET_SOURCE_DISPLAY_CLEANUP_RESULT.md`

## Public Source Display Behavior

- Public source chips are hidden/replaced.
- The widget now renders at most one concise source line:
  - `წყარო: [human-readable official document title]`
  - `Source: [human-readable official document title]`
- The source line appears only for `answered_from_approved_source` responses when a readable label can be derived.
- Low UX finding fixed: backend responses now expose `public_source_label` for eligible source-backed answers, and the widget prefers it.
- MEDIUM review finding fixed: raw `used_sources` fallback was removed from backend and frontend source-label derivation.
- `public_source_label` is now derived only from trusted `source_group` mapping or an exact public-label whitelist.
- Frontend fallback order is now:
  - backend `public_source_label`
  - safe `source_group` public-label mapping
  - exact public-label whitelist only
  - no source line
- Raw `used_sources`, `snippet_titles`, internal KB names, chunk/page IDs, and source keys are not used as public source-label fallback.
- Unsupported/no-source, clarification, handover, wait-for-operator, and generic fallback responses render no source label.
- The widget no longer infers/defaults public source links from department pages when backend source metadata is absent.

## Human-Readable Labels

The widget maps internal/source metadata to public labels, including:

- ბაკალავრიატის დებულება
- მაგისტრატურის დებულება
- სასწავლო პროცესის მარეგულირებელი წესი
- აკადემიური კალენდარი 2025-2026
- საგანმანათლებლო პროგრამების კატალოგი
- მიღების წესი
- საერთაშორისო მიღების წესი
- ბიბლიოთეკის წესი
- კარიერის სერვისები
- ფინანსური მხარდაჭერა
- სახელმწიფო/სოციალური გრანტები

## Source Chip Hiding Result

- Internal source IDs are not rendered in the public source line UI.
- Public UI no longer renders source arrays as multiple clickable pills.
- Public UI no longer displays chunk/page/source-key style chips.

## Visual QA Result

- Visual QA status: not run in browser during this local pass because no frontend/widget build target was available and the bundled public widget artifact was not regenerated.
- Static UI checks confirm the source chip renderer was removed from the active Pro v2 widget JSX and replaced with a single-line renderer with mobile ellipsis constraints.
- Expected result after rebuilding the widget artifact: no source chip overflow, no internal source identifiers, and at most one compact source line under eligible source-backed answers.
- Required manual/browser viewports for reviewer follow-up after build: desktop 1440x900, mobile 430x932, mobile 390x844, mobile 375x667.

## Tests Run

- `python -m compileall app` - PASS
- `python -m pytest app/tests/test_phase_9bg_public_widget_source_display_cleanup.py --basetemp .pytest_tmp_9bg_medium_fix` - PASS, 7/7
- `python -m pytest --basetemp .pytest_tmp_9bg_medium_fix_full` - PASS, 1108/1108
- Static/source-rendering check - PASS; `public_source_label`, `source_group` fallback, exact whitelist checks, and single-line source rendering are present; raw `used_sources` fallback and removed source-chip markers remain absent from public rendering.
- Frontend/widget build - not run; no root or frontend `package.json` build target was available. Browser visual QA remains required before deploy after rebuilding the widget artifact.

## Safety

- Real `alte.edu.ge` / `join.alte.edu.ge` modified: NO
- Upload/embed assets changed: NO
- Frontend/Netlify deployed: NO
- DB/schema/migration/seed/import changed: NO
- Secret Manager/CORS/Bridge Hub changed: NO
- Contact flow with real data run: NO
- Lead/customer/task created: NO
- Deploy status: NOT_DEPLOYED
- Commit status: NO
- Public launch: NO-GO
