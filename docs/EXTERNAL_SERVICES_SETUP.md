# External Services Setup

This guide lists the external accounts and services needed to activate AI, deploy Alte AI CRM, and later add omnichannel integrations.

Never commit `.env`, API keys, passwords, screenshots containing secrets, or production credentials.

## A. Immediate Required Services

### 1. Anthropic Console - Claude API

URL: https://console.anthropic.com/

Purpose: main AI provider for the production student chatbot.

Needed for:

- Claude Sonnet chatbot replies
- structured JSON analysis
- admissions/contact/knowledge-based conversation

Required values:

- `ANTHROPIC_API_KEY`
- `AI_PROVIDER=claude`
- `AI_MODEL=claude-sonnet-4-5` or the current Sonnet model

Where to configure locally:

```text
backend/.env
```

Example:

```env
AI_PROVIDER=claude
AI_MODEL=claude-sonnet-4-5
ANTHROPIC_API_KEY=your-real-key
AUTH_REQUIRED=false
```

Important:

- Never commit `backend/.env`.
- Never paste API keys into chat, GitHub, screenshots, or docs.
- Rotate any key that was exposed.

### 2. GitHub

URL: https://github.com/

Purpose: source control, backup, future deployment connection, and release tags.

Needed for:

- pushing the `alte-ai-crm` repo
- version history
- collaboration
- deployment automation later

Commands:

```powershell
cd C:\tmp\alte-ai-crm
git status
git remote -v
git remote add origin YOUR_GITHUB_REPO_URL
git branch -M main
git push -u origin main
git tag v0.7-local-mvp
git push origin v0.7-local-mvp
```

### 3. Google Cloud Console

URL: https://console.cloud.google.com/

Purpose: production hosting.

Needed services:

- Cloud Run for backend
- Cloud SQL PostgreSQL for production database
- Secret Manager for API keys and secrets
- Cloud Storage for uploaded documents/files later
- Cloud Logging for logs

Important: production secrets must go to Secret Manager, not `.env`.

### 4. Google Cloud SQL PostgreSQL

URL: https://console.cloud.google.com/sql

Purpose: production database.

Needed values:

- production `DATABASE_URL`
- database user
- password
- database name
- connection settings for Cloud Run

Local default:

```env
DATABASE_URL=sqlite+aiosqlite:///./alte_ai_crm_local.db
```

Production target: PostgreSQL.

## B. Website Embedding Requirements

Alte website access:

- admin/developer access to `alte.edu.ge`
- admin/developer access to `join.alte.edu.ge` if the widget will be used there

Needed:

- ability to add a script snippet
- backend public URL
- widget JS public URL
- CORS allowed origins:
  - `https://alte.edu.ge`
  - `https://join.alte.edu.ge`

Future embed snippet:

```html
<script>
  window.AlteChatWidgetConfig = {
    apiBaseUrl: "https://YOUR_BACKEND_URL",
    sourceDomain: "alte.edu.ge",
    defaultLanguage: "ka",
    proactiveEnabled: true,
    proactiveDelayMs: 30000
  };
</script>
<script src="https://YOUR_WIDGET_URL/alte-chat-widget.js"></script>
```

## C. Later Services / Not Needed Yet

### 1. Meta Developers

URL: https://developers.facebook.com/

Purpose: WhatsApp, Facebook Messenger, and Instagram Messaging.

Needed later for:

- WhatsApp Business API
- Messenger API
- Instagram Messaging API
- webhook verification
- page/business permissions

Also likely needed: https://business.facebook.com/

Do not implement yet.

### 2. WhatsApp Providers, Optional Later

Options:

- Meta WhatsApp Cloud API
- Twilio
- 360dialog
- Infobip

Purpose: WhatsApp communication channel.

Do not implement yet.

### 3. Email Provider, Optional Later

Options:

- SendGrid: https://sendgrid.com/
- Mailgun: https://www.mailgun.com/
- Amazon SES: https://aws.amazon.com/ses/

Purpose: outbound email notifications and communication.

Do not implement yet.

### 4. SMS Provider, Optional Later

Options:

- Twilio: https://www.twilio.com/
- Infobip: https://www.infobip.com/
- Vonage: https://www.vonage.com/

Purpose: SMS reminders/notifications.

Do not implement yet.

### 5. Monitoring/Error Tracking, Optional Later

Option:

- Sentry: https://sentry.io/

Purpose: production error tracking.

Google Cloud Logging may be enough for MVP.

## D. Recommended Order

Step 1: create/verify GitHub repository and push current code.

Step 2: create Anthropic Console account, add billing, create API key.

Step 3: update local `backend/.env`:

```env
AI_PROVIDER=claude
ANTHROPIC_API_KEY=real_key
AUTH_REQUIRED=false
```

Step 4: run:

```powershell
python -m app.scripts.ai_direct_dry_run
```

Step 5: run backend and Claude live smoke:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
python -m app.scripts.claude_live_smoke
```

Step 6: only after Claude live test passes, prepare Google Cloud deployment.

Step 7: only after backend is deployed, prepare real website embed.

Step 8: only after website chat is stable, plan Meta/WhatsApp/Messenger/Instagram.

## E. Security Rules

- Never commit `.env`.
- Never commit API keys.
- Never paste keys into prompts or screenshots.
- Use Secret Manager in production.
- Keep `AI_PROVIDER=mock` for tests.
- Use Claude only through `ai_service` / `core ai_client`.
- Claude must not mutate CRM directly.
- Knowledge answers must be approved-source based.
- Low confidence or missing source should trigger handover.
