from __future__ import annotations

import json
import re
import subprocess
import csv
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
KB_DIR = PROJECT_ROOT / "backend" / "app" / "knowledge_seed" / "alte_chatbot_required_knowledge"
JSONL_PATH = KB_DIR / "alte_chatbot_required_knowledge.jsonl"
MD_PATH = KB_DIR / "alte_chatbot_required_knowledge.md"
SOURCES_PATH = KB_DIR / "alte_chatbot_required_sources.md"
BUILDER_PATH = PROJECT_ROOT / "backend" / "app" / "scripts" / "build_alte_chatbot_required_knowledge.py"
APPLY_PATH = PROJECT_ROOT / "backend" / "app" / "scripts" / "apply_alte_chatbot_required_knowledge.py"
RESULT_PATH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9Z_ALTE_CHATBOT_REQUIRED_KNOWLEDGE_RESULT.md"
REVIEWER_CSV_PATH = PROJECT_ROOT / "backend" / "reports" / "alte_chatbot_required_knowledge_reviewer_queue.csv"

REQUIRED_TOPICS = {
    "საგანმანათლებლო პროგრამები",
    "აკადემიური კალენდარი",
    "სასწავლო პროცესი",
    "ბაკალავრიატი",
    "მაგისტრატურა",
    "გამოცდები",
    "კრედიტების აღიარება",
    "ინდივიდუალური სასწავლო გეგმა",
    "ელექტრონული სწავლება",
    "აკადემიური კეთილსინდისიერება",
    "ფინანსური მხარდაჭერა",
    "სახელმწიფო და სოციალური გრანტები",
    "ფინანსური საკითხების დეპარტამენტი",
    "დეკანის გრანტი",
    "სტუდენტთა მომსახურება",
    "სტუდენტური სერვისების დეპარტამენტი",
    "სტუდენტის უფლებები",
    "ომბუდსმენი",
    "სტუდენტური თვითმმართველობა",
    "ბიბლიოთეკა",
    "სპეციალური საჭიროების მქონე პირთა მომსახურება",
    "კარიერა და კურსდამთავრებულები",
    "საერთაშორისო სტუდენტები და ურთიერთობები",
    "IT მხარდაჭერა",
    "ფორმალური კომუნიკაცია და განცხადებები",
    "გენერაციული AI",
    "უნივერსიტეტის დებულება",
    "ეთიკა",
}

FORBIDDEN_PATTERNS = [
    r"ANTHROPIC_API_KEY",
    "sk" + r"-ant",
    r"api\.anthropic\.com",
    r"DATABASE_URL",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def is_tracked(path: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", path],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def run_checks() -> dict:
    for path in [BUILDER_PATH, APPLY_PATH, JSONL_PATH, MD_PATH, SOURCES_PATH, RESULT_PATH, REVIEWER_CSV_PATH]:
        require(path.exists(), f"Missing required knowledge artifact: {path}")

    rows = load_jsonl(JSONL_PATH)
    require(len(rows) >= 300, "Required knowledge JSONL should contain broad chatbot coverage")

    required_fields = {
        "source_id",
        "question",
        "answer",
        "topic",
        "department",
        "language",
        "source_title",
        "source_file",
        "source_local_path",
        "answer_policy",
        "handover_recommended",
        "student_facing",
    }
    topics = Counter(row["topic"] for row in rows)
    for row in rows:
        missing = required_fields - row.keys()
        require(not missing, f"Missing fields {missing}: {row.get('source_id')}")
        require(row["language"] == "ka", f"Non-Georgian required knowledge row: {row['source_id']}")
        require(row["student_facing"] is True, f"Non-student-facing row included: {row['source_id']}")
        require("áƒ" not in row["question"], f"Mojibake in question: {row['source_id']}")
        require("áƒ" not in row["answer"][:500], f"Mojibake in answer: {row['source_id']}")
        if row["department"] in {"finance", "academic_registry"}:
            require(
                row["answer_policy"] != "direct_general" or row["handover_recommended"],
                f"Sensitive academic/finance row lacks cautious policy: {row['source_id']}",
            )

    missing_topics = REQUIRED_TOPICS - set(topics)
    require(not missing_topics, f"Missing required topics: {sorted(missing_topics)}")
    require(topics["საგანმანათლებლო პროგრამები"] >= 20, "Program catalog coverage is too small")
    require(topics["სასწავლო პროცესი"] >= 10, "Study process coverage is too small")

    with REVIEWER_CSV_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        reviewer_rows = list(csv.DictReader(handle))
    require(len(reviewer_rows) == len(rows), "Reviewer CSV row count must match JSONL")
    require(all(not row["reviewer_decision"] for row in reviewer_rows), "Reviewer decisions must start blank")

    generated_text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in [JSONL_PATH, MD_PATH, SOURCES_PATH, RESULT_PATH])
    for pattern in FORBIDDEN_PATTERNS:
        require(not re.search(pattern, generated_text, re.IGNORECASE), f"Forbidden marker found: {pattern}")

    result_text = RESULT_PATH.read_text(encoding="utf-8")
    require(
        "PHASE_9Z_ALTE_CHATBOT_REQUIRED_KNOWLEDGE_STATUS=READY_PENDING_REVIEW_AND_DB_APPLY" in result_text,
        "Result status missing or incorrect",
    )
    require("Production DB modified: NO" in result_text, "Result must record no production DB modification")
    require("--apply run: NO" in result_text, "Result must record apply was not run")
    require("Dry-run apply result: PASS" in result_text, "Result must record dry-run apply passed")

    docs_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in [
            PROJECT_ROOT / "README.md",
            PROJECT_ROOT / "docs" / "NEXT_PHASES.md",
            PROJECT_ROOT / "docs" / "deployment" / "PRODUCTION_READINESS_DECISION.md",
            PROJECT_ROOT / "docs" / "deployment" / "FINAL_PREFLIGHT_GATE.md",
        ]
        if path.exists()
    )
    require(
        "BACKEND_DEPLOYED_CHATBOT_REQUIRED_KNOWLEDGE_READY_PENDING_REVIEW_AND_APPLY" in docs_text,
        "Decision state missing from status docs",
    )
    require("PUBLIC_LAUNCH_DECISION=GO_APPROVED_FOR_PUBLIC_LAUNCH" not in docs_text, "Public launch must not be GO")
    require(not is_tracked(".env"), ".env must not be tracked")
    require(not is_tracked(".local-secrets"), ".local-secrets must not be tracked")

    return {
        "status": "PASS",
        "records": len(rows),
        "topics": dict(topics),
        "source_count": len({row["source_title"] for row in rows}),
        "reviewer_rows": len(reviewer_rows),
    }


def main() -> None:
    print(json.dumps(run_checks(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
