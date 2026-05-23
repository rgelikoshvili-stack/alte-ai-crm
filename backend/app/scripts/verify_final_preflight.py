from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from app.scripts.verify_deployment_docs import FORBIDDEN_PATTERNS


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
DEPLOYMENT_DOCS = PROJECT_ROOT / "docs" / "deployment"

REQUIRED_DOCS = [
    "CLOUD_RUN_DEPLOYMENT.md",
    "CLOUD_SQL_POSTGRES.md",
    "SECRET_MANAGER.md",
    "CORS_AND_WIDGET_ORIGINS.md",
    "DEPLOYMENT_CHECKLIST.md",
    "DEPLOYMENT_VARIABLES.template.md",
    "GOOGLE_CLOUD_PREFLIGHT.md",
    "COMMAND_PLAN_GCLOUD.md",
    "DEPLOYMENT_RISK_REGISTER.md",
    "PRODUCTION_READINESS_DECISION.md",
    "GITHUB_BACKUP_AND_RELEASE.md",
    "FINAL_PREFLIGHT_GATE.md",
]


@dataclass
class PreflightCheck:
    name: str
    passed: bool
    detail: str = ""


def read_doc(name: str, root: Path = DEPLOYMENT_DOCS) -> str:
    return (root / name).read_text(encoding="utf-8")


def required_docs_exist(root: Path = DEPLOYMENT_DOCS) -> list[PreflightCheck]:
    return [PreflightCheck(f"{name} exists", (root / name).exists(), str(root / name)) for name in REQUIRED_DOCS]


def content_checks(root: Path = DEPLOYMENT_DOCS) -> list[PreflightCheck]:
    variables = read_doc("DEPLOYMENT_VARIABLES.template.md", root)
    decision = read_doc("PRODUCTION_READINESS_DECISION.md", root)
    combined = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.md"))
    forbidden = [pattern.pattern for pattern in FORBIDDEN_PATTERNS if pattern.search(combined)]
    return [
        PreflightCheck("PROJECT_ID is filled", "TODO_GCP_PROJECT_ID" not in variables and "project-1e145fd0-c30e-4aac-a34" in variables),
        PreflightCheck("GITHUB_REMOTE_URL exists", "https://github.com/rgelikoshvili-stack/alte-ai-crm" in variables),
        PreflightCheck("CORS includes alte.edu.ge", "https://alte.edu.ge" in variables),
        PreflightCheck("CORS includes join.alte.edu.ge", "https://join.alte.edu.ge" in variables),
        PreflightCheck("Decision remains NO-GO", "NO-GO_FOR_ACTUAL_DEPLOYMENT" in decision),
        PreflightCheck("No forbidden secret patterns", not forbidden, ", ".join(forbidden)),
    ]


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> PreflightCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return PreflightCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def run_checks(root: Path = DEPLOYMENT_DOCS) -> list[PreflightCheck]:
    return required_docs_exist(root) + content_checks(root) + [env_not_tracked(root.parents[1])]


def main() -> None:
    checks = run_checks()
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"{status} {check.name}: {check.detail}")
    if any(not check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
