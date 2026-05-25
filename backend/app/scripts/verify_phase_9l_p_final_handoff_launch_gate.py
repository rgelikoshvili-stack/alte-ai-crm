from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

APPROVAL_RECORD = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9L_FINAL_APPROVAL_AND_ACCESS_RECORD.md"
HANDOFF_PACKAGE = PROJECT_ROOT / "docs" / "final_handoff" / "FINAL_WEBSITE_HANDOFF_PACKAGE_GEO.md"
ALTE_SNIPPET = PROJECT_ROOT / "docs" / "final_handoff" / "alte_final_embed_snippet.html"
JOIN_SNIPPET = PROJECT_ROOT / "docs" / "final_handoff" / "join_alte_final_embed_snippet.html"
ASSET_MANIFEST = PROJECT_ROOT / "docs" / "final_handoff" / "WIDGET_ASSET_MANIFEST.md"
ASSET_HANDOFF_RESULT = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9M_FINAL_ASSET_HANDOFF_RESULT.md"
SITE_EMBED_DECISION = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_ACTUAL_SITE_EMBED_DECISION.md"
SITE_EMBED_CHECKLIST = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_ACTUAL_SITE_EMBED_CHECKLIST.md"
SMOKE_RESULT = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9O_REAL_DOMAIN_SMOKE_RESULT.md"
PUBLIC_LAUNCH_DECISION = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"

README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
READINESS = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md"
FINAL_PREFLIGHT = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md"
FINAL_PRE_EMBED = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PRE_EMBED_APPROVAL_GATE.md"
ASSET_DECISION = PROJECT_ROOT / "docs" / "deployment" / "FINAL_WIDGET_ASSET_URL_DECISION.md"
RUNBOOK = PROJECT_ROOT / "docs" / "deployment" / "ACTUAL_SITE_EMBED_RUNBOOK.md"
SMOKE_GUIDE = PROJECT_ROOT / "docs" / "deployment" / "REAL_DOMAIN_BROWSER_SMOKE_EXECUTION_GUIDE.md"
ANSWER_POLICY = PROJECT_ROOT / "docs" / "deployment" / "CHATBOT_PUBLIC_ANSWER_POLICY.md"
SITE_RECORD = PROJECT_ROOT / "docs" / "deployment" / "SITE_EMBED_FINAL_APPROVAL_RECORD.md"
SITE_CHECKLIST = PROJECT_ROOT / "docs" / "deployment" / "SITE_EMBED_GO_NO_GO_CHECKLIST.md"
PRIVACY_CHECKLIST = PROJECT_ROOT / "docs" / "deployment" / "PRIVACY_DATA_FINAL_APPROVAL_CHECKLIST.md"

WIDGET = PROJECT_ROOT / "widget" / "alte-university-ai-chatbot-safe-pro.html"
ASSET_HTML = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.html"
ASSET_JS = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js"
PRODUCTION_ASSETS = [WIDGET, ASSET_HTML, ASSET_JS]

DECISION_STATE = "BACKEND_DEPLOYED_FINAL_HANDOFF_READY_NO_GO_PENDING_SITE_EMBED_AND_SMOKE"

DOCS = [
    README,
    NEXT_PHASES,
    READINESS,
    FINAL_PREFLIGHT,
    FINAL_PRE_EMBED,
    ASSET_DECISION,
    RUNBOOK,
    SMOKE_GUIDE,
    ANSWER_POLICY,
    SITE_RECORD,
    SITE_CHECKLIST,
    PRIVACY_CHECKLIST,
    APPROVAL_RECORD,
    ASSET_HANDOFF_RESULT,
    SITE_EMBED_DECISION,
    SITE_EMBED_CHECKLIST,
    SMOKE_RESULT,
    PUBLIC_LAUNCH_DECISION,
]

