# Temporary Test Origin Browser Smoke Checklist

## Browser smoke

- [ ] გახსენით hosted test URL.
- [ ] გახსენით DevTools Console.
- [ ] გახსენით DevTools Network.
- [ ] დაადასტურეთ, რომ widget ჩანს.
- [ ] დაადასტურეთ, რომ console errors არ არის.
- [ ] დაადასტურეთ, რომ CORS errors არ არის.
- [ ] დაადასტურეთ, რომ requests მიდის backend-ზე:

```text
https://alte-ai-crm-backend-226875230147.europe-west1.run.app
```

- [ ] დაადასტურეთ, რომ `api.anthropic.com` call არ არის.
- [ ] დაადასტურეთ, რომ frontend API key არ ჩანს.
- [ ] გატესტეთ KA კითხვები `index.html` გვერდზე.
- [ ] გატესტეთ EN კითხვები `join.html` გვერდზე.
- [ ] არ შეიყვანოთ phone/email/contact details.
- [ ] არ შექმნათ intentional lead/task/customer.

## Result rule

PASS მხოლოდ მაშინ ჩაიწეროს, თუ ყველა ზემოთ მოცემული პუნქტი შესრულდა hosted test origin-ზე.
