# Pro v2 Standalone UI Audit

Source evidence:

```text
docs/knowledge_evidence/uploaded_pro_v2_widget/Alte_AI_Chat_Pro_v2_standalone.html
```

## Scope

The uploaded Pro v2 standalone file was reviewed as a UI/UX reference only. It is not a production asset and must not be used as browser logic for the Alte backend widget.

## UI Findings

- Layout: polished standalone page with a floating chat launcher and expanded chat panel. The chat uses a two-column composition: narrow navigation sidebar plus main conversation area.
- Sidebar: brand block, department/navigation items, active item highlight, compact footer identity row, and a collapsed/mobile-friendly concept.
- Department list: admissions, international, finance, medicine, student services, IT/support, and operator-style routing concepts are represented.
- Header/topbar: assistant identity, online/backend status, language switch, utility actions, and reset/settings style controls.
- Chat area: warm paper/cream background, bot/user message bubbles, compact source/status rows, quick replies, and a typing state.
- Message bubbles: bot bubbles are light/paper with subtle borders; user bubbles use deep Alte teal.
- Quick chips: rounded pill chips for common admission, finance, medicine, international, and support topics.
- KA/EN switch: language selection is a first-class header control and affects UI strings and sample prompts.
- Reset button: visible topbar control for clearing/restarting the conversation.
- Source cards: visual cards for answer evidence/sources are part of the expected experience.
- Operator/handover card: warm accent styling is used for human handover or department routing.
- Contact request card: exists as a prototype pattern, but production frontend must not create leads/tasks/customers directly.
- Colors: dominant Alte deep teal, cream/paper surfaces, muted ink, light borders, and orange accent.
- Spacing/radius/typography: compact SaaS-style spacing, 12-18px radius, Inter/Noto Sans Georgian style sans typography, restrained shadows.
- Mobile behavior: responsive panel concept with sidebar collapsing/reflowing for narrow screens.

## Safety Scan

- `api.anthropic.com`: not present as a literal endpoint in the outer template, but the bundled standalone logic uses direct browser-side Claude completion APIs.
- `ANTHROPIC_API_KEY`: absent.
- Anthropic secret-key prefix: absent.
- Hardcoded AI prompt: present in bundled standalone logic.
- Hardcoded tuition/deadline/fact patterns: present in bundled standalone prompt/content logic.
- Frontend lead/task/customer creation: prototype contact/lead-style behavior is present conceptually and must not be carried into production logic.

## Production Decision

The Pro v2 standalone file is approved only as a visual and interaction reference. The safe production/test widget must keep the existing FastAPI backend as the source of truth and must only call:

```text
/chat/session/start
/chat/message
```

Public launch remains NO-GO until hosted browser retest, real Alte embed, real-domain smoke, and final approvals are completed.
