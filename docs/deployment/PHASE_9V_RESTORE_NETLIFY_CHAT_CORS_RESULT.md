# Phase 9V - Restore Netlify Chat CORS

PHASE_9V_RESTORE_NETLIFY_CHAT_CORS_STATUS=READY_PENDING_BROWSER_RETEST

Decision state:

BACKEND_DEPLOYED_NETLIFY_CHAT_CORS_RESTORED_PENDING_BROWSER_RETEST

## Scope

This phase covers only public chatbot CORS for the Netlify test origin:

`https://nimble-croissant-2f66e8.netlify.app`

The local operator admin panel issue is separate and was not changed in this phase.

## Root Cause

- The active Cloud Run revision already had the exact Netlify origin in `CORS_ORIGINS`.
- Preflight for `/chat/message` from the Netlify origin returned `Access-Control-Allow-Origin: https://nimble-croissant-2f66e8.netlify.app`.
- Real `POST /chat/session/start` returned backend `500` and did not include `Access-Control-Allow-Origin`, causing the browser to show a CORS warning on the failed request.
- The CORS allowlist was correct; the missing browser header was on backend error responses.

## Fix

- CORS middleware was moved to the outermost user middleware position in `backend/app/main.py`.
- A minimal safe error middleware now converts unhandled exceptions into generic `500` JSON responses before they leave the app stack, allowing the outer CORS middleware to attach the exact allowed origin header.
- This is a minimal CORS reliability change so backend error responses, including `500`, still carry the exact allowed origin header.
- No wildcard CORS was added.

## Exact Origin

- Restored/confirmed origin: `https://nimble-croissant-2f66e8.netlify.app`
- Wildcard CORS used: NO

## Endpoints Covered

- `/chat/session/start`
- `/chat/message`
- `/chat/handover/{conversation_id}` preflight only

## Verification

- Cloud Run config/image deploy executed: YES
- Previous serving revision: `alte-ai-crm-backend-00015-ftf`
- Current serving revision: `alte-ai-crm-backend-00016-2gk`
- Image tag: `v0.9-netlify-cors-error-headers`
- `/health`: 200
- `/version`: 200
- `/diagnostics/ai`: 200, Claude enabled, no secrets exposed
- `/dashboard/overview` without auth: 401
- CORS preflight for `/chat/session/start`: 200 with exact Netlify origin
- CORS preflight for `/chat/message`: 200 with exact Netlify origin
- CORS preflight for `/chat/handover/{conversation_id}`: 200 with exact Netlify origin
- Real POST `/chat/session/start`: still returns backend `500` before DB repair, but now includes `Access-Control-Allow-Origin: https://nimble-croissant-2f66e8.netlify.app`.
- Remaining functional blocker: backend `500` on session start. This phase does not modify production DB or Secret Manager.
- Python/httpx smoke from this environment can return `ConnectError`; curl/PowerShell checks reached Cloud Run.

## Safety

- Production DB modified: NO
- Migration/seed run: NO
- Secret Manager changed: NO
- Real Alte site modified: NO
- Contact details sent: NO
- Lead/task/customer intentionally created: NO
- Public launch: NO

## Next Step

Manual browser retest after backend redeploy:

`https://nimble-croissant-2f66e8.netlify.app/join.html`
