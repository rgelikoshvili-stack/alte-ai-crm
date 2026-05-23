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
class LocalSecretPrepCheck:
    name: str
    passed: bool
    detail: str = ""


def gitignore_includes_local_secret_patterns(project_root: Path = PROJECT_ROOT) -> LocalSecretPrepCheck:
    text = (project_root / ".gitignore").read_text(encoding="utf-8")
    required = [
        ".local-secrets/",
        "*.secret",
        "*.secrets",
        "production-secrets.local.*",
        "secret-values.local.*",
    ]
    missing = [item for item in required if item not in text]
    return LocalSecretPrepCheck(".gitignore excludes local secret files", not missing, ", ".join(missing))


def required_files_exist(project_root: Path = PROJECT_ROOT) -> list[LocalSecretPrepCheck]:
    paths = [
        DEPLOYMENT_DOCS / "LOCAL_SECRET_VALUES_PREP.md",
        SCRIPTS_ROOT / "prepare_local_secret_values.ps1",
    ]
    return [LocalSecretPrepCheck(f"{path.name} exists", path.exists(), str(path)) for path in paths]


def approval_gate_recorded(root: Path = DEPLOYMENT_DOCS) -> LocalSecretPrepCheck:
    text = (root / "SECRET_MANAGER_APPROVAL_GATE.md").read_text(encoding="utf-8")
    return LocalSecretPrepCheck(
        "Secret Manager gate approved for next execution",
        "APPROVED_FOR_NEXT_EXECUTION" in text,
    )


def decision_remains_no_go(root: Path = DEPLOYMENT_DOCS) -> LocalSecretPrepCheck:
    text = (root / "PRODUCTION_READINESS_DECISION.md").read_text(encoding="utf-8")
    return LocalSecretPrepCheck("Production decision remains NO-GO", "NO-GO_FOR_ACTUAL_DEPLOYMENT" in text)


def no_secret_patterns(paths: list[Path] | None = None) -> LocalSecretPrepCheck:
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
    return LocalSecretPrepCheck("No real-looking secrets in docs/scripts", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> LocalSecretPrepCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return LocalSecretPrepCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secret_file_not_tracked(project_root: Path = PROJECT_ROOT) -> LocalSecretPrepCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return LocalSecretPrepCheck(
        "Local generated secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks(project_root: Path = PROJECT_ROOT) -> list[LocalSecretPrepCheck]:
    return (
        [
            gitignore_includes_local_secret_patterns(project_root),
        ]
        + required_files_exist(project_root)
        + [
            approval_gate_recorded(DEPLOYMENT_DOCS),
            decision_remains_no_go(DEPLOYMENT_DOCS),
            no_secret_patterns(),
            env_not_tracked(project_root),
            local_secret_file_not_tracked(project_root),
        ]
    )


def main() -> None:
    checks = run_checks()
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"{status} {check.name}: {check.detail}")
    if any(not check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
