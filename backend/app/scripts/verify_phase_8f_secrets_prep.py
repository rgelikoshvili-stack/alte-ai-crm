from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
DEPLOYMENT_DOCS = PROJECT_ROOT / "docs" / "deployment"
SCRIPTS_ROOT = PROJECT_ROOT / "scripts"

REQUIRED_FILES = [
    DEPLOYMENT_DOCS / "SECRET_VALUES_PREPARATION_WORKSHEET.md",
    DEPLOYMENT_DOCS / "SECRET_MANAGER_APPROVAL_GATE.md",
    DEPLOYMENT_DOCS / "DATABASE_URL_CONSTRUCTION.md",
    SCRIPTS_ROOT / "prepare_secret_values.ps1",
]

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
class SecretsPrepCheck:
    name: str
    passed: bool
    detail: str = ""


def required_files_exist(files: list[Path] | None = None) -> list[SecretsPrepCheck]:
    paths = files or REQUIRED_FILES
    return [SecretsPrepCheck(f"{path.name} exists", path.exists(), str(path)) for path in paths]


def approval_gate_pending(root: Path = DEPLOYMENT_DOCS) -> SecretsPrepCheck:
    text = (root / "SECRET_MANAGER_APPROVAL_GATE.md").read_text(encoding="utf-8")
    return SecretsPrepCheck("Secret Manager approval remains pending", "PENDING_APPROVAL" in text)


def decision_remains_no_go(root: Path = DEPLOYMENT_DOCS) -> SecretsPrepCheck:
    text = (root / "PRODUCTION_READINESS_DECISION.md").read_text(encoding="utf-8")
    return SecretsPrepCheck("Production decision remains NO-GO", "NO-GO_FOR_ACTUAL_DEPLOYMENT" in text)


def no_secret_patterns(paths: list[Path] | None = None) -> SecretsPrepCheck:
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
    return SecretsPrepCheck("No real-looking secret values", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> SecretsPrepCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return SecretsPrepCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def run_checks(root: Path = DEPLOYMENT_DOCS) -> list[SecretsPrepCheck]:
    return (
        required_files_exist()
        + [
            approval_gate_pending(root),
            decision_remains_no_go(root),
            no_secret_patterns(),
            env_not_tracked(root.parents[1]),
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
