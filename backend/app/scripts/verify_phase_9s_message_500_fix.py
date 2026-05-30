from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


FILES = [
    ROOT / "test_site" / "alte-ai-chat-widget.js",
    ROOT / "dist" / "widget" / "alte-ai-chat-widget.js",
    ROOT / "test_site" / "alte-ai-chat-widget.html",
    ROOT / "dist" / "widget" / "alte-ai-chat-widget.html",
    ROOT / "test_site" / "variants" / "pro-v2-chat.jsx",
    ROOT / "widget" / "variants" / "pro-v2-chat.jsx",
]

FORBIDDEN = [
    "/api/chat",
    "api.anthropic.com",
    "ANTHROPIC_API_KEY",
    "sk-ant-",
    "DATABASE_URL",
    "window.claude.complete",
    "/chat/messages_",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def git_tracked(path: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", path],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def check(condition: bool, label: str, failures: list[str]) -> None:
    print(f"{'PASS' if condition else 'FAIL'} {label}")
    if not condition:
        failures.append(label)


def main() -> int:
    failures: list[str] = []
    joined = "\n".join(read(path) for path in FILES if path.exists())

    for path in FILES:
        check(path.exists(), f"{path.relative_to(ROOT)} exists", failures)

    check("/chat/session/start" in joined, "frontend contains /chat/session/start", failures)
    check("/chat/message" in joined, "frontend contains /chat/message", failures)
    for forbidden in FORBIDDEN:
        check(forbidden not in joined, f"frontend excludes {forbidden}", failures)

    check("website_chat" in joined, "frontend contains website_chat", failures)
    check("pro_v2_safe" in joined, "frontend contains pro_v2_safe", failures)
    check("selected_department" in joined, "frontend contains selected_department", failures)
    check("selected_topic" in joined, "frontend contains selected_topic", failures)
    variant = read(ROOT / "test_site" / "variants" / "pro-v2-chat.jsx")
    check("/chat/handover automatically from a normal typed message" in variant, "handover auto-call guard documented", failures)
    check("requestBackendHandover(currentDept, requestText)" in variant, "handover remains explicit operator action", failures)
    check("ვერ მივიღე პასუხი. სცადეთ თავიდან ან მიმართეთ ოპერატორს." in variant, "visible Georgian message error renderer exists", failures)
    check("Could not get an answer. Please try again or contact an operator." in variant, "visible English message error renderer exists", failures)

    check((ROOT / "backend" / "app" / "scripts" / "production_chat_message_smoke.py").exists(), "production chat message smoke exists", failures)

    docs = "\n".join(
        read(path)
        for path in [
            ROOT / "README.md",
            ROOT / "docs" / "NEXT_PHASES.md",
            ROOT / "docs" / "deployment" / "PHASE_9N_HOSTED_BROWSER_SMOKE_RESULT.md",
            ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md",
        ]
        if path.exists()
    )
    check("PUBLIC_LAUNCH_DECISION=GO_APPROVED_FOR_PUBLIC_LAUNCH" not in docs, "public launch not marked complete", failures)
    check("HOSTED_BROWSER_SMOKE_STATUS=PASSED" not in docs, "browser smoke not falsely passed", failures)

    check(not git_tracked(".env"), ".env not tracked", failures)
    check(not git_tracked(".local-secrets"), ".local-secrets not tracked", failures)

    if failures:
        print("verify_phase_9s_message_500_fix=FAIL")
        return 1
    print("verify_phase_9s_message_500_fix=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
