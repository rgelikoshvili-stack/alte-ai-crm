from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEPARTMENT_MAP = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "department_topic_source_map.json"
SOURCE_GROUPS = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "source_groups.json"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AI_KNOWLEDGE_ROUTING_CLARIFICATION_OPERATOR_RESULT.md"
QA_REPORT = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AI_CLARIFICATION_ROUTING_QA_RESULT.md"
TEST_FILE = PROJECT_ROOT / "backend" / "app" / "tests" / "test_phase_9ai_knowledge_source_routing_clarification.py"
PRODUCTION_SCRIPT = PROJECT_ROOT / "backend" / "app" / "scripts" / "production_phase_9ai_clarification_routing_qa.py"
TEST_STRINGS = PROJECT_ROOT / "test_site" / "variants" / "pro-v2-strings.jsx"
TEST_MODALS = PROJECT_ROOT / "test_site" / "variants" / "pro-v2-modals.jsx"
WIDGET_STRINGS = PROJECT_ROOT / "widget" / "variants" / "pro-v2-strings.jsx"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
CHAT_SERVICE = PROJECT_ROOT / "backend" / "app" / "services" / "chat_service.py"
BRIDGE = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html"
BRIDGE_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT, text=True, capture_output=True, check=True)
    return result.stdout.splitlines()


def check(name: str, passed: bool, detail: str = "") -> tuple[str, bool, str]:
    print(f"{'PASS' if passed else 'FAIL'} {name}: {detail}")
    return name, passed, detail


def run_checks() -> list[tuple[str, bool, str]]:
    frontend_text = "\n".join(read(path) for path in [TEST_STRINGS, TEST_MODALS, WIDGET_STRINGS, BRIDGE, BRIDGE_JS])
    docs_text = "\n".join(read(path) for path in [DEPARTMENT_MAP, SOURCE_GROUPS, RESULT_DOC] if path.exists())
    chat_text = read(CHAT_SERVICE)
    public_text = read(PUBLIC_LAUNCH).lower()
    tracked = tracked_files()
    return [
        check("department_topic_source_map.json exists", DEPARTMENT_MAP.exists(), str(DEPARTMENT_MAP)),
        check("source_groups.json exists", SOURCE_GROUPS.exists(), str(SOURCE_GROUPS)),
        check("result doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
        check("production QA report exists", QA_REPORT.exists(), str(QA_REPORT)),
        check("tests exist", TEST_FILE.exists(), str(TEST_FILE)),
        check("production QA script exists", PRODUCTION_SCRIPT.exists(), str(PRODUCTION_SCRIPT)),
        check("KA/EN clarification examples exist", all(value in docs_text for value in [
            "ზუსტად რომ გიპასუხოთ",
            "To answer accurately",
            "რომელ პროგრამაზე",
            "გადახდებზე რომ გიპასუხოთ",
            "სტუდენტის სტატუსთან დაკავშირებით",
        ])),
        check("official KB facts documented", all(value in docs_text for value in ["240", "120", "5", "9–14 March"])),
        check("finance/library/IT are mapped away from international", all(value in docs_text for value in [
            "\"department_id\": \"finance\"",
            "\"department_id\": \"library\"",
            "\"department_id\": \"it_support\"",
            "Do NOT route to international admissions just because source_domain is join.alte.edu.ge",
        ])),
        check("contact textarea labels exist", all(value in frontend_text for value in [
            "თქვენი კითხვა / შეტყობინება",
            "Your question / message",
        ])),
        check("wait_for_operator labels exist", all(value in frontend_text for value in ["დაელოდე ოპერატორს", "Wait for operator"])),
        check("no mojibake in 9AI/static evidence", "áƒ" not in docs_text + frontend_text),
        check("unsupported answer copy does not ask direct contact details", all(value not in chat_text[chat_text.index("def build_no_source_reply") : chat_text.index("def is_ambiguous_program_question")].lower() for value in [
            "phone",
            "email",
            "name",
            "ტელეფონი",
            "ელ.ფოსტა",
            "სახელი",
        ])),
        check("public launch remains NO-GO", "public_launch_decision=go" not in public_text and "no-go" in public_text),
        check("no real contact data in docs/tests", all(value not in docs_text + read(TEST_FILE) for value in [
            "+995",
            "@gmail.com",
            "real contact data sent: YES",
        ])),
        check("env/local-secrets are not tracked", not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]),
        check("frontend does not call api.anthropic.com", "api.anthropic.com" not in frontend_text),
        check("frontend does not expose API keys", all(value not in frontend_text for value in ["ANTHROPIC_API_KEY", "sk-ant"])),
        check("frontend uses backend endpoints", all(value in frontend_text for value in ["/chat/session/start", "/chat/message"])),
    ]


def main() -> int:
    checks = run_checks()
    return 0 if all(passed for _, passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
