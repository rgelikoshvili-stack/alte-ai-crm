from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INVENTORY_DOC = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AS_ACTIVE_KNOWLEDGE_INVENTORY.md"
QA_DATASET = PROJECT_ROOT / "backend" / "app" / "data" / "evaluation" / "phase_9as_full_knowledge_qa.json"
KNOWLEDGE_REPORT = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AS_FULL_KNOWLEDGE_COVERAGE_QA_RESULT.md"
OPERATOR_REPORT = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AS_OPERATOR_CRM_ALIGNMENT_QA_RESULT.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AS_FULL_KNOWLEDGE_AND_OPERATOR_VERIFICATION_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"

SECRET_PATTERNS = [
    "DATABASE_URL=",
    "ANTHROPIC_API_KEY=",
    "OPENAI_API_KEY=",
    "sk-ant",
]
REAL_CONTACT_PATTERNS = [
    "@gmail.com",
    "+995",
    "555-",
    "599-",
]
MOJIBAKE_MARKERS = ["áƒ", "â†", "â€¢", "�"]
REQUIRED_CATEGORIES = {
    "official_academic_facts",
    "academic_calendar",
    "admissions",
    "clarification",
    "routing",
    "unsupported",
    "operator_handover",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    return result.stdout.splitlines()


def check(name: str, passed: bool, detail: str = "") -> tuple[str, bool, str]:
    print(f"{'PASS' if passed else 'FAIL'} {name}: {detail}")
    return name, passed, detail


def load_dataset() -> list[dict]:
    if not QA_DATASET.exists():
        return []
    return json.loads(QA_DATASET.read_text(encoding="utf-8"))


def docs_surface(paths: Iterable[Path]) -> str:
    return "\n".join(read(path) for path in paths)


def run_checks() -> list[tuple[str, bool, str]]:
    dataset = load_dataset()
    categories = {item.get("category") for item in dataset}
    result_doc = read(RESULT_DOC)
    inventory = read(INVENTORY_DOC)
    public = read(PUBLIC_LAUNCH).lower()
    knowledge_report = read(KNOWLEDGE_REPORT)
    operator_report = read(OPERATOR_REPORT)
    safety_surface = docs_surface([INVENTORY_DOC, KNOWLEDGE_REPORT, OPERATOR_REPORT, RESULT_DOC])
    tracked = tracked_files()

    return [
        check("inventory doc exists", INVENTORY_DOC.exists(), str(INVENTORY_DOC)),
        check("QA dataset exists", QA_DATASET.exists(), str(QA_DATASET)),
        check("QA dataset has at least 50 questions", len(dataset) >= 50, str(len(dataset))),
        check("required categories present", REQUIRED_CATEGORIES.issubset(categories), ", ".join(sorted(categories))),
        check("full knowledge QA report exists", KNOWLEDGE_REPORT.exists(), str(KNOWLEDGE_REPORT)),
        check("operator alignment QA report exists", OPERATOR_REPORT.exists(), str(OPERATOR_REPORT)),
        check("result doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
        check("result status documented", "PHASE_9AS_FULL_VERIFICATION_STATUS=" in result_doc),
        check("public launch remains NO-GO", "public_launch_decision=go" not in public and "Public launch: NO-GO" in result_doc),
        check("real site not modified", "REAL_ALTE_SITE_MODIFIED=NO" in result_doc),
        check("contact creation not executed", "CONTACT_FLOW_EXECUTED=NO" in result_doc),
        check("no lead/customer/task creation marked", "LEAD_TASK_CUSTOMER_CREATED=NO" in result_doc),
        check("hallucination check documented", "hallucination" in knowledge_report.lower() or "no-hallucination" in knowledge_report.lower()),
        check("handover pollution check documented", "handover" in knowledge_report.lower() and "handover" in operator_report.lower()),
        check("inventory documents source groups", "official_academic_rules" in inventory and "academic_calendar_2025_2026" in inventory),
        check("no mojibake in new docs", not any(marker in safety_surface for marker in MOJIBAKE_MARKERS)),
        check("no secrets", not any(pattern in safety_surface for pattern in SECRET_PATTERNS)),
        check("no real contact data", not any(pattern in safety_surface for pattern in REAL_CONTACT_PATTERNS)),
        check("env/local-secrets not tracked", not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]),
    ]


def main() -> int:
    checks = run_checks()
    return 0 if all(passed for _, passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
