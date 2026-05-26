# ალტე AI ჩათბოტი — Pro v2

წინასწარ აწყობილი deploy-ready ჩათბოტი ალტეს უნივერსიტეტისთვის. ცოცხალი Claude AI, KA/EN, sidebar-ით 8 დეპარტამენტი, lead capture, ცოცხალი ოპერატორი, ფაილების ატვირთვა.

## 📁 ფაილების სტრუქტურა

```
deploy/
├── index.html              ← მთავარი გვერდი (იხსნება ბრაუზერში)
├── variants/
│   ├── pro-v2-icons.jsx    ← ლოგო, იკონები
│   ├── pro-v2-strings.jsx  ← KA/EN თარგმანი, system prompt
│   ├── pro-v2-chat.jsx     ← ჩათ კომპონენტი (UI + ლოგიკა)
│   ├── pro-v2-modals.jsx   ← Settings + Lead Capture
│   ├── pro-v2-page.jsx     ← faux alte.edu.ge backdrop
│   └── tweaks-panel.jsx    ← დიზაინერის Tweaks პანელი
├── api/
│   └── chat.js             ← Vercel serverless function (Claude API proxy)
├── vercel.json             ← Vercel კონფიგი
├── package.json
├── .env.example            ← გადააკოპირე .env-ად, ჩასვი შენი API key
├── .gitignore
└── README.md (ეს ფაილი)
```

---

## 🚀 5-წუთიანი deploy (Vercel-ით — რეკომენდებული)

### 1. დააყენე Vercel CLI
```bash
npm i -g vercel
```

### 2. შედი ანგარიშში
```bash
vercel login
```

### 3. მიიღე Anthropic API key
1. გადადი: https://console.anthropic.com/settings/keys
2. დააჭირე **"Create Key"**
3. დააკოპირე — `sk-ant-api03-...`-ით იწყება
4. ბილინგი: `Billing` ტაბში დადე ~$10 (საკმარისია 10,000+ კითხვისთვის)

### 4. დააყენე environment variable
```bash
cd deploy/
vercel env add ANTHROPIC_API_KEY
# შემდეგ ჩასვი key-ი, აირჩიე "Production, Preview, Development"
```

### 5. Deploy!
```bash
vercel deploy --prod
```

5–10 წამში გექნება URL, მაგ.: `https://alte-ai-chat.vercel.app`

გახსენი ბრაუზერში → ცოცხალია 🎉

---

## 🌐 დომენის მიბმა (chat.alte.edu.ge)

1. Vercel Dashboard → შენი პროექტი → **Settings → Domains**
2. დაამატე `chat.alte.edu.ge`
3. DNS პროვაიდერთან (სადაც alte.edu.ge ცხოვრობს):
   - დაამატე `CNAME` რეკორდი:
     - **Name:** `chat`
     - **Value:** `cname.vercel-dns.com`
4. 5–60 წუთში HTTPS-ით ცოცხალია

---

## 🧪 ლოკალურად ტესტი

```bash
cd deploy/
cp .env.example .env
# გახსენი .env და ჩასვი შენი API key

vercel dev
```

გახსენი http://localhost:3000

---

## 🔧 alte.edu.ge საიტში ჩასმა (embed)

ვარიანტი 1 — **iframe** (უმარტივესი):
```html
<iframe src="https://chat.alte.edu.ge" style="position:fixed;bottom:0;right:0;width:440px;height:700px;border:0;z-index:9999"></iframe>
```

ვარიანტი 2 — **მხოლოდ ჩათ ვიჯეტი** (გვერდის ფონის გარეშე):
- იხილე `variants/pro-v2-page.jsx`
- ამოიღე `<FauxNav>`, `<FauxHero>`, `<FauxFooter>`
- დატოვე მხოლოდ `<Launcher>` + `<ChatWidget>`

ვარიანტი 3 — **ფლოატინგ button + iframe**:
```html
<!-- alte.edu.ge-ის ნებისმიერ გვერდზე -->
<script>
(function(){
  var btn = document.createElement('button');
  btn.innerHTML = '💬 ალტე ჩათი';
  btn.style.cssText = 'position:fixed;bottom:22px;right:22px;background:#074045;color:#fff;border:0;padding:14px 22px;border-radius:28px;font-size:14px;font-weight:700;cursor:pointer;z-index:9999;box-shadow:0 10px 30px rgba(0,0,0,0.2)';
  btn.onclick = function(){
    var f = document.createElement('iframe');
    f.src = 'https://chat.alte.edu.ge';
    f.style.cssText = 'position:fixed;bottom:0;right:0;width:440px;height:700px;border:0;z-index:9999;border-radius:18px;box-shadow:0 20px 60px rgba(0,0,0,0.3)';
    document.body.appendChild(f);
    btn.remove();
  };
  document.body.appendChild(btn);
})();
</script>
```

---

## ⚙️ კონფიგურაცია

