# Alte AI Chatbot Embed Package

ეს პაკეტი მომზადებულია მომავალი website embed-ისთვის. ამ ეტაპზე public launch ან actual embed დამტკიცებული არ არის.

## ფაილები

- `alte_safe_pro_sidebar_embed_snippet.html` — draft snippet `alte.edu.ge`-სთვის
- `join_alte_safe_pro_sidebar_embed_snippet.html` — draft snippet `join.alte.edu.ge`-სთვის

## როგორ გამოიყენოს website admin/developer-მა

1. გამოიყენოს Alte-controlled hosting.
2. ატვირთოს `dist/widget/alte-ai-chat-widget.html` და `dist/widget/alte-ai-chat-widget.js`.
3. რეკომენდებული URL არის `https://alte.edu.ge/assets/alte-ai-chat-widget.js`.
4. თუ სხვა approved path გამოიყენება, snippet-ში შეცვალოს asset URL.
5. ჩასვას შესაბამისი snippet დამტკიცებულ test/staging გვერდზე.
6. გაუშვას real-domain smoke.
7. მხოლოდ approval-ის შემდეგ გადავიდეს public rollout-ზე.

## ჯერ არ არის დამტკიცებული

- final asset upload pending
- privacy/content approval pending
- actual site embed pending
- real-domain smoke required after embed

Frontend არ უნდა შეიცავდეს API key-ს და არ უნდა აკეთებდეს Anthropic browser call-ს. ყველა AI/CRM მოქმედება უნდა წავიდეს backend-ზე.
