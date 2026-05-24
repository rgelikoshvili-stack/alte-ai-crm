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

VERIFIED_STATE = "BACKEND_DEPLOYED_NO_CONTACT_GUARD_VERIFIED_PENDING_TEST_KNOWLEDGE_APPROVAL"
REVIEW_STATE = "BACKEND_DEPLOYED_NO_CONTACT_GUARD_SMOKE_NEEDS_REVIEW"
IMAGE_TAG = "v0.8-no-contact-guard"

SECRET_PATTERNS = [
    re.compile(r"sk-ant-", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
    re.compile(r"DB_PASSWORD\s*=", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]

DOC_FILES = [
    DEPLOYMENT_DOCS / "STANDALONE_CHATBOT_API_SMOKE_RESULT.md",
    DEPLOYMENT_DOCS / "PRODUCTION_READINESS_DECISION.md",
    DEPLOYMENT_DOCS / "FINAL_PREFLIGHT_GATE.md",
    NEXT_PHASES,
    README,
]


@dataclass
class RedeployDocsCheck:
    name: str
    passed: bool
    detail: str = ""


def _read(paths: list[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


def image_tag_recorded() -> RedeployDocsCheck:
    text = _read(DOC_FILES)
    return RedeployDocsCheck("No-contact guard image tag recorded", IMAGE_TAG in text)


def redeploy_status_recorded() -> RedeployDocsCheck:
    text = _read(DOC_FILES).lower()
    required = [
        "no-contact guard",
        "deployed",
        "safe standalone api smoke rerun",
        "lead/task side effect fixed: yes",
    ]
    missing = [item for item in required if item not in text]
    return RedeployDocsCheck("No-contact guard deployment and smoke recorded", not missing, ", ".join(missing))


def contact_flow_not_run_recorded() -> RedeployDocsCheck:
    text = _read(DOC_FILES).lower()
    required = ["contact-flow", "not run", "contact details submitted: no"]
    missing = [item for item in required if item not in text]
    return RedeployDocsCheck("Contact-flow remains not run", not missing, ", ".join(missing))


def decision_state_documented() -> RedeployDocsCheck:
    text = _read([DEPLOYMENT_DOCS / "PRODUCTION_READINESS_DECISION.md", DEPLOYMENT_DOCS / "FINAL_PREFLIGHT_GATE.md", NEXT_PHASES, README])
    return RedeployDocsCheck("Decision state documented", VERIFIED_STATE in text or REVIEW_STATE in text)


def no_forbidden_patterns(paths: list[Path] | None = None) -> RedeployDocsCheck:
    paths = paths or DOC_FILES
    findings: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    return RedeployDocsCheck("No forbidden secret patterns", not findings, ", ".join(findings))


def env_not_tracked(project_root: Path = PROJECT_ROOT) -> RedeployDocsCheck:
    result = subprocess.run(
        ["git", "ls-files", ".env", "backend/.env"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return RedeployDocsCheck(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked(project_root: Path = PROJECT_ROOT) -> RedeployDocsCheck:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "secret-values.local.txt", "secret-values.local.*"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return RedeployDocsCheck(
        ".local-secrets and generated secret files are not tracked",
        not tracked,
        ", ".join(tracked) if tracked else "not tracked",
    )


def run_checks() -> list[RedeployDocsCheck]:
    return [
        image_tag_recorded(),
        redeploy_status_recorded(),
        contact_flow_not_run_recorded(),
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
