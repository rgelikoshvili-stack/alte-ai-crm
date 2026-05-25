# Netlify Site Name / Deploy Troubleshooting

## მიმდინარე პრობლემა

URL:

```text
https://alte-ai-chat-test.netlify.app/index.html
```

აჩვენებს Netlify-ის default გვერდს:

```text
Site not found / not deployed
```

ეს ნიშნავს, რომ backend/CORS პრობლემა არ არის. ეს არის Netlify hosting/deploy ან site-name პრობლემა.

## რას ნიშნავს ეს შეცდომა

- Netlify site ჯერ არ არის deployed.
- ან იხსნება არასწორი Netlify site URL.
- ან Netlify-ში site name არ არის `alte-ai-chat-test`.
- ან deployment არ არის `Published` სტატუსში.

## რა უნდა გადამოწმდეს Netlify Dashboard-ში

1. გახსენით Netlify dashboard.
2. იპოვეთ ის site, სადაც test chatbot უნდა იყოს ატვირთული.
3. გადაამოწმეთ რეალური Netlify site URL.
4. თუ site name არ არის `alte-ai-chat-test`, გააკეთეთ ერთ-ერთი:
   - გახსენით რეალური Netlify URL, რომელიც dashboard-ში წერია.
   - ან rename გააკეთეთ site-ზე: `alte-ai-chat-test`.
5. გადაამოწმეთ, რომ deploy status არის:

```text
Published
```

## სწორი package

სწორი deploy package არის:

```text
dist/netlify_test_site_deploy.zip
```

ეს ZIP უნდა აიტვირთოს სწორ Netlify site-ზე.

ZIP root-ში ფაილები პირდაპირ დევს:

```text
index.html
join.html
alte-ai-chat-widget.js
alte-ai-chat-widget.html
_redirects
README_GEO.md
NETLIFY_DEPLOY_README_GEO.md
```

## Git Deploy-ის შემთხვევაში

თუ Netlify Git deploy გამოიყენება:

- Repository: `rgelikoshvili-stack/alte-ai-crm`
- Branch: `master`
- Build command: ცარიელი
- Publish directory:

```text
test_site
```

## წარმატებული შედეგი

სწორი deploy-ის შემდეგ ეს URL-ები უნდა გაიხსნას:

```text
https://alte-ai-chat-test.netlify.app/
https://alte-ai-chat-test.netlify.app/index.html
https://alte-ai-chat-test.netlify.app/join.html
```

წარმატებულ გვერდზე უნდა გამოჩნდეს:

```text
Alte AI Chatbot - Test Site
```

ან ვიზუალურად იგივე სათაური dash-ით:

```text
Alte AI Chatbot — Test Site
```

## რა არ უნდა შეიცვალოს

- production backend არ იცვლება.
- Cloud Run არ იცვლება.
- CORS არ იცვლება.
- DB/Secret Manager არ იცვლება.
- რეალური `alte.edu.ge` / `join.alte.edu.ge` არ იცვლება.
- public launch არ მონიშნოთ დასრულებულად.
