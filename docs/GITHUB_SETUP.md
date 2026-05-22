# GitHub Setup

Use this guide to connect the local MVP repository to GitHub.

Important: do not commit `.env`, real API keys, local databases, logs, or virtual environments.

## Check Current State

```powershell
cd C:\tmp\alte-ai-crm
git status
git remote -v
```

## If No Remote Exists

```powershell
git remote add origin YOUR_GITHUB_REPO_URL
git branch -M main
git push -u origin main
```

## If Remote Exists

```powershell
git push
```

## Optional Release Tag

```powershell
git tag v0.7-local-mvp
git push origin v0.7-local-mvp
```

## Before Pushing

```powershell
cd C:\tmp\alte-ai-crm\backend
.\.venv\Scripts\Activate.ps1
python -m compileall -q app
python -m pytest -q
python -m app.scripts.verify_release_checkpoint
```
