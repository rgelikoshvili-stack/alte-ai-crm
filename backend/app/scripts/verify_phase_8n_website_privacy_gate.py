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
WIDGET_README = PROJECT_ROOT / "widget" / "README.md"

DECISION_STATE = "BACKEND_DEPLOYED_WIDGET_READY_PENDING_WEBSITE_PRIVACY_APPROVAL"
REQUIRED_APPROVAL_PHRASE = "Approve Phase 8O-Execution for actual website widget embed"
NO_GO_STATE = "NO-GO_FOR_ACTUAL_SITE_EMBED"

KA_CONSENT = "საკონტაქტო მონაცემებს ვიყენებთ მხოლოდ კონსულტაციისთვის."
EN_CONSENT = "We use your contact details only to provide consultation."

SECRET_PATTERNS = [
    re.compile(r"sk-ant-", re.IGNORECASE),
    re.compile(r"DATABASE_URL", re.IGNORECASE),
    re.compile(r"DB_PASSWORD", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]


@dataclass
class WebsitePrivacyGateCheck:
    name: str
    passed: bool
    detail: str = ""


REQUIRED_FILES = [
    DEPLOYMENT_DOCS / "WEBSITE_EMBED_APPROVAL_GATE.md",
    DEPLOYMENT_DOCS / "PRIVACY_CONSENT_APPROVAL.md",
    DEPLOYMENT_DOCS / "FINAL_WIDGET_EMBED_GO_NO_GO.md",
    DEPLOYMENT_DOCS / "WIDGET_FINAL_ASSET_URL_DECISION.md",
]

SECRET_SCAN_FILES = REQUIRED_FILES + [
    DEPLOYMENT_DOCS / "WEBSITE_AND_PRIVACY_APPROVAL.md",
]


def _read(paths: list[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


def required_files_exist() -> list[WebsitePrivacyGateCheck]:
    return [WebsitePrivacyGateCheck(f"{path.name} exists", path.exists(), str(path)) for path in REQUIRED_FILES]


def approval_statuses_pending() -> WebsitePrivacyGateCheck:
    text = _read(REQUIRED_FILES + [DEPLOYMENT_DOCS / "WEBSITE_AND_PRIVACY_APPROVAL.md"])
    required = [
        "Website access status: PENDING",
        "Privacy approval status: PENDING",
        "Final widget asset URL: PENDING",
        "Actual site embed: BLOCKED",
        "Real-domain smoke: PENDING",
    ]
    missing = [item for item in required if item not in text]
    return WebsitePrivacyGateCheck("Approval statuses remain pending/blocked", not missing, ", ".join(missing))


def no_go_documented() -> WebsitePrivacyGateCheck:
    text = (DEPLOYMENT_DOCS / "FINAL_WIDGET_EMBED_GO_NO_GO.md").read_text(encoding="utf-8")
    return WebsitePrivacyGateCheck("Actual site embed remains NO-GO", NO_GO_STATE in text)


def decision_state_documented() -> WebsitePrivacyGateCheck:
    text = _read(
        [
            DEPLOYMENT_DOCS / "PRODUCTION_READINESS_DECISION.md",
            DEPLOYMENT_DOCS / "FINAL_PREFLIGHT_GATE.md",
            README,
            NEXT_PHASES,
            WIDGET_README,
        ]
    )
    forbidden = [
        "FULL_PRODUCTION_LAUNCH_COMPLETE",
        "WEBSITE_WIDGET_EMBED_COMPLETED",
        "WEBSITE_PRIVACY_APPROVED_FOR_WIDGET_EMBED",
    ]
    findings = [item for item in forbidden if item in text]
    return WebsitePrivacyGateCheck(
        "Decision state remains pending website/privacy approval",
        DECISION_STATE in text and not findings,
        ", ".join(findings),
    )


def consent_text_documented() -> WebsitePrivacyGateCheck:
    text = (DEPLOYMENT_DOCS / "PRIVACY_CONSENT_APPROVAL.md").read_text(encoding="utf-8")
    missing = [item for item in [KA_CONSENT, EN_CONSENT] if item not in text]
    return WebsitePrivacyGateCheck("KA/EN consent text documented", not missing, ", ".join(missing))


def required_phrase_documented() -> WebsitePrivacyGateCheck:
    text = (DEPLOYMENT_DOCS / "WEBSITE_EMBED_APPROVAL_GATE.md").read_text(encoding="utf-8")
    return WebsitePrivacyGateCheck("Required approval phrase documented", REQUIRED_APPROVAL_PHRASE in text)


def no_forbidden_patterns(paths: list[Path] | None = None) -> WebsitePrivacyGateCheck:
    paths = paths or SECRET_SCAN_FILES
    findings: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return WebsitePrivacyGateCheck("No forbidden secret patterns", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> WebsitePrivacyGateCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return WebsitePrivacyGateCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked(project_root: Path = PROJECT_ROOT) -> WebsitePrivacyGateCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return WebsitePrivacyGateCheck(
        ".local-secrets and generated secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks() -> list[WebsitePrivacyGateCheck]:
    return [
        *required_files_exist(),
        approval_statuses_pending(),
        no_go_documented(),
        decision_state_documented(),
        consent_text_documented(),
        required_phrase_documented(),
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
