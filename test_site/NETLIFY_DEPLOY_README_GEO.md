# Netlify Test Site Deploy

ეს პაკეტი განკუთვნილია მხოლოდ დროებითი test site-სთვის:

```text
https://alte-ai-chat-test.netlify.app
```

ეს არ არის ოფიციალური Alte website და public launch არ არის დასრულებული.

## Option 1 - Git Deploy

Netlify-ში დააყენეთ:

- Repository: `rgelikoshvili-stack/alte-ai-crm`
- Deploy branch: `master`
- Build command: დატოვეთ ცარიელი
- Publish directory:

```text
test_site
```

Deploy-ის შემდეგ უნდა გაიხსნას:

```text
https://alte-ai-chat-test.netlify.app/
https://alte-ai-chat-test.netlify.app/index.html
https://alte-ai-chat-test.netlify.app/join.html
```

## Option 2 - Manual Deploy

Manual deploy-ისას ატვირთეთ `test_site` საქაღალდის შიგთავსი როგორც site root.

Root-ში პირდაპირ უნდა იყოს:

```text
index.html
join.html
alte-ai-chat-widget.js
alte-ai-chat-widget.html
_redirects
```

არ ატვირთოთ project root, თუ Netlify-ში publish directory არ არის დაყენებული `test_site`-ზე.

## ZIP Deploy

Manual upload-ისთვის შეიძლება გამოყენება:

```text
dist/netlify_test_site_deploy.zip
```

ZIP root-ში ფაილები პირდაპირ უნდა იყოს, არა `test_site/` ქვეშ.

## Troubleshooting

- თუ Netlify აჩვენებს `Site not found`, site ჯერ არ არის deploy-ებული ან არასწორი site name/URL იხსნება.
- თუ Netlify აჩვენებს 404-ს, publish directory სავარაუდოდ არასწორია.
- თუ widget იტვირთება, მაგრამ chat request ვერ გადის, შეამოწმეთ DevTools Network/CORS.
- თუ local file listing ჩანს, ეს local browser/server-ია და არა Netlify.

## Safety

- არ შეიყვანოთ phone/email/contact details test smoke-ში.
- browser request-ები უნდა მიდიოდეს მხოლოდ backend-ზე:

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

- frontend-ში API key/secret არ უნდა იყოს.
