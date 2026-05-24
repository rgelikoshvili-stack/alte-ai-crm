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
class CloudRunDeploymentCheck:
    name: str
    passed: bool
    detail: str = ""


def _combined_docs(root: Path = DEPLOYMENT_DOCS) -> str:
    paths = list(root.glob("*.md")) + [README, NEXT_PHASES]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


def cloud_run_deployment_documented(root: Path = DEPLOYMENT_DOCS) -> CloudRunDeploymentCheck:
    combined = _combined_docs(root)
    required = [
        "CLOUD_RUN_DEPLOYED",
        "alte-ai-crm-backend",
        "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
        "v0.8-cloud-run",
        "CLOUD_SQL_ATTACHED",
        "SECRET_MANAGER_MAPPED",
        "BACKEND_DEPLOYED_PENDING_WEBSITE_PRIVACY",
    ]
    missing = [item for item in required if item not in combined]
    return CloudRunDeploymentCheck("Cloud Run deployment status documented", not missing, ", ".join(missing))


def endpoint_results_documented(root: Path = DEPLOYMENT_DOCS) -> CloudRunDeploymentCheck:
    combined = _combined_docs(root)
    required = [
        "/health: 200",
        "/version: 200",
        "/diagnostics/ai: 200",
        "/diagnostics/local-demo: 200",
        "/dashboard/overview: 401",
    ]
    missing = [item for item in required if item not in combined]
    return CloudRunDeploymentCheck("Cloud Run endpoint checks documented", not missing, ", ".join(missing))


def website_privacy_pending(root: Path = DEPLOYMENT_DOCS) -> CloudRunDeploymentCheck:
    combined = _combined_docs(root)
    required = [
        "Website admin/developer access pending",
        "Privacy/data approval pending",
        "Actual website widget embed pending",
    ]
    missing = [item for item in required if item not in combined]
    return CloudRunDeploymentCheck("Website/privacy launch blockers remain pending", not missing, ", ".join(missing))


def no_secret_patterns(paths: list[Path] | None = None) -> CloudRunDeploymentCheck:
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
    return CloudRunDeploymentCheck("No real-looking secrets in docs", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> CloudRunDeploymentCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return CloudRunDeploymentCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked(project_root: Path = PROJECT_ROOT) -> CloudRunDeploymentCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return CloudRunDeploymentCheck(
        ".local-secrets and generated secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks(root: Path = DEPLOYMENT_DOCS) -> list[CloudRunDeploymentCheck]:
    project_root = root.parents[1]
    return [
        cloud_run_deployment_documented(root),
        endpoint_results_documented(root),
        website_privacy_pending(root),
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
