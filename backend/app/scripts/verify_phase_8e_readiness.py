from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
DEPLOYMENT_DOCS = PROJECT_ROOT / "docs" / "deployment"

REQUIRED_DOCS = [
    "CLOUD_SQL_TIER_DECISION.md",
    "SECRET_VALUES_RUNBOOK.md",
    "PRODUCTION_ENV_MAPPING.md",
    "PRODUCTION_MIGRATION_AND_SEED.md",
    "WEBSITE_AND_PRIVACY_APPROVAL.md",
    "PRODUCTION_READINESS_DECISION.md",
    "DEPLOYMENT_VARIABLES.template.md",
    "FINAL_PREFLIGHT_GATE.md",
    "GITHUB_BACKUP_AND_RELEASE.md",
]

SECRET_PATTERNS = [
    re.compile(r"sk-ant-", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY\s*=\s*sk-", re.IGNORECASE),
]


@dataclass
class ReadinessCheck:
    name: str
    passed: bool
    detail: str = ""


def required_docs_exist(root: Path = DEPLOYMENT_DOCS) -> list[ReadinessCheck]:
    return [ReadinessCheck(f"{doc} exists", (root / doc).exists(), str(root / doc)) for doc in REQUIRED_DOCS]


def scan_secret_patterns(root: Path = DEPLOYMENT_DOCS) -> ReadinessCheck:
    findings: list[str] = []
    for path in sorted(root.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return ReadinessCheck("No real-looking Anthropic secret patterns", not findings, ", ".join(findings))


def decision_remains_no_go(root: Path = DEPLOYMENT_DOCS) -> ReadinessCheck:
    text = (root / "PRODUCTION_READINESS_DECISION.md").read_text(encoding="utf-8")
    return ReadinessCheck("Decision remains NO-GO", "NO-GO_FOR_ACTUAL_DEPLOYMENT" in text)


def variables_include_project_id(root: Path = DEPLOYMENT_DOCS) -> ReadinessCheck:
    text = (root / "DEPLOYMENT_VARIABLES.template.md").read_text(encoding="utf-8")
    return ReadinessCheck("Deployment variables include PROJECT_ID", "project-1e145fd0-c30e-4aac-a34" in text)


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> ReadinessCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return ReadinessCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def run_checks(root: Path = DEPLOYMENT_DOCS) -> list[ReadinessCheck]:
    return (
        required_docs_exist(root)
        + [
            decision_remains_no_go(root),
            variables_include_project_id(root),
            scan_secret_patterns(root),
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
