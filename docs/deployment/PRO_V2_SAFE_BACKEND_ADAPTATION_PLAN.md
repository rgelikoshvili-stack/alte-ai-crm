# Pro v2 Safe Backend Adaptation Plan

## Decision

The uploaded Pro v2 standalone widget is a visual and functional reference only. It is not used directly as production logic.

## Safe Backend Contract

The browser widget remains backend-only and calls only:

```text
/chat/session/start
/chat/message
```

The frontend must not call Anthropic or any model provider directly, must not expose API keys, and must not create leads, tasks, or customers.

## Session Start Payload

The widget starts sessions with the existing backend-compatible schema:

```json
{
  "source_domain": "alte.edu.ge",
  "language": "ka",
  "channel": "website_chat"
}
```

The source domain and language are read from `window.AlteChatWidgetConfig`.

## Message Payload

Messages include the safe routing context:

```json
{
  "conversation_id": "...",
  "session_id": "...",
  "message": "...",
  "source_domain": "alte.edu.ge",
  "language": "ka",
  "selected_department": "admissions",
  "selected_topic": "programs",
  "page_url": "https://...",
  "widget_variant": "pro_v2_safe"
}
```

## UI Adaptation

The safe Pro v2 widget keeps:

- Pro v2-inspired sidebar and department navigation.
- Active department highlight.
- KA/EN switch.
- Reset/new conversation action.
- Quick chips.
- Source cards from backend `used_sources`.
- Operator/handover card when backend requests human routing.
- Contact request notice without collecting phone/email in smoke tests.
- Privacy/consent note.
- Loading/typing and backend unavailable states.
- Mobile responsive behavior.

## Launch Status

This adaptation prepares the Netlify test package only. Netlify redeploy and manual browser retest are still required. Public launch remains NO-GO.
