from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
DEPLOYMENT_DOCS = PROJECT_ROOT / "docs" / "deployment"
README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"

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
class Phase8HCheck:
    name: str
    passed: bool
    detail: str = ""


def _read_all_docs(root: Path = DEPLOYMENT_DOCS) -> str:
    paths = list(root.glob("*.md")) + [README, NEXT_PHASES]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


def migration_seed_status_documented(root: Path = DEPLOYMENT_DOCS) -> Phase8HCheck:
    combined = _read_all_docs(root)
    required = [
        "Alembic version table width correction",
        "VARCHAR(128)",
        "MIGRATIONS_COMPLETED",
        "006_phase_7b_knowledge_governance",
        "PRODUCTION_SAFE_BOOTSTRAP_COMPLETED",
        "KNOWLEDGE_SEED_COMPLETED",
        "PRODUCTION_DB_SEED_VERIFIED",
    ]
    missing = [item for item in required if item not in combined]
    return Phase8HCheck("Phase 8H migration and seed status documented", not missing, ", ".join(missing))


def decision_remains_no_go(root: Path = DEPLOYMENT_DOCS) -> Phase8HCheck:
    text = (root / "PRODUCTION_READINESS_DECISION.md").read_text(encoding="utf-8")
    return Phase8HCheck("Production decision remains NO-GO", "NO-GO_FOR_ACTUAL_DEPLOYMENT" in text)


def no_secret_patterns(paths: list[Path] | None = None) -> Phase8HCheck:
    if paths is None:
        paths = list(DEPLOYMENT_DOCS.glob("*.md")) + [README, NEXT_PHASES]
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
    return Phase8HCheck("No real-looking secrets in docs", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> Phase8HCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Phase8HCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked(project_root: Path = PROJECT_ROOT) -> Phase8HCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Phase8HCheck(
        ".local-secrets and generated secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks(root: Path = DEPLOYMENT_DOCS) -> list[Phase8HCheck]:
    project_root = root.parents[1]
    return [
        migration_seed_status_documented(root),
        decision_remains_no_go(root),
        no_secret_patterns(),
        env_not_tracked(project_root),
        local_secrets_not_tracked(project_root),
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
