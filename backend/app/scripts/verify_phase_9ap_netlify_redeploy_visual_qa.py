from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AP_NETLIFY_REDEPLOY_AND_VISUAL_QA_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
MOJIBAKE_MARKER = "\u00e1\u0192"
SECRET_PATTERNS = [
    "DATABASE_URL=",
    "ANTHROPIC_API_KEY=",
    "sk-ant",
    "password=",
    "token=",
]
REAL_CONTACT_PATTERNS = [
    "@gmail.com",
    "+995",
    "555-",
    "599-",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    return result.stdout.splitlines()


def check(name: str, passed: bool, detail: str = "") -> tuple[str, bool, str]:
    print(f"{'PASS' if passed else 'FAIL'} {name}: {detail}")
    return name, passed, detail


def run_checks() -> list[tuple[str, bool, str]]:
    doc = read(RESULT_DOC)
    public = read(PUBLIC_LAUNCH).lower()
    tracked = tracked_files()
    combined = "\n".join([doc, public])
    return [
        check("result doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
        check("status passed", "PHASE_9AP_NETLIFY_STATUS=PASSED" in doc),
        check(
            "decision state updated",
            "BACKEND_DEPLOYED_FULL_CHATBOT_FUNCTIONALITY_FIXES_VERIFIED_PENDING_APPROVALS" in doc,
        ),
        check("public launch remains NO-GO", "Public launch: NO-GO" in doc and "public_launch_decision=go" not in public and "no-go" in public),
        check("Netlify deploy source documented", "Deploy source branch:" in doc and "master" in doc),
        check("master sync commit documented", "1b89682" in doc and "phase 9ap: sync netlify frontend fixes" in doc),
        check("live source freshness documented", "LIVE_SOURCE_FRESH=YES" in doc and "HTTP_STATUS=200" in doc),
        check("live source URLs documented", "nimble-croissant-2f66e8.netlify.app/variants/pro-v2-chat.jsx" in doc),
        check("frontend label freshness documented", "მედიცინა / MD" in doc and "მედიცინა/MD" in doc),
        check("contact prefill freshness documented", "latestUserText() || m.text" in doc and "m.text || latestUserText()" in doc),
        check("visual QA passed documented", "VISUAL_QA_STATUS=PASSED" in doc),
        check("contact prefill browser check passed", "CONTACT_PREFILL_PASS=True" in doc),
        check("production QA passed documented", "PRODUCTION_9AP_QA_STATUS=PASSED" in doc and "16/16" in doc),
        check("real site not modified", "REAL_ALTE_SITE_MODIFIED=NO" in doc),
        check("no asset upload/embed executed", "Real Alte asset upload executed: NO" in doc and "Real-site embed executed: NO" in doc),
        check("contact flow not executed", "CONTACT_FLOW_EXECUTED=NO" in doc),
        check("no lead/task/customer created", "LEAD_TASK_CUSTOMER_CREATED=NO" in doc),
        check("no real contact data", "REAL_CONTACT_DATA_SENT=NO" in doc and all(pattern not in combined for pattern in REAL_CONTACT_PATTERNS)),
        check("no secrets", all(pattern not in combined for pattern in SECRET_PATTERNS)),
        check("env/local-secrets not tracked", not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]),
        check("no mojibake marker", MOJIBAKE_MARKER not in combined),
    ]


def main() -> int:
    checks = run_checks()
    return 0 if all(passed for _, passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
