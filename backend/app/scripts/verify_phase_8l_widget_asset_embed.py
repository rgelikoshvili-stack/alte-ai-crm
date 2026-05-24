from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
DEPLOYMENT_DOCS = PROJECT_ROOT / "docs" / "deployment"
WIDGET_ROOT = PROJECT_ROOT / "widget"
README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"

SECRET_PATTERNS = [
    re.compile(r"sk-ant-", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY\s*=\s*sk-", re.IGNORECASE),
    re.compile(r"DATABASE_URL", re.IGNORECASE),
    re.compile(r"DB_PASSWORD", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]


@dataclass
class Phase8LCheck:
    name: str
    passed: bool
    detail: str = ""


REQUIRED_FILES = [
    WIDGET_ROOT / "alte-chat-widget.v0.8.js",
    WIDGET_ROOT / "production-embed-test.html",
    DEPLOYMENT_DOCS / "WIDGET_EMBED_SNIPPETS_FINAL.md",
    DEPLOYMENT_DOCS / "WEBSITE_DEVELOPER_HANDOFF.md",
    DEPLOYMENT_DOCS / "WIDGET_ASSET_HOSTING_DECISION.md",
]


def required_files_exist() -> list[Phase8LCheck]:
    return [Phase8LCheck(f"{path.name} exists", path.exists(), str(path)) for path in REQUIRED_FILES]


def _read(paths: list[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


def production_backend_url_present() -> Phase8LCheck:
    text = _read(REQUIRED_FILES + [README, NEXT_PHASES])
    return Phase8LCheck("Production backend URL present", BACKEND_URL in text)


def snippets_have_correct_domains() -> Phase8LCheck:
    text = (DEPLOYMENT_DOCS / "WIDGET_EMBED_SNIPPETS_FINAL.md").read_text(encoding="utf-8")
    required = [
        'sourceDomain: "alte.edu.ge"',
        'defaultLanguage: "ka"',
        'sourceDomain: "join.alte.edu.ge"',
        'defaultLanguage: "en"',
    ]
    missing = [item for item in required if item not in text]
    return Phase8LCheck("Final snippets have correct source domains and languages", not missing, ", ".join(missing))


def actual_embed_blocked_unless_approved() -> Phase8LCheck:
    text = _read(
        [
            DEPLOYMENT_DOCS / "WEBSITE_AND_PRIVACY_APPROVAL.md",
            DEPLOYMENT_DOCS / "FINAL_PREFLIGHT_GATE.md",
            DEPLOYMENT_DOCS / "PRODUCTION_READINESS_DECISION.md",
            DEPLOYMENT_DOCS / "WIDGET_EMBED_SNIPPETS_FINAL.md",
            README,
            NEXT_PHASES,
        ]
    )
    required = [
        "ACTUAL_EMBED_BLOCKED_PENDING_WEBSITE_PRIVACY_APPROVAL",
        "Website admin/developer access pending",
        "Privacy/data approval pending",
    ]
    missing = [item for item in required if item not in text]
    full_launch_claims = [
        "FULL_PRODUCTION_LAUNCH_COMPLETE",
        "WEBSITE_WIDGET_EMBED_COMPLETED",
        "WEBSITE_PRIVACY_APPROVED_FOR_WIDGET_EMBED",
    ]
    forbidden = [item for item in full_launch_claims if item in text]
    return Phase8LCheck(
        "Actual embed remains blocked unless approvals are recorded",
        not missing and not forbidden,
        ", ".join(missing + forbidden),
    )


def no_forbidden_patterns(paths: list[Path] | None = None) -> Phase8LCheck:
    if paths is None:
        paths = (
            REQUIRED_FILES
            + [
                DEPLOYMENT_DOCS / "PRODUCTION_WIDGET_SMOKE_CHECKLIST.md",
                DEPLOYMENT_DOCS / "WEBSITE_WIDGET_PRODUCTION_EMBED.md",
                WIDGET_ROOT / "production-config.alte.example.js",
                WIDGET_ROOT / "production-config.join.example.js",
            ]
        )
    findings: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return Phase8LCheck("No forbidden secret patterns in widget/docs", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> Phase8LCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Phase8LCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked(project_root: Path = PROJECT_ROOT) -> Phase8LCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Phase8LCheck(
        ".local-secrets and generated secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks() -> list[Phase8LCheck]:
    return [
        *required_files_exist(),
        production_backend_url_present(),
        snippets_have_correct_domains(),
        actual_embed_blocked_unless_approved(),
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
