from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOC_PATH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AZ_FINAL_APPROVAL_GATES_AND_STAGED_EMBED_READINESS.md"
EMBED_SNIPPET = '<script src="https://alte.edu.ge/assets/alte-ai-chat-widget.js" defer></script>'
SECRET_PATTERNS = [
    "DATABASE_URL=",
    "ANTHROPIC_API_KEY=",
    "sk-ant",
    "password=",
    "token=",
]


def read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8") if DOC_PATH.exists() else ""


def tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    return result.stdout.splitlines()


def check(name: str, passed: bool, detail: str = "") -> tuple[str, bool, str]:
    print(f"{'PASS' if passed else 'FAIL'} {name}: {detail}")
    return name, passed, detail


def run_checks() -> list[tuple[str, bool, str]]:
    text = read_doc()
    tracked = tracked_files()
    return [
        check("9AZ doc exists", DOC_PATH.exists(), str(DOC_PATH)),
        check("decision state documented", "BACKEND_DEPLOYED_FULL_KNOWLEDGE_AND_PUBLIC_ANSWER_CLEANUP_VERIFIED_PENDING_APPROVALS" in text),
        check("public launch remains NO-GO", "Public launch:\n\n`NO-GO`" in text and "Ready for public launch: NO-GO" in text),
        check("backend revision documented", "alte-ai-crm-backend-00051-btg" in text),
        check("image tag documented", "v0.9-phase-9ax-9ay-final-routing-cleanup3" in text),
        check("QA results documented", all(value in text for value in ["7/7 PASS", "53/53 PASS", "Browser/API answer-cleanliness QA: `7/7 PASS`"])),
        check("remaining failures none", "Remaining failures/gaps: none" in text),
        check("privacy gate pending", "Status: `PENDING`" in text and "official privacy URL" in text),
        check("contact flow not approved", "Status: `NOT_APPROVED`" in text and "No lead/customer/task created." in text),
        check("asset upload not executed", "Upload status: `NOT_EXECUTED_PENDING_APPROVAL`" in text and "Asset upload executed: NO" in text),
        check("asset path and hash documented", "dist/widget/alte-ai-chat-widget.js" in text and "A5083446ADE39513D77969115FE0CEF21A4BF8EF3F588551BC87EFDD4E2C2B73" in text),
        check("staged embed not executed", "Status: `NOT_EXECUTED_PENDING_APPROVAL`" in text and "Staged embed executed: NO" in text),
        check("embed snippet documented", EMBED_SNIPPET in text),
        check("real-domain smoke checklist documented", "Real-Domain Smoke Checklist" in text and "Bachelor ECTS" in text and "operator handover" in text),
        check("rollback plan documented", "Rollback Plan" in text and "Remove the staged embed snippet" in text),
        check("dirty tree owner decision documented", "Dirty tree reconciliation" in text and "Owner decision required" in text),
        check("safety no execution documented", all(marker in text for marker in ["Real `alte.edu.ge` modified: NO", "Assets uploaded: NO", "Embed executed: NO", "DB schema/migration/seed/import changed or run: NO", "Secret Manager changed: NO", "CORS changed: NO", "Bridge Hub touched: NO"])),
        check("no secrets in doc", all(pattern not in text for pattern in SECRET_PATTERNS)),
        check("env/local-secrets are not tracked", not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]),
    ]


def main() -> int:
    checks = run_checks()
    return 0 if all(passed for _, passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
