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
class SecretManagerExecutionCheck:
    name: str
    passed: bool
    detail: str = ""


def secret_manager_execution_recorded(root: Path = DEPLOYMENT_DOCS) -> SecretManagerExecutionCheck:
    text = (root / "SECRET_MANAGER_APPROVAL_GATE.md").read_text(encoding="utf-8")
    required = [
        "SECRET_MANAGER_EXECUTION_CONTAINERS_CREATED",
        "alte-db-password: CONTAINER_CREATED / VERSION_ADDED",
        "alte-jwt-secret: CONTAINER_CREATED / VERSION_ADDED",
        "alte-anthropic-api-key: CONTAINER_CREATED / VERSION_ADDED",
        "alte-database-url: CONTAINER_CREATED / VERSION_ADDED",
    ]
    missing = [item for item in required if item not in text]
    return SecretManagerExecutionCheck("Secret Manager execution status recorded", not missing, ", ".join(missing))


def decision_remains_no_go(root: Path = DEPLOYMENT_DOCS) -> SecretManagerExecutionCheck:
    text = (root / "PRODUCTION_READINESS_DECISION.md").read_text(encoding="utf-8")
    return SecretManagerExecutionCheck("Production decision remains NO-GO", "NO-GO_FOR_ACTUAL_DEPLOYMENT" in text)


def database_url_version_added(root: Path = DEPLOYMENT_DOCS) -> SecretManagerExecutionCheck:
    combined = "\n".join(
        [
            (root / "SECRET_MANAGER_APPROVAL_GATE.md").read_text(encoding="utf-8"),
            (root / "SECRET_PREPARATION_CHECKLIST.md").read_text(encoding="utf-8"),
            (root / "FINAL_PREFLIGHT_GATE.md").read_text(encoding="utf-8"),
        ]
    )
    return SecretManagerExecutionCheck(
        "DATABASE_URL version added",
        "alte-database-url: CONTAINER_CREATED / VERSION_ADDED" in combined
        or "Secret Manager status: `CONTAINER_CREATED / VERSION_ADDED`" in combined,
    )


def no_secret_patterns(paths: list[Path] | None = None) -> SecretManagerExecutionCheck:
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
    return SecretManagerExecutionCheck("No real-looking secret values in docs/scripts", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> SecretManagerExecutionCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return SecretManagerExecutionCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked(project_root: Path = PROJECT_ROOT) -> SecretManagerExecutionCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return SecretManagerExecutionCheck(
        ".local-secrets and local secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks(root: Path = DEPLOYMENT_DOCS) -> list[SecretManagerExecutionCheck]:
    return [
        secret_manager_execution_recorded(root),
        decision_remains_no_go(root),
        database_url_version_added(root),
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