### System Prompt (AI-ის ქცევა)
ჩაირედაქტირე: `variants/pro-v2-strings.jsx` → `altePrompt()` ფუნქცია

აქ მიეცი Claude-ს:
- სრული ფაქტები ალტეს შესახებ (ფასები, ვადები, პროგრამები)
- ცოცხალი ოპერატორის სამუშაო საათები
- რა შემთხვევაში გადართოს ოპერატორზე
- რა URL-ები მიუთითოს წყაროდ

### დეპარტამენტები
ჩაირედაქტირე: `variants/pro-v2-strings.jsx` → `DEPTS` მასივი

### ფერები / ბრენდი
ჩაირედაქტირე: `index.html` → `:root` CSS ვარიაბლები
ან გამოიყენე **Tweaks panel** ბრაუზერში live preview-სთვის.

### Model შეცვლა
`api/chat.js` → `model: 'claude-haiku-4-5'`

ალტერნატივები:
- `claude-haiku-4-5` — სწრაფი, იაფი ($0.001/კითხვა) ← **რეკომენდებული**
- `claude-sonnet-4-5` — უფრო ჭკვიანი, ძვირი ($0.015/კითხვა)

---

## 💰 ფასები (პროდუქცია)

| ნივთი | ფასი |
|---|---|
| Vercel Hobby | **$0/თვე** |
| Anthropic API (Haiku, 1,000 კითხვა/თვე) | **~$1/თვე** |
| Anthropic API (Haiku, 10,000 კითხვა/თვე) | **~$10/თვე** |
| Anthropic API (Haiku, 100,000 კითხვა/თვე) | **~$100/თვე** |
| დომენი (chat.alte.edu.ge) | $0 (subdomain) |

---

## 🔐 უსაფრთხოება

✅ API key **არასოდეს** ხვდება HTML-ში — ცხოვრობს მხოლოდ Vercel-ის env-ში
✅ HTTPS automatic
✅ Rate limiting — Vercel ავტომატურად ზღუდავს abuse-ს
✅ Conversation length cap — 30 turn (`api/chat.js`-ში)

### სრული უსაფრთხოებისთვის დაამატე:
- **CAPTCHA** — Cloudflare Turnstile (10-წუთიანი ინტეგრაცია)
- **Rate limit per IP** — Upstash Redis
- **PII filtering** — Anthropic API-ში ჩაშენებული, ან custom regex

---

## 🤝 ცოცხალი ოპერატორის ინტეგრაცია

ამჟამად Lead capture-ის Submit-ი მხოლოდ confirmation აჩვენებს.
რეალური CRM-თან ჩასართავად — `variants/pro-v2-chat.jsx` → `onLeadSubmit` ფუნქცია:

```js
const onLeadSubmit = async (formData) => {
  // შენი CRM-ის webhook
  await fetch('/api/lead', {
    method: 'POST',
    body: JSON.stringify(formData),
  });
  setShowLead(false);
  setMessages(m => [...m, { role:'assistant', text: S.leadDone }]);
};
```

დაამატე `api/lead.js` რომელიც გადასცემს HubSpot/Pipedrive/Slack-ს.

---

## 📊 Analytics (არასავალდებულო)

დაამატე `<head>`-ში:
```html
<!-- Plausible (privacy-friendly) -->
<script defer data-domain="chat.alte.edu.ge" src="https://plausible.io/js/script.js"></script>

<!-- ან Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
```

---

## ❓ ხშირი კითხვები

**Q: მუშაობს iPhone/Android-ზე?**
A: დიახ, სრულად responsive.

**Q: მუშაობს offline?**
A: UI კი, AI პასუხები არა (საჭიროა internet).

**Q: შემიძლია გადავიტანო AWS/Cloudflare-ზე?**
A: დიახ. `api/chat.js` Standard Node.js-ია, ნებისმიერი serverless platform-ი მუშაობს. სტატიკური ფაილები — ნებისმიერ CDN-ზე.

**Q: Babel ბრაუზერში — ნელია?**
A: First load-ი 2–3 წამი. პროდუქციისთვის რეკომენდებულია prebuild (იხ. "Build optimization" ქვემოთ).

---

## 🏗️ Build optimization (პროდუქცია)

ამჟამად JSX ბრაუზერში კომპილირდება Babel-ით (~500KB load). რომ უფრო სწრაფი იყოს:

1. დააყენე Vite ან esbuild
2. დაკომპილირე `variants/*.jsx` → `dist/bundle.js`
3. HTML-ში შეცვალე `<script type="text/babel">` → `<script src="dist/bundle.js">`

შემიძლია გავაკეთო თუ გჭირდება.

---

## 📝 ლიცენზია

ალტეს უნივერსიტეტისთვის შექმნილი. შიდა გამოყენებისთვის.

---

**კითხვები? ცვლილებები?** დაბრუნდი ჩათში — გავაკეთებ.
