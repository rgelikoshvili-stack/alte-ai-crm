from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
WIDGET_ROOT = PROJECT_ROOT / "widget"
DEPLOYMENT_DOCS = PROJECT_ROOT / "docs" / "deployment"
README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
DECISION_STATE = "BACKEND_DEPLOYED_STANDALONE_WIDGET_READY_PENDING_SITE_EMBED"

SECRET_PATTERNS = [
    re.compile(r"sk-ant-", re.IGNORECASE),
    re.compile(r"DATABASE_URL", re.IGNORECASE),
    re.compile(r"DB_PASSWORD", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]


@dataclass
class StandaloneWidgetCheck:
    name: str
    passed: bool
    detail: str = ""


REQUIRED_FILES = [
    WIDGET_ROOT / "standalone-production-demo.html",
    WIDGET_ROOT / "STANDALONE_PRODUCTION_DEMO.md",
    DEPLOYMENT_DOCS / "WIDGET_TRANSFER_TO_ALTE_SITE.md",
    DEPLOYMENT_DOCS / "STANDALONE_WIDGET_SMOKE_CHECKLIST.md",
]


def required_files_exist() -> list[StandaloneWidgetCheck]:
    return [StandaloneWidgetCheck(f"{path.name} exists", path.exists(), str(path)) for path in REQUIRED_FILES]


def _read(paths: list[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


def standalone_demo_content_valid() -> StandaloneWidgetCheck:
    text = (WIDGET_ROOT / "standalone-production-demo.html").read_text(encoding="utf-8")
    required = [
        BACKEND_URL,
        "./alte-chat-widget.v0.8.js",
        "alte.edu.ge",
        "join.alte.edu.ge",
        "საკონტაქტო მონაცემებს ვიყენებთ მხოლოდ კონსულტაციისთვის.",
        "We use your contact details only to provide consultation.",
    ]
    missing = [item for item in required if item not in text]
    return StandaloneWidgetCheck("Standalone demo content is valid", not missing, ", ".join(missing))


def transfer_package_documented() -> StandaloneWidgetCheck:
    text = _read(
        [
            DEPLOYMENT_DOCS / "WIDGET_TRANSFER_TO_ALTE_SITE.md",
            DEPLOYMENT_DOCS / "STANDALONE_WIDGET_SMOKE_CHECKLIST.md",
            WIDGET_ROOT / "STANDALONE_PRODUCTION_DEMO.md",
        ]
    )
    required = [
        BACKEND_URL,
        "alte-chat-widget.v0.8.js",
        "sourceDomain: \"alte.edu.ge\"",
        "sourceDomain: \"join.alte.edu.ge\"",
        "remove both script tags",
    ]
    normalized = text.lower()
    missing = [item for item in required if item.lower() not in normalized]
    return StandaloneWidgetCheck("Transfer package documented", not missing, ", ".join(missing))


def decision_state_documented() -> StandaloneWidgetCheck:
    text = _read(
        [
            DEPLOYMENT_DOCS / "PRODUCTION_READINESS_DECISION.md",
            DEPLOYMENT_DOCS / "FINAL_PREFLIGHT_GATE.md",
            README,
            NEXT_PHASES,
            WIDGET_ROOT / "STANDALONE_PRODUCTION_DEMO.md",
        ]
    )
    forbidden = [
        "FULL_PRODUCTION_LAUNCH_COMPLETE",
        "WEBSITE_WIDGET_EMBED_COMPLETED",
        "WEBSITE_PRIVACY_APPROVED_FOR_WIDGET_EMBED",
    ]
    findings = [item for item in forbidden if item in text]
    return StandaloneWidgetCheck(
        "Decision state remains pending actual site embed",
        DECISION_STATE in text and not findings,
        ", ".join(findings),
    )


def no_forbidden_patterns(paths: list[Path] | None = None) -> StandaloneWidgetCheck:
    if paths is None:
        paths = REQUIRED_FILES + [
            DEPLOYMENT_DOCS / "WEBSITE_WIDGET_PRODUCTION_EMBED.md",
            DEPLOYMENT_DOCS / "WEBSITE_DEVELOPER_HANDOFF.md",
            DEPLOYMENT_DOCS / "PRODUCTION_WIDGET_SMOKE_CHECKLIST.md",
            WIDGET_ROOT / "README.md",
        ]
    findings: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return StandaloneWidgetCheck("No forbidden secret patterns", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> StandaloneWidgetCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return StandaloneWidgetCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked(project_root: Path = PROJECT_ROOT) -> StandaloneWidgetCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return StandaloneWidgetCheck(
        ".local-secrets and generated secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks() -> list[StandaloneWidgetCheck]:
    return [
        *required_files_exist(),
        standalone_demo_content_valid(),
        transfer_package_documented(),
        decision_state_documented(),
        no_forbidden_patterns(),
        env_not_tracked(),
        local_secrets_not_tracked(),
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
