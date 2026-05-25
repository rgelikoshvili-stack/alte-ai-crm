# Website Developer Handoff - Alte AI Chatbot

## Phase 9L-M-N Final Package

- Final handoff package: `docs/final_handoff/FINAL_WEBSITE_HANDOFF_PACKAGE_GEO.md`
- Asset manifest: `docs/final_handoff/WIDGET_ASSET_MANIFEST.md`
- Actual upload: not executed.
- Actual embed: not executed.
- Final asset URL: pending website approval unless explicitly replaced by the approved live URL.
- Public launch: blocked until content/privacy approvals, official privacy URL, asset upload, actual embed, real-domain smoke, and explicit launch approval are recorded.

## არჩეული hosting ვარიანტი

არჩეულია Option A - Alte-controlled hosting.

რეკომენდებული final URL:

```text
https://alte.edu.ge/assets/alte-ai-chat-widget.js
```

## ასატვირთი ფაილები

- `dist/widget/alte-ai-chat-widget.html`
- `dist/widget/alte-ai-chat-widget.js`

თუ website team გადაწყვეტს სხვა static path-ს, embed snippet-ში უნდა შეიცვალოს asset URL მხოლოდ დამტკიცებულ live URL-ზე.

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
- Official privacy policy URL უნდა იყოს დამტკიცებული.
- Final asset URL უნდა დადასტურდეს.
- Real-domain smoke უნდა ჩატარდეს embed-ის შემდეგ.
- Public launch უნდა დამტკიცდეს ცალკე.

## Phase 9J/9L Status

- Option A selected: Alte-controlled hosting.
- Final URL placeholder: `https://alte.edu.ge/assets/alte-ai-chat-widget.js`
- Actual upload: not done.
- Actual embed: not done.
- Real-domain smoke: not executed.
- Public launch: NO-GO.

ატვირთვამდე/ჩასმამდე website developer-მა უნდა დაადასტუროს:

- საბოლოო asset path.
- გვერდები, სადაც snippet ჩაიდება.
- rollback მეთოდი.
- rollback owner.
- real-domain smoke owner and schedule.

## Rollback

- წაშალეთ script snippet გვერდიდან, ან
- გამორთეთ asset/static file, ან
- დააბრუნეთ წინა page version.

## Security

- Frontend-ში API key არ არის.
- Browser Anthropic/Claude-ს პირდაპირ არ იძახებს.
- Browser მხოლოდ FastAPI backend-ს ეძახის.
- Frontend CRM lead/task/customer-ს არ ქმნის.
