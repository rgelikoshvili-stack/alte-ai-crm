from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
DEPLOYMENT_DOCS = PROJECT_ROOT / "docs" / "deployment"
SCRIPTS_ROOT = PROJECT_ROOT / "scripts"

SECRET_PATTERNS = [
    re.compile(r"sk-ant-", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY\s*=\s*sk-", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]

REAL_DATABASE_URL_PATTERN = re.compile(
    r"postgresql\+asyncpg://(?!USER:PASSWORD@)(?!alte_app:DB_PASSWORD@)[^:\s`]+:[^@\s`]+@[^/\s`]+/[^\s`]+",
    re.IGNORECASE,
)


@dataclass
class SecretVersionsExecutionCheck:
    name: str
    passed: bool
    detail: str = ""


def secret_version_statuses_documented(root: Path = DEPLOYMENT_DOCS) -> SecretVersionsExecutionCheck:
    combined = "\n".join(
        [
            (root / "SECRET_MANAGER_APPROVAL_GATE.md").read_text(encoding="utf-8"),
            (root / "SECRET_PREPARATION_CHECKLIST.md").read_text(encoding="utf-8"),
            (root / "PRODUCTION_READINESS_DECISION.md").read_text(encoding="utf-8"),
            (root / "FINAL_PREFLIGHT_GATE.md").read_text(encoding="utf-8"),
        ]
    )
    required = [
        "alte-db-password: CONTAINER_CREATED / VERSION_ADDED",
        "alte-jwt-secret: CONTAINER_CREATED / VERSION_ADDED",
        "alte-anthropic-api-key: CONTAINER_CREATED / VERSION_ADDED",
        "alte-database-url: CONTAINER_CREATED / VERSION_PENDING_UNTIL_CLOUD_SQL_EXISTS",
    ]
    missing = [item for item in required if item not in combined]
    return SecretVersionsExecutionCheck("Secret version statuses documented", not missing, ", ".join(missing))


def database_url_pending_until_cloud_sql(root: Path = DEPLOYMENT_DOCS) -> SecretVersionsExecutionCheck:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.md"))
    return SecretVersionsExecutionCheck(
        "DATABASE_URL version remains pending",
        "VERSION_PENDING_UNTIL_CLOUD_SQL_EXISTS" in combined,
    )


def decision_remains_no_go(root: Path = DEPLOYMENT_DOCS) -> SecretVersionsExecutionCheck:
    text = (root / "PRODUCTION_READINESS_DECISION.md").read_text(encoding="utf-8")
    return SecretVersionsExecutionCheck("Production decision remains NO-GO", "NO-GO_FOR_ACTUAL_DEPLOYMENT" in text)


def no_secret_patterns(paths: list[Path] | None = None) -> SecretVersionsExecutionCheck:
    if paths is None:
        paths = list(DEPLOYMENT_DOCS.glob("*.md")) + list(SCRIPTS_ROOT.glob("*.ps1"))
    findings: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
        if REAL_DATABASE_URL_PATTERN.search(text):
            findings.append(f"{path.name}:real-looking DATABASE_URL")
    return SecretVersionsExecutionCheck("No real-looking secret values in docs/scripts", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> SecretVersionsExecutionCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return SecretVersionsExecutionCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked(project_root: Path = PROJECT_ROOT) -> SecretVersionsExecutionCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return SecretVersionsExecutionCheck(
        ".local-secrets and generated secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks(root: Path = DEPLOYMENT_DOCS) -> list[SecretVersionsExecutionCheck]:
    return [
        secret_version_statuses_documented(root),
        database_url_pending_until_cloud_sql(root),
        decision_remains_no_go(root),
        no_secret_patterns(),
        env_not_tracked(root.parents[1]),
        local_secrets_not_tracked(root.parents[1]),
    ]


def main() -> None:
    checks = run_checks()
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"{status} {check.name}: {check.detail}")
    if any(not check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
