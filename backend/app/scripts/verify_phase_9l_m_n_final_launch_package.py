from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from app.scripts.validate_final_launch_approvals import evaluate_approvals


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

APPROVAL_INTAKE = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9L_FINAL_APPROVAL_INTAKE.md"
APPROVAL_VALIDATOR = BACKEND_ROOT / "app" / "scripts" / "validate_final_launch_approvals.py"
HANDOFF_PACKAGE = PROJECT_ROOT / "docs" / "final_handoff" / "FINAL_WEBSITE_HANDOFF_PACKAGE_GEO.md"
ASSET_MANIFEST = PROJECT_ROOT / "docs" / "final_handoff" / "WIDGET_ASSET_MANIFEST.md"
MANIFEST_BUILDER = BACKEND_ROOT / "app" / "scripts" / "build_widget_asset_manifest.py"
ACTUAL_EMBED_RESULT = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9M_ACTUAL_SITE_EMBED_EXECUTION_RESULT.md"
REAL_DOMAIN_SMOKE_PLAN = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_REAL_DOMAIN_SMOKE_PLAN_FINAL.md"
REAL_DOMAIN_SMOKE_RESULT = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_REAL_DOMAIN_SMOKE_RESULT.md"
PUBLIC_LAUNCH_DECISION = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9O_PUBLIC_LAUNCH_DECISION.md"

README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
READINESS = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md"
FINAL_PREFLIGHT = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md"
FINAL_PRE_EMBED = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PRE_EMBED_APPROVAL_GATE.md"
SITE_CHECKLIST = PROJECT_ROOT / "docs" / "deployment" / "SITE_EMBED_GO_NO_GO_CHECKLIST.md"
SITE_APPROVAL_RECORD = PROJECT_ROOT / "docs" / "deployment" / "SITE_EMBED_FINAL_APPROVAL_RECORD.md"

WIDGET = PROJECT_ROOT / "widget" / "alte-university-ai-chatbot-safe-pro.html"
ASSET_HTML = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.html"
ASSET_JS = PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js"
PRODUCTION_ASSETS = [WIDGET, ASSET_HTML, ASSET_JS]

NO_GO_DECISION = "BACKEND_DEPLOYED_FINAL_HANDOFF_READY_NO_GO_PENDING_APPROVALS_AND_SITE_EMBED"
GO_READY_DECISION = "BACKEND_DEPLOYED_SITE_EMBEDDED_SMOKE_PASSED_PUBLIC_LAUNCH_READY"

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
        APPROVAL_INTAKE,
        APPROVAL_VALIDATOR,
        HANDOFF_PACKAGE,
        ASSET_MANIFEST,
        MANIFEST_BUILDER,
        ACTUAL_EMBED_RESULT,
        REAL_DOMAIN_SMOKE_PLAN,
        REAL_DOMAIN_SMOKE_RESULT,
        PUBLIC_LAUNCH_DECISION,
    ]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in files]


def actual_embed_status_recorded() -> Check:
    text = read(ACTUAL_EMBED_RESULT)
    valid = "ACTUAL_SITE_EMBED_EXECUTION_STATUS=NOT_EXECUTED_MISSING_APPROVALS" in text or "ACTUAL_SITE_EMBED_EXECUTION_STATUS=EXECUTED" in text
    return Check("Actual embed execution status recorded", valid)


def real_domain_smoke_status_recorded() -> Check:
    text = read(REAL_DOMAIN_SMOKE_RESULT)
    valid = "REAL_DOMAIN_SMOKE_STATUS=NOT_EXECUTED_SITE_NOT_EMBEDDED" in text or "REAL_DOMAIN_SMOKE_STATUS=PASSED" in text
    return Check("Real-domain smoke status recorded", valid)


def public_launch_decision_recorded() -> Check:
    text = read(PUBLIC_LAUNCH_DECISION)
    valid = "PUBLIC_LAUNCH_DECISION=NO_GO_PENDING_APPROVALS_OR_SITE_EMBED" in text or "PUBLIC_LAUNCH_DECISION=GO_APPROVED_FOR_PUBLIC_LAUNCH" in text
    return Check("Public launch decision recorded", valid)


def docs_record_final_decision_state() -> Check:
    docs = [README, NEXT_PHASES, READINESS, FINAL_PREFLIGHT, FINAL_PRE_EMBED, SITE_CHECKLIST, SITE_APPROVAL_RECORD, PUBLIC_LAUNCH_DECISION]
    text = "\n".join(read(path) for path in docs)
    valid = NO_GO_DECISION in text or GO_READY_DECISION in text
    return Check("Docs record final Phase 9L-M-N decision state", valid)


def go_has_required_evidence() -> Check:
    public_text = read(PUBLIC_LAUNCH_DECISION)
    if "PUBLIC_LAUNCH_DECISION=GO_APPROVED_FOR_PUBLIC_LAUNCH" not in public_text:
        return Check("GO decision has required evidence when applicable", True, "NO-GO state")

    approval = evaluate_approvals()
    combined = "\n".join(read(path) for path in [ACTUAL_EMBED_RESULT, REAL_DOMAIN_SMOKE_RESULT, APPROVAL_INTAKE])
    valid = (
        approval["go_allowed"] is True
        and "ACTUAL_SITE_EMBED_EXECUTION_STATUS=EXECUTED" in combined
        and "REAL_DOMAIN_SMOKE_STATUS=PASSED" in combined
        and "#privacy-policy-pending" not in combined
    )
    return Check("GO decision has required evidence when applicable", valid)


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
    return Check("Widget assets contain backend chat routes", not missing, ", ".join(missing))


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
        actual_embed_status_recorded(),
        real_domain_smoke_status_recorded(),
        public_launch_decision_recorded(),
        docs_record_final_decision_state(),
        go_has_required_evidence(),
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
