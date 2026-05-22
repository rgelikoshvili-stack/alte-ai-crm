# Local MVP Checklist

Use this checklist to verify the local Alte AI CRM MVP.

- [ ] Open `C:\tmp\alte-ai-crm`.
- [ ] Confirm `git status` is clean.
- [ ] Copy `backend\.env.local.example` to `backend\.env`.
- [ ] Activate backend virtual environment.
- [ ] Install requirements: `pip install -r requirements.txt`.
- [ ] Run migrations: `alembic upgrade head`.
- [ ] Run local setup: `python -m app.scripts.setup_local_demo`.
- [ ] Start backend: `uvicorn app.main:app --reload`.
- [ ] Start widget static server: `cd C:\tmp\alte-ai-crm\widget && python -m http.server 5500`.
- [ ] Open `http://127.0.0.1:5500/demo.html`.
- [ ] Send: `მაინტერესებს ბიზნესის პროგრამაზე ჩარიცხვა`.
- [ ] Send: `ნინო ბერიძე, +995599000000, nino@example.com`.
- [ ] Check `http://127.0.0.1:8000/diagnostics/local-demo`.
- [ ] Run smoke script: `python -m app.scripts.e2e_local_smoke`.
- [ ] Check `http://127.0.0.1:8000/dashboard/overview`.
- [ ] Check `http://127.0.0.1:8000/inbox`.
- [ ] Run tests: `python -m pytest -q`.
- [ ] Confirm no `.env`, local DB, logs, or cache files are staged.
