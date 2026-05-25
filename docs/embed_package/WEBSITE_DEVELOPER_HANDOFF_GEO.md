# Website Developer Handoff — Alte AI Chatbot

## არჩეული hosting ვარიანტი

არჩეულია Option A — Alte-controlled hosting.

რეკომენდებული final URL:

```text
https://alte.edu.ge/assets/alte-ai-chat-widget.js
```

## ასატვირთი ფაილები

- `dist/widget/alte-ai-chat-widget.html`
- `dist/widget/alte-ai-chat-widget.js`

თუ website team გადაწყვეტს სხვა static path-ს, embed snippet-ში უნდა შეიცვალოს asset URL.

## Backend URL

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

## Domains / Pages

- `alte.edu.ge`
- `join.alte.edu.ge`

## Snippet Examples

Main Alte site:

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
    sourceDomain: "alte.edu.ge",
    defaultLanguage: "ka",
    widgetVariant: "safe_pro_sidebar"
  };
</script>
<script src="https://alte.edu.ge/assets/alte-ai-chat-widget.js" defer></script>
```

Join Alte site:

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
    sourceDomain: "join.alte.edu.ge",
    defaultLanguage: "en",
    widgetVariant: "safe_pro_sidebar"
  };
</script>
<script src="https://alte.edu.ge/assets/alte-ai-chat-widget.js" defer></script>
```

## აუცილებელი პირობები public launch-მდე

- Privacy/content approval დასრულებული უნდა იყოს.
- Final asset URL უნდა დადასტურდეს.
- Real-domain smoke უნდა ჩატარდეს embed-ის შემდეგ.
- Public launch უნდა დამტკიცდეს ცალკე.

## Rollback

- წაშალეთ script snippet გვერდიდან, ან
- გამორთეთ asset/static file, ან
- დააბრუნეთ წინა page version.

## Security

- frontend-ში API key არ არის.
- browser Anthropic/Claude-ს პირდაპირ არ იძახებს.
- browser მხოლოდ FastAPI backend-ს ეძახის.
- frontend CRM lead/task/customer-ს არ ქმნის.
