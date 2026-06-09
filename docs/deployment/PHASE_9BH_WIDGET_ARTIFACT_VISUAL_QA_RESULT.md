# Phase 9BH Widget Artifact Visual QA Result

PHASE_9BH_STATUS=LOCAL_VISUAL_QA_PASS_PENDING_REVIEW

Public launch: NO-GO

## Build / Rebuild

- Root/widget/test_site package build target found: NO
- Local widget artifact pattern found: YES
  - `test_site/alte-ai-chat-widget.html`
  - `test_site/alte-ai-chat-widget.js`
  - `test_site/variants/pro-v2-*.jsx`
- The active test widget loads variant JSX files directly through the static HTML shell, so no package rebuild command was available or run.
- Local static preview used: `python -m http.server 8765 --directory C:\tmp\alte-ai-crm\test_site`
- Artifact files changed: NO

## Visual QA Method

- Browser tooling: Playwright from backend virtual environment.
- URL: `http://127.0.0.1:8765/index.html`
- Backend/API calls were mocked in Playwright route handlers:
  - `/chat/session/start`
  - `/chat/message`
  - `/chat/handover/*`
  - `/chat/contact/*`
- No production/backend contact flow was executed.
- No contact form was submitted.
- No lead/customer/task was created.

## Viewport Results

| Viewport | Case | Result | Notes |
| --- | --- | --- | --- |
| 1440x900 | source-backed bachelor credits | PASS | One source line, no chips, no internal IDs, header/composer visible, no overflow. |
| 430x932 | source-backed calendar | PASS | One source line, no chips, no internal IDs, mobile sidebar hidden, no overflow. |
| 390x844 | clarification | PASS | No source line, no chips, header/composer visible, no overflow. |
| 375x667 | unsupported future year | PASS | No source line, mocked raw/internal source strings did not render, no overflow. |
| 430x932 | handover visual only | PASS | Handover card displayed without contact submit, no source line, mobile sidebar hidden. |

## Prompts Tested

Source-backed:

- `ბაკალავრიატის პროგრამების კრედიტები რამდენია?`
- `Computer Science-ის გაზაფხულის სემესტრი როდის იწყება?`
- `GPA როგორ ითვლება?`

Clarification:

- `გამოცდები როდის არის?`
- `რეგისტრაცია როდის არის?`

Unsupported:

- `2031 წლის გაზაფხულის სემესტრი როდის იწყება?`
- `ახლანდელი სწავლის საფასური მითხარი`

Handover visual only:

- `ოპერატორთან დაკავშირება მინდა`

## Screenshots

- `docs/visual/phase_9bh/desktop_1440_source_backed.png`
- `docs/visual/phase_9bh/mobile_430_source_backed.png`
- `docs/visual/phase_9bh/mobile_390_clarification.png`
- `docs/visual/phase_9bh/mobile_375_unsupported.png`
- `docs/visual/phase_9bh/mobile_430_handover_no_submit.png`

## Source Display Result

- Multi-source chips: GONE
- Maximum public source line count for source-backed answers: 1
- Unsupported/clarification/handover/fallback source line count: 0
- Internal source ID leakage: NONE OBSERVED
- Checked blocked strings:
  - `full_alte_local_kb`
  - `selected_alte_45_doc`
  - `official_alte_8_pdf_kb`
  - `official_academic_rules_full`
  - `chunk`
  - `p022_c050`
  - `raw used_sources`
  - `Phase 9BF Georgian control deterministic source mapping`

## Mobile Layout Result

- Header visible: PASS
- Composer visible: PASS
- Mobile sidebar hidden: PASS
- Horizontal overflow: NONE OBSERVED
- Source line layout: PASS
- Georgian text in rendered widget: PASS in active JSX-rendered UI.

## Verification

- `python -m compileall app` - PASS
- `pytest --basetemp .pytest_tmp_9bh_visual_qa` - PASS, 1108/1108
- `pytest app/tests/test_phase_9bg_public_widget_source_display_cleanup.py --basetemp .pytest_tmp_9bh_source_display_static` - PASS, 7/7

## Remaining Blockers

- Backend deploy remains blocked pending explicit approval.
- Frontend/Netlify deploy remains blocked pending explicit approval.
- Real widget artifact upload/embed remains blocked pending explicit approval.
- Browser visual QA against the rebuilt/deployed artifact remains required before any public deploy approval.

## Safety

- Deploy status: NOT_DEPLOYED
- Real `alte.edu.ge` / `join.alte.edu.ge` modified: NO
- Upload/embed assets changed: NO
- DB/schema/migration/seed/import changed: NO
- Secret Manager/CORS/Bridge Hub changed: NO
- Contact flow with real data run: NO
- Lead/customer/task created: NO
- Public launch: NO-GO
- Commit status: NO
