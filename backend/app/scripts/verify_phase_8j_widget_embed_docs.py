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
class Phase8JCheck:
    name: str
    passed: bool
    detail: str = ""


def required_files_exist() -> list[Phase8JCheck]:
    paths = [
        DEPLOYMENT_DOCS / "WEBSITE_WIDGET_PRODUCTION_EMBED.md",
        DEPLOYMENT_DOCS / "PRODUCTION_WIDGET_SMOKE_CHECKLIST.md",
        WIDGET_ROOT / "production-config.alte.example.js",
        WIDGET_ROOT / "production-config.join.example.js",
    ]
    return [Phase8JCheck(f"{path.name} exists", path.exists(), str(path)) for path in paths]


def _read(paths: list[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


def embed_docs_record_backend_and_domains() -> Phase8JCheck:
    text = _read(
        [
            DEPLOYMENT_DOCS / "WEBSITE_WIDGET_PRODUCTION_EMBED.md",
            WIDGET_ROOT / "production-config.alte.example.js",
            WIDGET_ROOT / "production-config.join.example.js",
        ]
    )
    required = [
        "https://alte-ai-crm-backend-226875230147.europe-west1.run.app",
        'sourceDomain: "alte.edu.ge"',
        'sourceDomain: "join.alte.edu.ge"',
        'defaultLanguage: "ka"',
        'defaultLanguage: "en"',
        "YOUR_WIDGET_ASSET_URL",
    ]
    missing = [item for item in required if item not in text]
    return Phase8JCheck("Production widget backend/domains documented", not missing, ", ".join(missing))


def smoke_and_rollback_documented() -> Phase8JCheck:
    text = _read(
        [
            DEPLOYMENT_DOCS / "WEBSITE_WIDGET_PRODUCTION_EMBED.md",
            DEPLOYMENT_DOCS / "PRODUCTION_WIDGET_SMOKE_CHECKLIST.md",
        ]
    )
    normalized = text.lower()
    required = [
        "rollback",
        "smoke test checklist",
        "remove both script tags",
        "privacy/data approval",
        "production widget smoke",
    ]
    missing = [item for item in required if item not in normalized]
    return Phase8JCheck("Widget smoke and rollback documented", not missing, ", ".join(missing))


def website_privacy_pending() -> Phase8JCheck:
    text = _read(
        [
            DEPLOYMENT_DOCS / "WEBSITE_WIDGET_PRODUCTION_EMBED.md",
            DEPLOYMENT_DOCS / "PRODUCTION_WIDGET_SMOKE_CHECKLIST.md",
            DEPLOYMENT_DOCS / "FINAL_PREFLIGHT_GATE.md",
            DEPLOYMENT_DOCS / "PRODUCTION_READINESS_DECISION.md",
        ]
    )
    required = [
        "Website admin/developer access pending",
        "Privacy/data approval pending",
        "Actual website widget embed pending",
    ]
    missing = [item for item in required if item not in text]
    return Phase8JCheck("Website/privacy blockers remain pending", not missing, ", ".join(missing))


def no_secret_patterns(paths: list[Path] | None = None) -> Phase8JCheck:
    if paths is None:
        paths = list(DEPLOYMENT_DOCS.glob("*.md")) + list(WIDGET_ROOT.glob("*.js")) + [README, NEXT_PHASES]
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
    return Phase8JCheck("No real-looking secrets in docs/widget examples", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> Phase8JCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Phase8JCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked(project_root: Path = PROJECT_ROOT) -> Phase8JCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Phase8JCheck(
        ".local-secrets and generated secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks() -> list[Phase8JCheck]:
    return [
        *required_files_exist(),
        embed_docs_record_backend_and_domains(),
        smoke_and_rollback_documented(),
        website_privacy_pending(),
        no_secret_patterns(),
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
