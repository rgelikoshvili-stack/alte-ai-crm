from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from app.scripts.verify_phase_9ai_knowledge_routing_clarification_operator import (
    check,
    read,
    run_checks as run_base_checks,
    tracked_files,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9AI_CHATGPT_STYLE_KB_CLARIFICATION_OPERATOR_RESULT.md"
QA_REPORT = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AI_CHATGPT_STYLE_ROUTING_QA_RESULT.md"
TEST_FILE = PROJECT_ROOT / "backend" / "app" / "tests" / "test_phase_9ai_chatgpt_style_kb_clarification_operator.py"
PRODUCTION_SCRIPT = PROJECT_ROOT / "backend" / "app" / "scripts" / "production_phase_9ai_chatgpt_style_routing_qa.py"
DEPARTMENT_MAP = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "department_topic_source_map.json"
SOURCE_GROUPS = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge" / "source_groups.json"
TEST_STRINGS = PROJECT_ROOT / "test_site" / "variants" / "pro-v2-strings.jsx"
TEST_MODALS = PROJECT_ROOT / "test_site" / "variants" / "pro-v2-modals.jsx"
BRIDGE = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html"
BRIDGE_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"
CHAT_SERVICE = PROJECT_ROOT / "backend" / "app" / "services" / "chat_service.py"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"
MOJIBAKE_MARKER = "\u00e1\u0192"


def run_checks() -> list[tuple[str, bool, str]]:
    checks = run_base_checks()
    frontend_text = "\n".join(read(path) for path in [TEST_STRINGS, TEST_MODALS, BRIDGE, BRIDGE_JS])
    docs_text = "\n".join(read(path) for path in [RESULT_DOC, QA_REPORT, DEPARTMENT_MAP, SOURCE_GROUPS] if path.exists())
    chat_text = read(CHAT_SERVICE)
    public_text = read(PUBLIC_LAUNCH).lower()
    tracked = tracked_files()
    script_text = read(PRODUCTION_SCRIPT) if PRODUCTION_SCRIPT.exists() else ""
    test_text = read(TEST_FILE) if TEST_FILE.exists() else ""
    unsupported_block = chat_text[chat_text.index("def build_no_source_reply") : chat_text.index("def is_ambiguous_program_question")]
    checks.extend(
        [
            check("ChatGPT-style result doc exists", RESULT_DOC.exists(), str(RESULT_DOC)),
            check("ChatGPT-style production QA report exists", QA_REPORT.exists(), str(QA_REPORT)),
            check("ChatGPT-style tests exist", TEST_FILE.exists(), str(TEST_FILE)),
            check("ChatGPT-style production script exists", PRODUCTION_SCRIPT.exists(), str(PRODUCTION_SCRIPT)),
            check("ChatGPT-style doc decision state exists", "BACKEND_DEPLOYED_CHATGPT_STYLE_KB_ROUTING_OPERATOR_READY_PENDING_PRIVACY_CONTACT_APPROVAL" in docs_text),
            check("unsupported answer copy exists", "approved official sources" in unsupported_block or "დამტკიცებულ წყაროში" in unsupported_block),
            check("contact textarea labels exist in frontend", all(value in frontend_text for value in ["თქვენი კითხვა / შეტყობინება", "Your question / message"])),
            check("wait-for-operator labels exist in frontend", all(value in frontend_text for value in ["დაელოდე ოპერატორს", "Wait for operator"])),
            check("official KB facts documented", all(value in docs_text for value in ["240", "120", "5", "9–14 March"])),
            check("finance/library/IT not routed to International Admissions", all(value in docs_text for value in ["finance_sources", "library_sources", "it_support_sources", "Do NOT route to international admissions"])),
            check("no mojibake marker in ChatGPT-style docs/scripts/tests", MOJIBAKE_MARKER not in docs_text + script_text + test_text),
            check("unsupported copy does not directly ask phone/email/name", all(value not in unsupported_block.lower() for value in ["phone", "email", "name", "ტელეფონი", "ელ.ფოსტა", "სახელი"])),
            check("public launch remains NO-GO", "public_launch_decision=go" not in public_text and "no-go" in public_text),
            check("no real contact data in ChatGPT-style docs/tests", all(value not in docs_text + test_text for value in ["+995", "@gmail.com", "REAL_CONTACT_DATA_SENT=YES"])),
            check("env/local-secrets are not tracked", not [path for path in tracked if path.endswith(".env") or ".local-secrets" in path]),
            check("frontend does not call api.anthropic.com", "api.anthropic.com" not in frontend_text),
            check("frontend uses backend endpoints only", all(value in frontend_text for value in ["/chat/session/start", "/chat/message"])),
        ]
    )
    return checks


def main() -> int:
    checks = run_checks()
    return 0 if all(passed for _, passed, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
