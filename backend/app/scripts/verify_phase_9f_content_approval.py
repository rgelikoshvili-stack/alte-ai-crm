from __future__ import annotations

import csv
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

STRATEGY_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9F_OFFICIAL_CONTENT_APPROVAL_STRATEGY.md"
PREP_SCRIPT = BACKEND_ROOT / "app" / "scripts" / "prepare_conservative_content_decisions.py"
VALIDATE_SCRIPT = BACKEND_ROOT / "app" / "scripts" / "validate_phase_9f_content_decisions.py"
CONSERVATIVE_CSV = PROJECT_ROOT / "docs" / "reviewer_package" / "alte_kb_conservative_decisions_for_approval.csv"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9F_HUMAN_REVIEWER_DECISIONS_RESULT.md"

README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
READINESS = PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md"
FINAL_PREFLIGHT = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md"
FINAL_GATE = PROJECT_ROOT / "docs" / "deployment" / "FINAL_PRE_EMBED_APPROVAL_GATE.md"
OFFICIAL_REPORT = PROJECT_ROOT / "docs" / "deployment" / "OFFICIAL_CONTENT_REVIEW_REPORT.md"
OFFICIAL_CHECKLIST = PROJECT_ROOT / "docs" / "deployment" / "OFFICIAL_CONTENT_REVIEW_CHECKLIST.md"
ANSWER_POLICY = PROJECT_ROOT / "docs" / "deployment" / "CHATBOT_PUBLIC_ANSWER_POLICY.md"

STATUS = "PHASE_9F_CONTENT_APPROVAL_STATUS=CONSERVATIVE_DECISIONS_PREPARED_PENDING_HUMAN_APPROVAL"
DECISION_STATE = "BACKEND_DEPLOYED_CONTENT_DECISIONS_PREPARED_PENDING_HUMAN_APPROVAL"
SYSTEM_REVIEWER = "SYSTEM_CONSERVATIVE_DRAFT"

DOCS = [
    STRATEGY_DOC,
    RESULT_DOC,
    README,
    NEXT_PHASES,
    READINESS,
    FINAL_PREFLIGHT,
    FINAL_GATE,
    OFFICIAL_REPORT,
    OFFICIAL_CHECKLIST,
    ANSWER_POLICY,
]

SECRET_PATTERNS = [
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
    re.compile(r"DB_PASSWORD\s*=", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def required_files_exist() -> list[Check]:
    return [
        Check("Phase 9F strategy doc exists", STRATEGY_DOC.exists(), str(STRATEGY_DOC)),
        Check("Conservative decision preparation script exists", PREP_SCRIPT.exists(), str(PREP_SCRIPT)),
        Check("Phase 9F validation script exists", VALIDATE_SCRIPT.exists(), str(VALIDATE_SCRIPT)),
        Check("Conservative decision CSV exists", CONSERVATIVE_CSV.exists(), str(CONSERVATIVE_CSV)),
        Check("Phase 9F result doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
    ]


def result_status_recorded() -> Check:
    text = RESULT_DOC.read_text(encoding="utf-8") if RESULT_DOC.exists() else ""
    return Check("Phase 9F approval status recorded", STATUS in text)


def decision_state_documented() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8") for path in DOCS if path.exists())
    return Check("Phase 9F decision state documented", DECISION_STATE in text)


def public_launch_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in DOCS if path.exists())
    bad = [
        phrase
        for phrase in ["public launch complete", "full production launch complete", "actual site embed completed"]
        if phrase in text
    ]
    return Check("Public launch not marked complete", not bad, ", ".join(bad))


def official_human_approval_not_complete() -> Check:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in DOCS if path.exists())
    bad = [
        phrase
        for phrase in ["official content approval complete: yes", "official human approval exists: yes"]
        if phrase in text
    ]
    return Check("Official human approval not marked complete", not bad, ", ".join(bad))


def high_sensitivity_not_public_approved_by_system() -> Check:
    if not CONSERVATIVE_CSV.exists():
        return Check("High sensitivity rows are not public approved by system draft", False, "missing CSV")
    findings: list[str] = []
    with CONSERVATIVE_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader, start=2):
            sensitivity = (row.get("sensitivity") or "").strip().upper()
            decision = (row.get("decision") or "").strip().upper()
            reviewer = (row.get("reviewer") or "").strip()
            public_allowed = (row.get("public_launch_allowed") or "").strip().lower() in {"true", "1", "yes"}
            if sensitivity == "HIGH" and reviewer == SYSTEM_REVIEWER and (decision == "APPROVE" or public_allowed):
                findings.append(f"row {index}")
                if len(findings) >= 5:
                    break
    return Check("High sensitivity rows are not public approved by system draft", not findings, ", ".join(findings))


def no_forbidden_patterns() -> Check:
    findings: list[str] = []
    for path in [PREP_SCRIPT, VALIDATE_SCRIPT, CONSERVATIVE_CSV, *DOCS]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8-sig")
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
        result_status_recorded(),
        decision_state_documented(),
        public_launch_not_complete(),
        official_human_approval_not_complete(),
        high_sensitivity_not_public_approved_by_system(),
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
