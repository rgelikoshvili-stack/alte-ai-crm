# საბოლოო Website Handoff Package

ეს პაკეტი განკუთვნილია Alte-ს ვებ-დეველოპერისთვის. ამ ფაზაში ფაილები მხოლოდ მომზადებულია; რეალურ `alte.edu.ge` ან `join.alte.edu.ge` საიტზე ატვირთვა და embed არ შესრულებულა.

## ასატვირთი ფაილი

ზუსტად ასატვირთი production asset:

```text
dist/widget/alte-ai-chat-widget.js
```

რეკომენდებული საბოლოო URL:

```text
https://alte.edu.ge/assets/alte-ai-chat-widget.js
```

თუ ვებგუნდი სხვა Alte-controlled path-ს დაამტკიცებს, `script src` უნდა შეიცვალოს მხოლოდ დამტკიცებულ საბოლოო URL-ზე.

## Backend URL

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

## Embed Snippet: alte.edu.ge

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

## Embed Snippet: join.alte.edu.ge

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

## უსაფრთხოება

- Frontend-ში Anthropic API key არ არის.
- Frontend-ში direct `api.anthropic.com` call არ არის.
- Browser უკავშირდება მხოლოდ FastAPI backend-ს.
- CRM lead/task/customer creation logic backend-ში რჩება და frontend-დან პირდაპირ არ იქმნება.

## Embed-მდე აუცილებელია

- official content approval.
- privacy/data approval.
- official privacy policy URL.
- final asset URL approval.
- rollback owner.
- smoke test owner.
- explicit website embed approval.

## Embed-ის შემდეგ შესამოწმებელია

- Widget ჩანს რეალურ domain-ზე.
- KA/EN მუშაობს.
- Console-ში CORS error არ არის.
- Browser network-ში direct `api.anthropic.com` call არ არის.
- Backend calls მიდის Cloud Run service-ზე.
- Phone/email/contact details არ იგზავნება smoke test-ში.
- Unexpected lead/task/customer creation არ ხდება no-contact smoke-ში.

## Rollback

1. ამოიღეთ ჩასმული `script` snippet შესაბამისი გვერდის template-იდან ან CMS block-იდან.
2. აღადგინეთ embed-მდე არსებული გვერდის ვერსია.
3. გადაამოწმეთ, რომ widget აღარ იტვირთება real domain-ზე.
4. ჩაწერეთ rollback შედეგი deployment log-ში.
