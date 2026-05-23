# DATABASE_URL Construction

This guide uses placeholders only. Never commit a real production `DATABASE_URL`.

## Local SQLite

Local demo and tests can use SQLite:

```text
sqlite+aiosqlite:///./alte_ai_crm_local.db
```

SQLite is not acceptable for production.

## Production PostgreSQL Async Format

Production uses Cloud SQL PostgreSQL with SQLAlchemy async:

```text
postgresql+asyncpg://USER:PASSWORD@HOST:5432/DB_NAME
```

Planned project values:

- `USER=alte_app`
- `DB_NAME=alte_ai_crm`
- Password comes from the prepared DB password secret.
- Host depends on Cloud SQL connection method.

Example with placeholders:

```text
postgresql+asyncpg://alte_app:DB_PASSWORD@HOST:5432/alte_ai_crm
```

## Cloud SQL Connection Notes

Cloud Run can connect to Cloud SQL through the managed Cloud SQL integration/connector. The exact host or socket format must be selected during the deployment execution phase.

Public or private IP may be used depending on network design, but the final choice must be reviewed before production deployment.

## Secret Manager Storage

The final production `DATABASE_URL` must be stored in Secret Manager as:

`alte-database-url`

Do not write the real connection string into docs, Git, screenshots, or chat.
