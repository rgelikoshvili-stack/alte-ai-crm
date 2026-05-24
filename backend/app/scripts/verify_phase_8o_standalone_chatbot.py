from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
DEPLOYMENT_DOCS = PROJECT_ROOT / "docs" / "deployment"
WIDGET_ROOT = PROJECT_ROOT / "widget"
KNOWLEDGE_ROOT = BACKEND_ROOT / "app" / "knowledge_seed"
SCRIPTS_ROOT = BACKEND_ROOT / "app" / "scripts"
README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"

BACKEND_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"
DECISION_STATE = "BACKEND_DEPLOYED_FULL_STANDALONE_CHATBOT_READY_PENDING_REAL_SITE_EMBED"
KA_CONSENT = "საკონტაქტო მონაცემებს ვიყენებთ მხოლოდ კონსულტაციისთვის."
EN_CONSENT = "We use your contact details only to provide consultation."

SECRET_PATTERNS = [
    re.compile(r"sk-ant-", re.IGNORECASE),
    re.compile(r"DATABASE_URL", re.IGNORECASE),
    re.compile(r"DB_PASSWORD", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]


@dataclass
class StandaloneChatbotCheck:
    name: str
    passed: bool
    detail: str = ""


REQUIRED_FILES = [
    WIDGET_ROOT / "full-standalone-chatbot-test.html",
    KNOWLEDGE_ROOT / "alte_required_test_knowledge_v1.json",
    SCRIPTS_ROOT / "seed_required_test_knowledge.py",
    SCRIPTS_ROOT / "standalone_chatbot_api_smoke.py",
    DEPLOYMENT_DOCS / "STANDALONE_TEST_KNOWLEDGE_RUNBOOK.md",
    DEPLOYMENT_DOCS / "FULL_STANDALONE_CHATBOT_SMOKE_PLAN.md",
    DEPLOYMENT_DOCS / "STANDALONE_TEST_SITE_RUNBOOK.md",
]

SECRET_SCAN_FILES = REQUIRED_FILES + [
    WIDGET_ROOT / "README.md",
]


def _read(paths: list[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


def required_files_exist() -> list[StandaloneChatbotCheck]:
    return [StandaloneChatbotCheck(f"{path.name} exists", path.exists(), str(path)) for path in REQUIRED_FILES]


def seed_json_valid() -> StandaloneChatbotCheck:
    path = KNOWLEDGE_ROOT / "alte_required_test_knowledge_v1.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    required_categories = {
        "contact",
        "admissions",
        "finance",
        "international_admissions",
        "medicine",
        "deadlines",
        "handover",
    }
    categories = {item.get("category") for item in data}
    missing_categories = sorted(required_categories - categories)
    required_keys = {"source_key", "title", "language", "category", "department", "status", "content", "keywords"}
    invalid_rows = [
        str(index)
        for index, item in enumerate(data)
        if not required_keys.issubset(item.keys()) or item.get("status") not in {"approved", "review_required"}
    ]
    passed = bool(data) and not missing_categories and not invalid_rows
    detail = ""
    if missing_categories:
        detail += f"missing categories: {', '.join(missing_categories)} "
    if invalid_rows:
        detail += f"invalid rows: {', '.join(invalid_rows)}"
    return StandaloneChatbotCheck("Seed JSON is valid", passed, detail.strip())


def standalone_page_valid() -> StandaloneChatbotCheck:
    text = (WIDGET_ROOT / "full-standalone-chatbot-test.html").read_text(encoding="utf-8")
    required = [
        "Alte AI Chatbot — Standalone Test Site",
        BACKEND_URL,
        "./alte-chat-widget.v0.8.js",
        "alte.edu.ge",
        "join.alte.edu.ge",
        "ka",
        "en",
        KA_CONSENT,
        EN_CONSENT,
        "This test site uses the production backend. Do not enter real student data unless approved.",
    ]
    missing = [item for item in required if item not in text]
    return StandaloneChatbotCheck("Standalone chatbot page is valid", not missing, ", ".join(missing))


def smoke_script_valid() -> StandaloneChatbotCheck:
    text = (SCRIPTS_ROOT / "standalone_chatbot_api_smoke.py").read_text(encoding="utf-8")
    required = [
        BACKEND_URL,
        "--include-contact-flow",
        "alte.edu.ge",
        "join.alte.edu.ge",
        "/health",
        "/version",
        "/diagnostics/ai",
    ]
    missing = [item for item in required if item not in text]
    return StandaloneChatbotCheck("Standalone API smoke script is valid", not missing, ", ".join(missing))


def runbooks_documented() -> StandaloneChatbotCheck:
    text = _read(
        [
            DEPLOYMENT_DOCS / "STANDALONE_TEST_KNOWLEDGE_RUNBOOK.md",
            DEPLOYMENT_DOCS / "FULL_STANDALONE_CHATBOT_SMOKE_PLAN.md",
            DEPLOYMENT_DOCS / "STANDALONE_TEST_SITE_RUNBOOK.md",
        ]
    )
    required = [
        "python -m app.scripts.seed_required_test_knowledge",
        "python -m app.scripts.standalone_chatbot_api_smoke",
        "full-standalone-chatbot-test.html",
        "production CORS",
        "Do not enter real student data unless approved",
    ]
    missing = [item for item in required if item not in text]
    return StandaloneChatbotCheck("Standalone runbooks are documented", not missing, ", ".join(missing))


def decision_state_documented() -> StandaloneChatbotCheck:
    text = _read(
        [
            DEPLOYMENT_DOCS / "PRODUCTION_READINESS_DECISION.md",
            DEPLOYMENT_DOCS / "FINAL_PREFLIGHT_GATE.md",
            README,
            NEXT_PHASES,
            WIDGET_ROOT / "README.md",
        ]
    )
    forbidden = [
        "FULL_PRODUCTION_LAUNCH_COMPLETE",
        "WEBSITE_WIDGET_EMBED_COMPLETED",
        "WEBSITE_PRIVACY_APPROVED_FOR_WIDGET_EMBED",
    ]
    findings = [item for item in forbidden if item in text]
    return StandaloneChatbotCheck(
        "Decision state remains pending real site embed",
        DECISION_STATE in text and not findings,
        ", ".join(findings),
    )


def no_forbidden_patterns(paths: list[Path] | None = None) -> StandaloneChatbotCheck:
    paths = paths or SECRET_SCAN_FILES
    findings: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return StandaloneChatbotCheck("No forbidden secret patterns", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> StandaloneChatbotCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return StandaloneChatbotCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked(project_root: Path = PROJECT_ROOT) -> StandaloneChatbotCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return StandaloneChatbotCheck(
        ".local-secrets and generated secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks() -> list[StandaloneChatbotCheck]:
    return [
        *required_files_exist(),
        seed_json_valid(),
        standalone_page_valid(),
        smoke_script_valid(),
        runbooks_documented(),
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
