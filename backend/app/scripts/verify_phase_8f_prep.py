from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
DEPLOYMENT_DOCS = PROJECT_ROOT / "docs" / "deployment"

REQUIRED_DOCS = [
    "CLOUD_SQL_COST_APPROVAL_FORM.md",
    "SECRET_PREPARATION_CHECKLIST.md",
    "PHASE_8F_EXECUTION_PLAN.md",
    "PRODUCTION_READINESS_DECISION.md",
    "DEPLOYMENT_VARIABLES.template.md",
    "FINAL_PREFLIGHT_GATE.md",
]

SECRET_PATTERNS = [
    re.compile(r"sk-ant-", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY\s*=\s*sk-", re.IGNORECASE),
]


@dataclass
class PrepCheck:
    name: str
    passed: bool
    detail: str = ""


def required_docs_exist(root: Path = DEPLOYMENT_DOCS) -> list[PrepCheck]:
    return [PrepCheck(f"{doc} exists", (root / doc).exists(), str(root / doc)) for doc in REQUIRED_DOCS]


def cloud_sql_pending_approval(root: Path = DEPLOYMENT_DOCS) -> PrepCheck:
    text = (root / "CLOUD_SQL_COST_APPROVAL_FORM.md").read_text(encoding="utf-8")
    return PrepCheck("Cloud SQL approval remains pending", "PENDING_APPROVAL" in text)


def decision_remains_no_go(root: Path = DEPLOYMENT_DOCS) -> PrepCheck:
    text = (root / "PRODUCTION_READINESS_DECISION.md").read_text(encoding="utf-8")
    return PrepCheck("Production decision remains NO-GO", "NO-GO_FOR_ACTUAL_DEPLOYMENT" in text)


def no_secret_patterns(root: Path = DEPLOYMENT_DOCS) -> PrepCheck:
    findings: list[str] = []
    for path in sorted(root.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return PrepCheck("No real-looking Anthropic secret patterns", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> PrepCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return PrepCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def git_remote_configured(project_root: Path = PROJECT_ROOT) -> PrepCheck:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    remote = result.stdout.strip()
    expected = "https://github.com/rgelikoshvili-stack/alte-ai-crm"
    return PrepCheck("GitHub remote configured", remote == expected, remote or result.stderr.strip())


def variables_ready(root: Path = DEPLOYMENT_DOCS) -> list[PrepCheck]:
    text = (root / "DEPLOYMENT_VARIABLES.template.md").read_text(encoding="utf-8")
    return [
        PrepCheck("PROJECT_ID exists", "project-1e145fd0-c30e-4aac-a34" in text),
        PrepCheck("CORS includes alte.edu.ge", "https://alte.edu.ge" in text),
        PrepCheck("CORS includes join.alte.edu.ge", "https://join.alte.edu.ge" in text),
    ]


def run_checks(root: Path = DEPLOYMENT_DOCS) -> list[PrepCheck]:
    return (
        required_docs_exist(root)
        + [
            cloud_sql_pending_approval(root),
            decision_remains_no_go(root),
            no_secret_patterns(root),
            env_not_tracked(root.parents[1]),
            git_remote_configured(root.parents[1]),
        ]
        + variables_ready(root)
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
