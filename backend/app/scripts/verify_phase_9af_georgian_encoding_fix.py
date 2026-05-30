from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AF_GEORGIAN_ENCODING_FIX_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
SMOKE_SCRIPT = BACKEND_ROOT / "app" / "scripts" / "production_georgian_encoding_smoke.py"
VISUAL_SCRIPT = BACKEND_ROOT / "app" / "scripts" / "visual_qa_netlify_widget.py"
SMOKE_JSON = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AF_GEORGIAN_ENCODING_SMOKE_RESULT.json"

ACTIVE_FRONTEND_FILES = [
    PROJECT_ROOT / "test_site" / "join.html",
    PROJECT_ROOT / "test_site" / "index.html",
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html",
    PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-chat.jsx",
    PROJECT_ROOT / "test_site" / "variants" / "pro-v2-strings.jsx",
    PROJECT_ROOT / "widget" / "variants" / "pro-v2-chat.jsx",
    PROJECT_ROOT / "dist" / "netlify_test_site_package" / "variants" / "pro-v2-chat.jsx",
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def git_lines(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def result_doc_exists() -> Check:
    return Check("Phase 9AF Georgian encoding result doc exists", RESULT_DOC.exists(), str(RESULT_DOC))


def result_doc_status_valid() -> Check:
    text = read(RESULT_DOC)
    valid = [
        "PHASE_9AF_GEORGIAN_ENCODING_STATUS=PASSED_PENDING_PRIVACY_AND_EMBED_APPROVAL",
        "PHASE_9AF_GEORGIAN_ENCODING_STATUS=FIXED_PENDING_NETLIFY_REDEPLOY",
        "PHASE_9AF_GEORGIAN_ENCODING_STATUS=FAILED_PENDING_ENCODING_FIX",
    ]
    matches = [item for item in valid if item in text]
    return Check("Phase 9AF Georgian encoding status is valid", len(matches) == 1, ", ".join(matches))


def active_frontend_has_no_mojibake() -> Check:
    findings: list[str] = []
    for path in ACTIVE_FRONTEND_FILES:
        text = read(path)
        for marker in ["áƒ", "Ã", "Â·", "â€”"]:
            if marker in text:
                findings.append(f"{path.relative_to(PROJECT_ROOT)}:{marker}")
    return Check("Active frontend sources have no mojibake markers", not findings, ", ".join(findings))


def utf8_charset_present() -> Check:
    join = read(PROJECT_ROOT / "test_site" / "join.html").lower()
    widget_html = read(PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html").lower()
    netlify = read(PROJECT_ROOT / "netlify.toml")
    passed = (
        '<meta charset="utf-8"' in join
        and '<meta charset="utf-8"' in widget_html
        and 'for = "/variants/*.jsx"' in netlify
        and "charset=UTF-8" in netlify
    )
    return Check("UTF-8 charset is declared for host/widget/JSX delivery", passed)


def smoke_script_exists() -> Check:
    return Check("Production Georgian encoding smoke script exists", SMOKE_SCRIPT.exists(), str(SMOKE_SCRIPT))


def visual_qa_contains_encoding_check() -> Check:
    text = read(VISUAL_SCRIPT)
    required = ["GEORGIAN_TEST_QUESTION", "_run_georgian_encoding_check", "hasMojibake"]
    missing = [item for item in required if item not in text]
    return Check("Visual QA includes Georgian encoding check", not missing, ", ".join(missing))


def smoke_result_if_present_passes() -> Check:
    if not SMOKE_JSON.exists():
        return Check("Production Georgian encoding smoke result is present or pending", True, "pending")
    text = read(SMOKE_JSON)
    passed = '"status": "PASSED"' in text and '"raw_response_no_mojibake": true' in text
    return Check("Production Georgian encoding smoke result passes", passed)


def public_launch_no_go() -> Check:
    text = (read(RESULT_DOC) + "\n" + read(PUBLIC_LAUNCH)).lower()
    bad = ["public_launch_decision=go", "public launch: go", "public launch complete"]
    findings = [item for item in bad if item in text]
    return Check("Public launch remains NO-GO", "no-go" in text and not findings, ", ".join(findings))


def real_site_not_modified_and_no_contact_created() -> Check:
    text = read(RESULT_DOC)
    required = [
        "Real Alte site modified: NO",
        "Real join.alte.edu.ge modified: NO",
        "Contact details sent: NO",
        "Lead/task/customer created: NO",
    ]
    missing = [item for item in required if item not in text]
    return Check("No real-site or contact/CRM side effects are recorded", not missing, ", ".join(missing))


def tracked_secret_files_absent() -> Check:
    tracked = set(git_lines("ls-files"))
    forbidden = [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]
    return Check("No .env or .local-secrets files are tracked", not forbidden, ", ".join(forbidden))


def run_checks() -> list[Check]:
    return [
        result_doc_exists(),
        result_doc_status_valid(),
        active_frontend_has_no_mojibake(),
        utf8_charset_present(),
        smoke_script_exists(),
        visual_qa_contains_encoding_check(),
        smoke_result_if_present_passes(),
        public_launch_no_go(),
        real_site_not_modified_and_no_contact_created(),
        tracked_secret_files_absent(),
    ]


def main() -> None:
    checks = run_checks()
    for check in checks:
        print(f"{'PASS' if check.passed else 'FAIL'} {check.name}: {check.detail}")
    if any(not check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
