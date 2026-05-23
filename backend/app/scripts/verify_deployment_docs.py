from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


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
]

FORBIDDEN_PATTERNS = [
    re.compile(r"sk-ant-", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY\s*=\s*sk-", re.IGNORECASE),
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://(?!USER:PASSWORD@)[^:\s]+:[^@\s]+@[^/\s]+/[^\s`]+", re.IGNORECASE),
]


@dataclass
class DocCheck:
    name: str
    passed: bool
    detail: str = ""


def required_docs_exist(root: Path = DEPLOYMENT_DOCS) -> list[DocCheck]:
    return [DocCheck(name=f"{doc} exists", passed=(root / doc).exists(), detail=str(root / doc)) for doc in REQUIRED_DOCS]


def scan_for_forbidden_patterns(root: Path = DEPLOYMENT_DOCS) -> list[DocCheck]:
    checks: list[DocCheck] = []
    for path in sorted(root.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        findings: list[str] = []
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                findings.append(pattern.pattern)
        checks.append(DocCheck(name=f"{path.name} forbidden secret scan", passed=not findings, detail=", ".join(findings)))
    return checks


def run_checks(root: Path = DEPLOYMENT_DOCS) -> list[DocCheck]:
    return required_docs_exist(root) + scan_for_forbidden_patterns(root)


def main() -> None:
    checks = run_checks()
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"{status} {check.name}: {check.detail}")
    if any(not check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
