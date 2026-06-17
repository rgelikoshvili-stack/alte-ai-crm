# Phase 9Z Operator UI Local Entrypoint Diagnosis

PHASE_9Z_OPERATOR_UI_LOCAL_ENTRYPOINT_DIAGNOSIS_STATUS=STATIC_FRONTEND_ENTRYPOINT_CONFIRMED

Decision state:

BACKEND_DEPLOYED_OPERATOR_UI_ENTRYPOINT_READY_PENDING_BROWSER_LOGIN_RETEST

## Finding

The local Operator CRM UI source exists in the repository at:

`frontend/`

Confirmed files:

- `frontend/index.html`
- `frontend/app.js`
- `frontend/styles.css`
- `frontend/README.md`

This is a dependency-free static operator workspace. It is not a Vite, React, Next, or npm app in the current repository state.

## Why npm Failed

`frontend/package.json` is missing because this Operator CRM frontend is intentionally static. The repo docs say to serve `frontend/` with Python's static server, not `npm run dev`.

The stray `frontend/package-lock.json` was produced by the failed local npm attempt and is not required for the Operator CRM UI.

## Archived Zip Source

`docs/knowledge_evidence/uploaded_pro_v2_zip_source/deploy/` is archived evidence for uploaded Pro v2 widget source review. It is not the intended Operator CRM app and must not be used as the local CRM runner.

## Correct Local Runner

From the repository root:

```powershell
.\scripts\start_operator_ui.ps1
```

Equivalent direct command:

```powershell
cd C:\tmp\alte-ai-crm\frontend
python -m http.server 5173 --bind 127.0.0.1
```

Local URL:

`http://127.0.0.1:5173`

## Browser Retest Notes

1. Start the static frontend server.
2. Open `http://127.0.0.1:5173`.
3. Click `Production API`.
4. Open Settings.
5. Log in as `admin_test@alte.edu.ge` using `.local-secrets/temporary_crm_admin_credentials.txt`.

## Safety

- Real Alte site modified: NO
- Public chatbot UI changed: NO
- Backend changed: NO
- Production DB modified: NO
- Migration run: NO
- Seed run: NO
- Secret Manager changed: NO
- Lead created: NO
- Task created: NO
- Customer created: NO
- Public launch: NO-GO
