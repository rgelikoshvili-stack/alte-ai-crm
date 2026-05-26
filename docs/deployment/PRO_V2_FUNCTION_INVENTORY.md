# Pro v2 Function Inventory

PRO_V2_FUNCTION_INVENTORY_STATUS=COMPLETED

## Phase 9S ZIP Source Inventory Update

The inventory is now based on `docs/knowledge_evidence/uploaded_pro_v2_zip_source/deploy/variants/pro-v2-chat.jsx` and supporting source files, not only screenshots or the bundled standalone HTML.

Source components/functions reviewed:

- `proV2Css` in `pro-v2-chat.jsx`: `.cw-win`, `.cw-win.expanded`, `.cw-backdrop`, `.cw-side`, `.cw-side.collapsed`, `.cw-hdr`, `.cw-trust`, `.cw-msgs`, `.cw-greet`, `.cw-chips`, `.cw-handover`, `.cw-comp`, `.cw-attach-menu`, `.cw-toast`.
- `Header`: language switch, new chat, settings, expand/collapse, close controls.
- `Sidebar`: department list, active state, collapsed state, human/operator entry.
- `Greeting`: welcome card, trending feature card, quick replies/chips.
- `Message`: user/assistant bubbles, source chips, bubble actions.
- `HandoverCard`: operator card and contact action UI.
- `Composer`: plus/attachment, textarea, mic, send, Enter/Shift+Enter behavior.
- `SettingsModal`: language cards, source toggle, notification toggle, dark toggle, clear conversation.
- `LeadModal`: contact capture prototype; documented as approval/backend-needed and not enabled for frontend CRM submission.

Port result:

- Visual/window/sidebar/composer/settings/source/operator behavior is ported into `widget/alte-ai-chatbot-pro-v2-safe.html`.
- Unsafe AI completion behavior from `window.claude.complete` is replaced by `/chat/session/start` and `/chat/message`.
- File upload, voice transcription, live operator workflow, and real contact/CRM submission remain documented approval/backend gaps.

## Layout And Window

- Launcher opens chat.
- Close hides chat and returns launcher.
- Expanded modal centers at desktop width around 980px.
- Backdrop appears in expanded mode in the standalone.
- Sidebar appears in expanded mode.
- Sidebar collapse reduces it to icon-only mode.
- Message area scrolls independently.
- Mobile reflows/hides sidebar.

## Header Controls

- KA/EN language toggle.
- Reset/new chat.
- Settings button.
- Expand/collapse button.
- Close button.
- Backend/status indicator.
- Title/subtitle.

## Sidebar And Navigation

- Department list: Admissions, Programs, Tuition/Aid, International, Medicine/MD, Library, Career, IT Help.
- Live operator entry.
- Active department state.
- Department icons/badges.
- Bottom user/profile area.
- Selected department context is used by chat behavior.

## Greeting And Quick Actions

- Greeting title and body.
- Trending/recommended card.
- Quick replies/popular questions.
- Department/topic-specific context.

## Chat Behavior

- User and assistant bubbles.
- Typing indicator.
- Source cards.
- Handover/operator card.
- Contact request card.
- Assistant message action buttons in the standalone.
- Retry/regenerate pattern in standalone.
- No-answer/fallback behavior.
- Link rendering and markdown-like formatting.

## Composer/Input

- Textarea input.
- Enter sends.
- Shift+Enter inserts newline.
- Plus/attachment button.
- Microphone/voice button.
- Send button.
- Disabled/loading state.
- Language-specific placeholder.
- Footer hint.

## Standalone AI/Backend Behavior

- Direct browser-side model completion.
- Hardcoded prompt and local routing helpers.
- Local intent detection for handover/contact.
- Local source inference.
- Local contact/lead prototype.

## Safety And Privacy

- Trust bar says answers come from official sources.
- Privacy/contact consent appears in contact prototype.
- Sensitive facts are present in the standalone prompt and must be backend-governed in the safe widget.

## Admin/Debug/Test

- Bundler exposes some globals such as component references.
- Settings panel exposes demo toggles.
- Local state persistence is used for conversation/UI state.
