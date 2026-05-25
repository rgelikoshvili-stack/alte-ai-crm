# Temporary Test Origin Hosting Package

ეს პაკეტი განკუთვნილია დროებითი hosted test origin-ისთვის. რეალური `alte.edu.ge` და `join.alte.edu.ge` ამ ფაზაში არ იცვლება.

## ასატვირთი ფაილები

- `test_site/index.html`
- `test_site/join.html`
- `test_site/alte-ai-chat-widget.js`

## Hosting მოთხოვნები

- Host უნდა მუშაობდეს HTTPS-ზე.
- საბოლოო origin უნდა იყოს exact URL, მაგალითად:

```text
https://alte-chat-test.example.com
```

- URL path მნიშვნელობა არ არის CORS origin-ის ნაწილი; საჭიროა scheme + host + optional port.
- Hosted URL-ის ცნობილი გახდომის შემდეგ backend CORS-მა დროებით უნდა დაუშვას ეს exact origin.
- Wildcard origin არ გამოიყენოთ.

## უსაფრთხოება და scope

- ეს არ არის public Alte launch.
- ეს არ არის actual Alte site embed.
- Smoke test-ში არ შეიყვანოთ phone/email/contact details.
- Browser არ უნდა იძახებდეს `api.anthropic.com`-ს.
- Frontend-ში API key არ უნდა იყოს.
- ტესტის შემდეგ უნდა გადაწყდეს, დარჩეს თუ მოიხსნას დროებითი origin CORS-დან.
