# GitHub Backup And Release

Current remote URL:

```text
https://github.com/rgelikoshvili-stack/alte-ai-crm
```

## Verify Remote And Status

```powershell
cd C:\tmp\alte-ai-crm
git remote -v
git status --short --branch
```

## Push Backup

Current local branch is `master`.

```powershell
git push -u origin master
```

If the branch is renamed to `main`, use:

```powershell
git branch -M main
git push -u origin main
```

## Release Tag

Recommended tag:

```text
v0.8-deployment-ready
```

Tag commands:

```powershell
git tag v0.8-deployment-ready
git push origin v0.8-deployment-ready
```

## Safety

- Confirm `.env` is not tracked before pushing.
- Never push secrets.
- Never commit API keys, database passwords, screenshots with secrets, or local SQLite databases.
- Run `python -m app.scripts.verify_release_checkpoint`.
- Run `python -m app.scripts.verify_final_preflight`.