FORBIDDEN_ASSET_PATTERNS = [
    re.compile(r"api\.anthropic\.com", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile(r"DATABASE_URL", re.IGNORECASE),
    re.compile(r"DB_PASSWORD", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def required_files_exist() -> list[Check]:
    files = [
        APPROVAL_RECORD,
        HANDOFF_PACKAGE,
        ALTE_SNIPPET,
        JOIN_SNIPPET,
        ASSET_MANIFEST,
        ASSET_HANDOFF_RESULT,
        SITE_EMBED_DECISION,
        SITE_EMBED_CHECKLIST,
        SMOKE_RESULT,
        PUBLIC_LAUNCH_DECISION,
    ]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in files]


def approval_record_statuses() -> list[Check]:
    text = read(APPROVAL_RECORD)
    required = [
        "CONTENT_APPROVAL_STATUS=APPROVED_WITH_CONSERVATIVE_POLICY_PENDING_HUMAN_FINAL_REVIEW",
        "PRIVACY_DATA_APPROVAL_STATUS=APPROVED_IN_PRINCIPLE_PENDING_OFFICIAL_PRIVACY_URL",
        "WEBSITE_ACCESS_STATUS=APPROVED_FOR_PREPARATION_PENDING_ACTUAL_UPLOAD_AND_EMBED",
    ]
    return [Check(f"Approval record contains {item}", item in text) for item in required]


def phase_statuses_recorded() -> list[Check]:
    expected = [
        (ASSET_HANDOFF_RESULT, "PHASE_9M_ASSET_HANDOFF_STATUS=READY_PENDING_ALTE_UPLOAD_AND_EMBED"),
        (SITE_EMBED_DECISION, "ACTUAL_SITE_EMBED_EXECUTION_STATUS=NOT_EXECUTED_PENDING_FINAL_CONFIRMATION"),
        (SMOKE_RESULT, "REAL_DOMAIN_SMOKE_STATUS=NOT_EXECUTED_SITE_NOT_EMBEDDED"),
        (PUBLIC_LAUNCH_DECISION, "PUBLIC_LAUNCH_DECISION=NO_GO_PENDING_SITE_EMBED_AND_REAL_DOMAIN_SMOKE"),
    ]
    return [Check(f"{path.name} contains {needle}", needle in read(path)) for path, needle in expected]


def docs_record_decision_state() -> Check:
    text = "\n".join(read(path) for path in DOCS)
    return Check("Docs record Phase 9L-P decision state", DECISION_STATE in text)


def public_launch_not_complete() -> Check:
    text = "\n".join(read(path).lower() for path in DOCS)
    bad = [
        phrase
        for phrase in [
            "public launch complete",
            "full production launch complete",
            "public launch: complete",
            "public launch approval granted: yes",
        ]
        if phrase in text
    ]
    return Check("Public launch not marked complete", not bad, ", ".join(bad))


def actual_embed_not_complete() -> Check:
    text = "\n".join(read(path).lower() for path in DOCS)
    bad = [
        phrase
        for phrase in [
            "actual site embed completed",
            "actual site embed executed: yes",
            "actual site embed: complete",
            "actual embed complete: yes",
            "site embed complete: yes",
        ]
        if phrase in text
    ]
    return Check("Actual embed not marked complete", not bad, ", ".join(bad))


def real_domain_smoke_not_passed() -> Check:
    text = "\n".join(read(path).lower() for path in DOCS)
    bad = [
        phrase
        for phrase in [
            "real_domain_smoke_status=passed",
            "real-domain smoke passed: yes",
            "real-domain smoke: passed",
            "real domain smoke passed",
        ]
        if phrase in text
    ]
    return Check("Real-domain smoke not marked passed", not bad, ", ".join(bad))


def production_assets_are_safe() -> Check:
    findings: list[str] = []
    for path in PRODUCTION_ASSETS:
        text = read(path)
        for pattern in FORBIDDEN_ASSET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return Check("Production widget/dist assets contain no forbidden patterns", not findings, ", ".join(findings))


def production_assets_have_backend_routes() -> Check:
    text = "\n".join(read(path) for path in PRODUCTION_ASSETS)
    required = ["/chat/session/start", "/chat/message"]
    missing = [item for item in required if item not in text]
    return Check("Widget/dist assets contain backend chat routes", not missing, ", ".join(missing))


def env_not_tracked() -> Check:
    result = subprocess.run(["git", "ls-files", ".env", "backend/.env"], cwd=PROJECT_ROOT, capture_output=True, text=True, check=False)
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked() -> Check:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "backend/.local-secrets", "secret-values.local.txt", "secret-values.local.*"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".local-secrets are not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def run_checks() -> list[Check]:
    return [
        *required_files_exist(),
        *approval_record_statuses(),
        *phase_statuses_recorded(),
        docs_record_decision_state(),
        public_launch_not_complete(),
        actual_embed_not_complete(),
        real_domain_smoke_not_passed(),
        production_assets_are_safe(),
        production_assets_have_backend_routes(),
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
