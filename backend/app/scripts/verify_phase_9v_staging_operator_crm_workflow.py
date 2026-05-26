from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
FRONTEND_APP = PROJECT_ROOT / "frontend" / "app.js"
FRONTEND_INDEX = PROJECT_ROOT / "frontend" / "index.html"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9V_STAGING_OPERATOR_CRM_TEST_WORKFLOW.md"

STATUS = "PHASE_9V_STAGING_OPERATOR_CRM_STATUS=LOCAL_OPERATOR_CRM_CAN_TARGET_PRODUCTION_BACKEND_FOR_NETLIFY_TESTING"
PRODUCTION_BACKEND = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
LOCAL_BACKEND = "http://127.0.0.1:8000"


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def required_files() -> list[Check]:
    return [
        Check("frontend app exists", FRONTEND_APP.exists(), str(FRONTEND_APP)),
        Check("frontend index exists", FRONTEND_INDEX.exists(), str(FRONTEND_INDEX)),
        Check("workflow doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
    ]


def frontend_has_api_presets() -> Check:
    text = read(FRONTEND_APP) + "\n" + read(FRONTEND_INDEX)
    required = [
        "API_PRESETS",
        LOCAL_BACKEND,
        PRODUCTION_BACKEND,
        "useLocalApiBtn",
        "useProductionApiBtn",
        "setApiBase",
        "syncApiControls",
    ]
    missing = [item for item in required if item not in text]
    return Check("frontend has local/production API switch", not missing, ", ".join(missing))


def workflow_status_recorded() -> Check:
    text = read(RESULT_DOC)
    required = [STATUS, PRODUCTION_BACKEND, "https://nimble-croissant-2f66e8.netlify.app", "http://127.0.0.1:5173"]
    missing = [item for item in required if item not in text]
    return Check("workflow doc records staging topology", not missing, ", ".join(missing))


def no_forbidden_frontend_patterns() -> Check:
    text = read(FRONTEND_APP) + "\n" + read(FRONTEND_INDEX)
    patterns = [
        re.compile(r"api\.anthropic\.com", re.IGNORECASE),
        re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
        re.compile("sk" + r"-ant", re.IGNORECASE),
        re.compile("DATABASE" + r"_URL", re.IGNORECASE),
    ]
    findings = [pattern.pattern for pattern in patterns if pattern.search(text)]
    return Check("frontend contains no provider keys/secrets", not findings, ", ".join(findings))


def launch_not_complete() -> Check:
    docs = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "docs" / "NEXT_PHASES.md",
        PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md",
        RESULT_DOC,
    ]
    text = "\n".join(read(path).lower() for path in docs)
    bad = [
        phrase
        for phrase in ["public_launch_decision=go", "public launch complete", "actual site embed executed: yes"]
        if phrase in text
    ]
    return Check("public launch and actual embed not complete", not bad, ", ".join(bad))


def env_not_tracked() -> Check:
    result = subprocess.run(["git", "ls-files", ".env", "backend/.env"], cwd=PROJECT_ROOT, capture_output=True, text=True, check=False)
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked() -> Check:
    result = subprocess.run(["git", "ls-files", ".local-secrets", ".local-secrets/*", "backend/.local-secrets"], cwd=PROJECT_ROOT, capture_output=True, text=True, check=False)
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".local-secrets are not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def run_checks() -> list[Check]:
    return [
        *required_files(),
        frontend_has_api_presets(),
        workflow_status_recorded(),
        no_forbidden_frontend_patterns(),
        launch_not_complete(),
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
