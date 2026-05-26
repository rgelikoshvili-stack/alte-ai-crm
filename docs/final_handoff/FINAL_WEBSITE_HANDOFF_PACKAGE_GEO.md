# საბოლოო Website Handoff Package

ეს პაკეტი განკუთვნილია Alte-ს ვებ-დეველოპერისთვის. ამ ფაზაში ფაილები მხოლოდ მომზადებულია; რეალურ `alte.edu.ge` ან `join.alte.edu.ge` საიტზე ატვირთვა და embed არ შესრულებულა.

## A. რა არის მზად

- Backend Cloud Run URL: `https://alte-ai-crm-backend-226875230147.europe-west1.run.app`
- Final widget asset: `dist/widget/alte-ai-chat-widget.js`
- HTML fallback/preview: `dist/widget/alte-ai-chat-widget.html`
- Safe Pro Sidebar widget: `widget/alte-university-ai-chatbot-safe-pro.html`

## B. სად უნდა აიტვირთოს asset

ზუსტად ასატვირთი production asset:

```text
dist/widget/alte-ai-chat-widget.js
```

Recommended final asset URL:

```text
https://alte.edu.ge/assets/alte-ai-chat-widget.js
```

Status:

```text
PENDING_UPLOAD_BY_ALTE_WEBSITE_TEAM
```

თუ ვებგუნდი სხვა Alte-controlled path-ს დაამტკიცებს, `script src` უნდა შეიცვალოს მხოლოდ დამტკიცებულ საბოლოო URL-ზე.

## Backend URL

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

## C. alte.edu.ge snippet

```html
<!--
  Alte AI Chatbot Safe Pro Sidebar draft snippet for alte.edu.ge.
  Replace the asset URL if the Alte website team uses another approved path.
  Do not use until privacy/content approval is complete.
  Run real-domain smoke after embed.
-->
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

## D. join.alte.edu.ge snippet

```html
<!--
  Alte AI Chatbot Safe Pro Sidebar draft snippet for join.alte.edu.ge.
  Replace the asset URL if the Alte website team uses another approved path.
  Do not use until privacy/content approval is complete.
  Run real-domain smoke after embed.
-->
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

## E. Security rules

- Frontend-ში Anthropic API key არ არის.
- Frontend-ში direct `api.anthropic.com` call არ არის.
- Browser უკავშირდება მხოლოდ FastAPI backend-ს.
- CRM lead/task/customer creation logic backend-ში რჩება და frontend-დან პირდაპირ არ იქმნება.

## F. Before actual embed

- official privacy URL must be inserted.
- content approval policy accepted.
- asset URL confirmed.
- rollback owner assigned.
- smoke owner assigned.

## G. After actual embed

- Widget ჩანს რეალურ domain-ზე.
- KA/EN მუშაობს.
- Console-ში CORS error არ არის.
- Browser network-ში direct `api.anthropic.com` call არ არის.
- Backend calls მიდის Cloud Run service-ზე.
- department routing მოწმდება.
- no-contact guard მოწმდება.
- Phone/email/contact details არ იგზავნება smoke test-ში.
- Unexpected lead/task/customer creation არ ხდება no-contact smoke-ში.

## H. Rollback

1. ამოიღეთ ჩასმული `script` snippet შესაბამისი გვერდის template-იდან ან CMS block-იდან.
2. აღადგინეთ embed-მდე არსებული გვერდის ვერსია.
3. გადაამოწმეთ, რომ widget აღარ იტვირთება real domain-ზე.
4. ჩაწერეთ rollback შედეგი deployment log-ში.
## Phase 9Q-9R Pro v2 განახლება

- საბოლოო სამიზნე ვიზუალი არის ატვირთული Pro v2 standalone chatbot.
- უსაფრთხო production/test ვერსია მომზადებულია backend-only ინტეგრაციით.
- რეალურ Alte საიტზე ატვირთვა და embed ჯერ არ შესრულებულა.
- Netlify test package ხელახლა უნდა აიტვირთოს/დაიდეპლოიდეს browser retest-მდე.

Decision state:

```text
BACKEND_DEPLOYED_PRO_V2_REBUILT_AND_FUNCTION_GAPS_AUDITED_PENDING_NETLIFY_REDEPLOY
```
