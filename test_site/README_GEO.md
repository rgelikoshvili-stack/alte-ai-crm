# Alte AI Chatbot Test Site

ეს არის ცალკე test package Safe Pro Sidebar widget-ის სანახავად. რეალური `alte.edu.ge` ან `join.alte.edu.ge` ამ ფაზაში არ იცვლება.

## Local preview

```powershell
cd C:\tmp\alte-ai-crm\test_site
python -m http.server 5500
```

გახსენით:

```text
http://127.0.0.1:5500/index.html
http://127.0.0.1:5500/join.html
```

## რა მოწმდება

- UI შეიძლება preview-ით ნახოთ ლოკალურად.
- Widget იყენებს production backend URL-ს.
- Browser chat შეიძლება დაიბლოკოს production CORS-ის გამო.
- სრული browser test-ს სჭირდება allowed origin.
- API behavior მაინც მოწმდება backend smoke scripts-ით.

## უსაფრთხოება

- Frontend-ში API key არ არის.
- Browser direct AI provider call არ უნდა იყოს.
- Contact-flow test არ უნდა გაეშვას.
- Phone/email/contact details არ უნდა გაიგზავნოს smoke test-ში.
