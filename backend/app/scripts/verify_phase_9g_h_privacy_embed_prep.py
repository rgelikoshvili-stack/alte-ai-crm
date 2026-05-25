from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

PRIVACY_PACKAGE = PROJECT_ROOT / "docs" / "privacy" / "CHATBOT_PRIVACY_DATA_APPROVAL_PACKAGE.md"
CONSENT_DOC = PROJECT_ROOT / "docs" / "privacy" / "CHATBOT_CONSENT_TEXT_GEO_EN.md"
RETENTION_DOC = PROJECT_ROOT / "docs" / "privacy" / "CHATBOT_DATA_RETENTION_AND_RIGHTS_DRAFT.md"
PRIVACY_CHECKLIST = PROJECT_ROOT / "docs" / "deployment" / "PRIVACY_DATA_FINAL_APPROVAL_CHECKLIST.md"
ASSET_DECISION = PROJECT_ROOT / "docs" / "deployment" / "FINAL_WIDGET_ASSET_URL_DECISION.md"
ALTE_SNIPPET = PROJECT_ROOT / "docs" / "embed_package" / "alte_safe_pro_sidebar_embed_snippet.html"
JOIN_SNIPPET = PROJECT_ROOT / "docs" / "embed_package" / "join_alte_safe_pro_sidebar_embed_snippet.html"
EMBED_README = PROJECT_ROOT / "docs" / "embed_package" / "EMBED_PACKAGE_README_GEO.md"
EMBED_RUNBOOK = PROJECT_ROOT / "docs" / "deployment" / "ACTUAL_SITE_EMBED_RUNBOOK.md"
SMOKE_GUIDE = PROJECT_ROOT / "docs" / "deployment" / "REAL_DOMAIN_BROWSER_SMOKE_EXECUTION_GUIDE.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9G_H_PRIVACY_AND_EMBED_PREP_RESULT.md"
WIDGET = PROJECT_ROOT / "widget" / "alte-university-ai-chatbot-safe-pro.html"

README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
READINESS = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md"
FINAL_PREFLIGHT = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md"
FINAL_GATE = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PRE_EMBED_APPROVAL_GATE.md"
REAL_DOMAIN_PLAN = PROJECT_ROOT / "docs" / "deployment" / "REAL_DOMAIN_WIDGET_SMOKE_PLAN.md"
WIDGET_SNIPPET = PROJECT_ROOT / "docs" / "deployment" / "WIDGET_SAFE_PRO_EMBED_SNIPPET.md"
ANSWER_POLICY = PROJECT_ROOT / "docs" / "deployment" / "CHATBOT_PUBLIC_ANSWER_POLICY.md"
OFFICIAL_REPORT = PROJECT_ROOT / "docs" / "deployment" / "OFFICIAL_CONTENT_REVIEW_REPORT.md"

STATUS = "PHASE_9G_H_STATUS=PRE_EMBED_PRIVACY_AND_ASSET_PACKAGE_READY_PENDING_APPROVALS"
PRIVACY_STATUS = "PRIVACY_DATA_FINAL_APPROVAL_STATUS=PENDING"
ASSET_STATUS = "FINAL_WIDGET_ASSET_URL_STATUS=PENDING_FINAL_URL"
DECISION_STATE = "BACKEND_DEPLOYED_PRIVACY_AND_EMBED_PACKAGE_READY_PENDING_FINAL_APPROVALS"

DOCS = [
    PRIVACY_PACKAGE,
    CONSENT_DOC,
    RETENTION_DOC,
    PRIVACY_CHECKLIST,
    ASSET_DECISION,
    ALTE_SNIPPET,
    JOIN_SNIPPET,
    EMBED_README,
    EMBED_RUNBOOK,
    SMOKE_GUIDE,
    RESULT_DOC,
    README,
    NEXT_PHASES,
    READINESS,
    FINAL_PREFLIGHT,
    FINAL_GATE,
    REAL_DOMAIN_PLAN,
    WIDGET_SNIPPET,
    ANSWER_POLICY,
    OFFICIAL_REPORT,
]

SECRET_PATTERNS = [
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
    re.compile(r"DB_PASSWORD\s*=", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]

WIDGET_FORBIDDEN = [
    re.compile(r"api\.anthropic\.com", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant-", re.IGNORECASE),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def required_files_exist() -> list[Check]:
    files = [
        PRIVACY_PACKAGE,
        CONSENT_DOC,
        RETENTION_DOC,
        PRIVACY_CHECKLIST,
        ASSET_DECISION,
        ALTE_SNIPPET,
        JOIN_SNIPPET,
        EMBED_README,
        EMBED_RUNBOOK,
        SMOKE_GUIDE,
        RESULT_DOC,
    ]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in files]


def statuses_recorded() -> list[Check]:
    result_text = RESULT_DOC.read_text(encoding="utf-8") if RESULT_DOC.exists() else ""
    privacy_text = PRIVACY_CHECKLIST.read_text(encoding="utf-8") if PRIVACY_CHECKLIST.exists() else ""
    asset_text = ASSET_DECISION.read_text(encoding="utf-8") if ASSET_DECISION.exists() else ""
    docs_text = "\n".join(path.read_text(encoding="utf-8") for path in DOCS if path.exists())
    return [
        Check("Phase 9G-H result status recorded", STATUS in result_text),
        Check("Privacy approval remains pending", PRIVACY_STATUS in privacy_text),
        Check("Final asset URL remains pending", ASSET_STATUS in asset_text),
        Check("Phase 9G-H decision state documented", DECISION_STATE in docs_text),
    ]


def actual_embed_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in DOCS if path.exists())
    bad = [
        phrase
        for phrase in ["actual site embed completed", "actual site embed: complete", "actual site embed: completed"]
        if phrase in text
    ]
    return Check("Actual site embed not marked complete", not bad, ", ".join(bad))


def public_launch_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in DOCS if path.exists())
    bad = [
        phrase
        for phrase in ["public launch complete", "full production launch complete", "public launch: complete"]
        if phrase in text
    ]
    return Check("Public launch not marked complete", not bad, ", ".join(bad))


def widget_privacy_and_security() -> Check:
    text = WIDGET.read_text(encoding="utf-8") if WIDGET.exists() else ""
    required = ["#privacy-policy-pending", "privacyNote", "contactBody", "/chat/session/start", "/chat/message"]
    missing = [item for item in required if item not in text]
    forbidden = [pattern.pattern for pattern in WIDGET_FORBIDDEN if pattern.search(text)]
    return Check("Widget has privacy placeholder and no unsafe browser AI/secrets", not missing and not forbidden, f"missing={missing}; forbidden={forbidden}")


def no_forbidden_patterns() -> Check:
    findings: list[str] = []
    for path in [WIDGET, *DOCS]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return Check("No forbidden secret patterns", not findings, ", ".join(findings))


def env_not_tracked() -> Check:
    result = subprocess.run(["git", "ls-files", ".env", "backend/.env"], cwd=PROJECT_ROOT, capture_output=True, text=True)
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked() -> Check:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".local-secrets not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def run_checks() -> list[Check]:
    return [
        *required_files_exist(),
        *statuses_recorded(),
        actual_embed_not_complete(),
        public_launch_not_complete(),
        widget_privacy_and_security(),
        no_forbidden_patterns(),
        env_not_tracked(),
        local_secrets_not_tracked(),
    ]


def main() -> None:
    checks = run_checks()
    for check in checks:
        print(f"{'PASS' if check.passed else 'FAIL'} {check.name}: {check.detail}")
    if any(not check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
