# Pro v2 Current Program Gap Matrix

PRO_V2_GAP_MATRIX_STATUS=COMPLETED

| Function | Pro v2 behavior | Current safe program behavior | Gap status | Required implementation | Files | Safety notes |
| --- | --- | --- | --- | --- | --- | --- |
| Large modal | Expanded centered modal around 980x720 | Previous safe widget was smaller | EXISTS_BUT_VISUAL_MISMATCH | Rebuild to large Pro v2 modal | `widget/`, `test_site/`, `dist/widget/` | Frontend-only |
| Close/reopen | Close returns launcher | Missing/partial | MISSING_FRONTEND | Add close and launcher open | widget HTML/JS | Frontend-only |
| Expand/fullscreen | Expand/collapse control | Partial | PARTIAL | Add fullscreen toggle | widget HTML/JS | Frontend-only |
| Sidebar collapse | Icon-only sidebar | Missing | MISSING_FRONTEND | Add collapse toggle | widget HTML/JS | Frontend-only |
| KA/EN switch | Header control | Exists | EXISTS_AND_WORKS | Preserve and restyle | widget HTML/JS | Frontend-only |
| Reset/new chat | Clears conversation | Exists | EXISTS_AND_WORKS | Preserve and restyle | widget HTML/JS | Clears local IDs only |
| Settings panel | Source/notify/theme/clear toggles | Missing | MISSING_FRONTEND | Add safe UI-only panel | widget HTML/JS | No backend side effects |
| Attachment | Upload UI | Not supported | NEEDS_APPROVAL | Disabled button and backend gap doc | widget HTML/JS, docs | Do not upload files |
| Voice | Voice UI | Not supported | NEEDS_APPROVAL | Disabled button and backend gap doc | widget HTML/JS, docs | Do not record audio |
| Direct AI call | Browser model call | Not allowed | UNSAFE_IN_STANDALONE_REPLACE_WITH_BACKEND | Use `/chat/message` only | widget HTML/JS | No provider calls in browser |
| Hardcoded facts | Prompt contains facts | Backend KB/policy governs answers | UNSAFE_IN_STANDALONE_REPLACE_WITH_BACKEND | Do not copy facts | docs | Sensitive topics conservative |
| Department nav | Active department and topics | Exists | EXISTS_AND_WORKS | Expand department list and selected_topic | widget HTML/JS | Backend routing remains source |
| Quick chips | Sends seeded prompts | Exists | EXISTS_AND_WORKS | Preserve with Pro v2 styling | widget HTML/JS | No contact details |
| Source cards | Local source inference | Backend sources rendered | EXISTS_AND_WORKS | Render `used_sources` only | widget HTML/JS | No fake sources |
| Handover card | Local intent handover | Backend handover rendered | EXISTS_AND_WORKS | Render when backend flags | widget HTML/JS | No task from frontend |
| Contact request | Contact form prototype | Not allowed in smoke | NEEDS_APPROVAL | Show no-contact safety notice only | widget HTML/JS, docs | No phone/email submission |
| Keyboard shortcuts | Enter/Shift+Enter | Partial | PARTIAL | Add textarea key handling | widget HTML/JS | Frontend-only |
| Backend status | Online indicator | Exists | EXISTS_AND_WORKS | Preserve trust/status bar | widget HTML/JS | No secrets |
| Mobile responsive | Reflow/hide sidebar | Exists partially | PARTIAL | Improve viewport-aware CSS | widget HTML/JS | Frontend-only |

## Summary Counts

- EXISTS_AND_WORKS: 7
- EXISTS_BUT_VISUAL_MISMATCH: 1
- PARTIAL: 3
- MISSING_FRONTEND: 3
- MISSING_BACKEND / NEEDS_APPROVAL: 3
- UNSAFE_IN_STANDALONE_REPLACE_WITH_BACKEND: 2
