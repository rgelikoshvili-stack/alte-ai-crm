# Claude Live Test Guide

This guide is for a controlled local test of `AI_PROVIDER=claude`.

Never commit `.env` or any real API key.

## Configure Local Claude Mode

Edit `backend\.env`:

```env
AI_PROVIDER=claude
ANTHROPIC_API_KEY=your-real-key
AUTH_REQUIRED=false
```

Keep the local database and local CORS values from `.env.local.example`.

## Run Backend

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

## Run Widget Demo

```powershell
cd C:\tmp\alte-ai-crm\widget
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500/demo.html
```

## Safe Test Messages

- `სად მდებარეობს უნივერსიტეტი?`
- `მაინტერესებს ბიზნესის პროგრამაზე ჩარიცხვა`
- `ნინო ბერიძე, +995599000000, nino@example.com`
- `What are the admission steps?`

Do not use sensitive personal data during testing.

## Direct AI Dry Run

This calls the local AI service layer directly and prints sanitized output only.

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.ai_direct_dry_run
```

## Claude Live HTTP Smoke

This uses the local backend HTTP endpoints. It does not call Anthropic directly from the script.

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m app.scripts.claude_live_smoke
```

The script refuses to run unless:

- `AI_PROVIDER=claude`
- `ANTHROPIC_API_KEY` is present and not a placeholder

## Fallback Behavior

Claude responses must be structured JSON. If Claude fails, times out, returns invalid JSON, or returns low confidence, the system should use a safe handover-style response. Claude never mutates CRM data directly. The chat service applies business rules and creates customers, leads, tasks, messages, and handovers.

## Switch Back to Mock

Edit `backend\.env`:

```env
AI_PROVIDER=mock
ANTHROPIC_API_KEY=local-placeholder
```

Restart the backend.
