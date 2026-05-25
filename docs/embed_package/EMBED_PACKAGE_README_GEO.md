# Alte AI Chatbot Embed Package

## Phase 9L-M-N Final Handoff

- Final website handoff package: `docs/final_handoff/FINAL_WEBSITE_HANDOFF_PACKAGE_GEO.md`
- Asset manifest: `docs/final_handoff/WIDGET_ASSET_MANIFEST.md`
- Asset upload: not executed.
- Actual site embed: not executed.
- Public launch: NO-GO until explicit approvals, live asset URL, site embed, and real-domain smoke are completed and recorded.

ეს პაკეტი მომზადებულია მომავალი website embed-ისთვის. ამ ეტაპზე public launch ან actual embed დამტკიცებული არ არის.

## ფაილები

- `alte_safe_pro_sidebar_embed_snippet.html` - draft snippet `alte.edu.ge`-სთვის.
- `join_alte_safe_pro_sidebar_embed_snippet.html` - draft snippet `join.alte.edu.ge`-სთვის.
- `WEBSITE_DEVELOPER_HANDOFF_GEO.md` - website developer handoff.
- `docs/final_handoff/FINAL_WEBSITE_HANDOFF_PACKAGE_GEO.md` - final website handoff package.

## როგორ გამოიყენოს website admin/developer-მა

1. გამოიყენოს Alte-controlled hosting.
2. ატვირთოს `dist/widget/alte-ai-chat-widget.js`.
3. რეკომენდებული URL არის `https://alte.edu.ge/assets/alte-ai-chat-widget.js`.
4. თუ სხვა approved path გამოიყენება, snippet-ში შეცვალოს asset URL.
5. ჩასვას შესაბამისი snippet დამტკიცებულ გვერდზე მხოლოდ content/privacy approval-ის შემდეგ.
6. გაუშვას real-domain smoke embed-ის შემდეგ.
7. მხოლოდ explicit approval-ის შემდეგ გადავიდეს public rollout-ზე.

## ჯერ არ არის დამტკიცებული

- final asset upload pending.
- privacy/content approval pending.
- official privacy URL pending.
- actual site embed pending.
- real-domain smoke required after embed.

Frontend არ უნდა შეიცავდეს API key-ს და არ უნდა აკეთებდეს Anthropic browser call-ს. ყველა AI/CRM მოქმედება უნდა წავიდეს backend-ზე.
