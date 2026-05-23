from __future__ import annotations

from dataclasses import dataclass

from app.api.routes_system import database_type, is_placeholder_key
from app.core.config import get_settings


@dataclass
class StartupCheck:
    name: str
    passed: bool
    detail: str
    critical: bool = True


def validate_startup() -> dict:
    settings = get_settings()
    environment = settings.ENVIRONMENT.lower().strip()
    provider = settings.AI_PROVIDER.lower().strip()
    db_type = database_type(settings.DATABASE_URL)
    checks = [
        StartupCheck("DATABASE_URL exists", bool(settings.DATABASE_URL.strip()), f"database_type={db_type}"),
        StartupCheck("JWT_SECRET exists", bool(settings.JWT_SECRET.strip()), "configured" if settings.JWT_SECRET else "missing"),
        StartupCheck("ENVIRONMENT exists", bool(settings.ENVIRONMENT.strip()), settings.ENVIRONMENT or "missing"),
        StartupCheck("APP_VERSION exists", bool(settings.APP_VERSION.strip()), settings.APP_VERSION or "missing"),
    ]

    if provider == "claude":
        checks.append(
            StartupCheck(
                "ANTHROPIC_API_KEY valid for Claude",
                not is_placeholder_key(settings.ANTHROPIC_API_KEY),
                "configured" if not is_placeholder_key(settings.ANTHROPIC_API_KEY) else "missing_or_placeholder",
            )
        )

    if environment == "production":
        checks.extend(
            [
                StartupCheck(
                    "AUTH_REQUIRED true in production",
                    settings.AUTH_REQUIRED is True,
                    f"AUTH_REQUIRED={settings.AUTH_REQUIRED}",
                ),
                StartupCheck(
                    "CORS_ORIGINS exists in production",
                    bool(settings.CORS_ORIGINS.strip()),
                    f"origin_count={len(settings.cors_origins_list)}",
                ),
                StartupCheck(
                    "Production database is PostgreSQL",
                    db_type == "postgresql",
                    f"database_type={db_type}",
                ),
            ]
        )

    return {
        "passed": all(check.passed or not check.critical for check in checks),
        "environment": settings.ENVIRONMENT,
        "ai_provider": settings.AI_PROVIDER,
        "database_type": db_type,
        "checks": [check.__dict__ for check in checks],
    }


def main() -> None:
    result = validate_startup()
    for check in result["checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"{status} {check['name']}: {check['detail']}")
    print(f"database_type={result['database_type']}")
    print(f"ai_provider={result['ai_provider']}")
    print(f"environment={result['environment']}")
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
