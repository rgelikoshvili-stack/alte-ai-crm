# Netlify Test Site Deployment Fix

## მიზანი

Netlify test origin `https://alte-ai-chat-test.netlify.app` ამჟამად აჩვენებს `Site not found / not deployed` გვერდს. Backend CORS მზად არის, მაგრამ browser smoke ვერ შესრულდება, სანამ test site სწორად არ დაიდება Netlify-ზე.

## Publish Directory

Netlify publish directory უნდა იყოს:

```text
test_site
```

## აუცილებელი ფაილები

Netlify-ზე site root-ში უნდა იყოს ეს ფაილები:

```text
index.html
join.html
alte-ai-chat-widget.js
```

Source repo-ში ეს ფაილები მდებარეობს:

```text
test_site/index.html
test_site/join.html
test_site/alte-ai-chat-widget.js
```

## Drag-and-Drop Deploy

თუ Netlify drag-and-drop deploy გამოიყენება:

1. გახსენით `C:\tmp\alte-ai-crm\test_site`.
2. ატვირთეთ `test_site` საქაღალდის შიგთავსი როგორც site root.
3. ალტერნატიულად, ატვირთეთ თვითონ `test_site` საქაღალდე ისე, რომ Netlify-მ root-ად გამოიყენოს მისი შიგთავსი.
4. დარწმუნდით, რომ `index.html`, `join.html`, და `alte-ai-chat-widget.js` root-ზე ჩანს.

## Git Deploy

თუ Netlify Git deploy გამოიყენება:

1. Repository მიუთითეთ Alte AI CRM repo-ზე.
2. Build command საჭირო არ არის, თუ static files პირდაპირ ქვეყნდება.
3. Publish directory დააყენეთ:

```text
test_site
```

## Verification URLs

Deploy-ის შემდეგ უნდა გაიხსნას:

```text
https://alte-ai-chat-test.netlify.app/
https://alte-ai-chat-test.netlify.app/index.html
https://alte-ai-chat-test.netlify.app/join.html
```

## Smoke Test Notes

- ეს არ არის ოფიციალური Alte website.
- რეალური Alte site არ უნდა შეიცვალოს ამ ტესტისთვის.
- browser smoke-ში არ შეიყვანოთ ტელეფონი, ელფოსტა ან სხვა contact details.
- DevTools Network-ში API calls უნდა მიდიოდეს მხოლოდ production FastAPI backend-ზე:

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

- Browser-იდან direct `api.anthropic.com` call არ უნდა იყოს.
- Frontend-ში API key/secret არ უნდა გამოჩნდეს.
