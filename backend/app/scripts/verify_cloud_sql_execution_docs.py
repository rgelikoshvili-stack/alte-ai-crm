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
class CloudSqlExecutionCheck:
    name: str
    passed: bool
    detail: str = ""


def cloud_sql_status_documented(root: Path = DEPLOYMENT_DOCS) -> CloudSqlExecutionCheck:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.md"))
    required = [
        "Corrected approach",
        "Enterprise edition",
        "db-f1-micro",
        "CLOUD_SQL_INSTANCE_CREATED",
        "DATABASE_CREATED",
        "DB_USER_CREATED",
        "VERSION_ADDED",
    ]
    missing = [item for item in required if item not in combined]
    return CloudSqlExecutionCheck("Cloud SQL execution status documented", not missing, ", ".join(missing))


def no_enterprise_plus_selected(root: Path = DEPLOYMENT_DOCS) -> CloudSqlExecutionCheck:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.md"))
    forbidden_selected = [
        "selected Enterprise Plus",
        "db-perf-optimized",
        "performance-optimized tier selected",
    ]
    findings = [item for item in forbidden_selected if item.lower() in combined.lower()]
    return CloudSqlExecutionCheck("No Enterprise Plus expensive tier selected", not findings, ", ".join(findings))


def decision_remains_no_go(root: Path = DEPLOYMENT_DOCS) -> CloudSqlExecutionCheck:
    text = (root / "PRODUCTION_READINESS_DECISION.md").read_text(encoding="utf-8")
    return CloudSqlExecutionCheck("Production decision remains NO-GO", "NO-GO_FOR_ACTUAL_DEPLOYMENT" in text)


def no_secret_patterns(paths: list[Path] | None = None) -> CloudSqlExecutionCheck:
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
    return CloudSqlExecutionCheck("No real-looking secrets in docs/scripts", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> CloudSqlExecutionCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return CloudSqlExecutionCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked(project_root: Path = PROJECT_ROOT) -> CloudSqlExecutionCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return CloudSqlExecutionCheck(
        ".local-secrets and generated secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks(root: Path = DEPLOYMENT_DOCS) -> list[CloudSqlExecutionCheck]:
    return [
        cloud_sql_status_documented(root),
        no_enterprise_plus_selected(root),
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
