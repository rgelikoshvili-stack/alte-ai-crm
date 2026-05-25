# Alte AI Chatbot Embed Package

ეს პაკეტი მომზადებულია მომავალი website embed-ისთვის. ამ ეტაპზე public launch ან actual embed დამტკიცებული არ არის.

## ფაილები

- `alte_safe_pro_sidebar_embed_snippet.html` — draft snippet `alte.edu.ge`-სთვის
- `join_alte_safe_pro_sidebar_embed_snippet.html` — draft snippet `join.alte.edu.ge`-სთვის

## როგორ გამოიყენოს website admin/developer-მა

1. აირჩიოს საბოლოო static asset URL.
2. შეცვალოს `SCRIPT_SRC_PLACEHOLDER_REPLACE_WITH_FINAL_ASSET_URL`.
3. ჩასვას შესაბამისი snippet დამტკიცებულ test/staging გვერდზე.
4. გაუშვას real-domain smoke.
5. მხოლოდ approval-ის შემდეგ გადავიდეს public rollout-ზე.

## ჯერ არ არის დამტკიცებული

- final asset URL pending
- privacy/content approval pending
- actual site embed pending
- real-domain smoke required after embed

Frontend არ უნდა შეიცავდეს API key-ს და არ უნდა აკეთებდეს Anthropic browser call-ს. ყველა AI/CRM მოქმედება უნდა წავიდეს backend-ზე.
