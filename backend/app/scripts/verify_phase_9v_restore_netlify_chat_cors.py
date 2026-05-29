from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
ORIGIN = "https://nimble-croissant-2f66e8.netlify.app"
RESULT_DOC = ROOT / "docs" / "deployment" / "PHASE_9V_RESTORE_NETLIFY_CHAT_CORS_RESULT.md"
SMOKE = BACKEND / "app" / "scripts" / "production_netlify_public_chat_cors_smoke.py"
FRONTEND_FILES = [
    ROOT / "test_site" / "alte-ai-chat-widget.js",
    ROOT / "dist" / "widget" / "alte-ai-chat-widget.js",
    ROOT / "test_site" / "alte-ai-chat-widget.html",
    ROOT / "dist" / "widget" / "alte-ai-chat-widget.html",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def tracked(path: str) -> bool:
    return subprocess.run(
        ["git", "ls-files", "--error-unmatch", path],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0


def check(condition: bool, label: str, failures: list[str]) -> None:
    print(f"{'PASS' if condition else 'FAIL'} {label}")
    if not condition:
        failures.append(label)


def main() -> int:
    failures: list[str] = []
    result = read(RESULT_DOC)
    frontend = "\n".join(read(path) for path in FRONTEND_FILES)
    docs = "\n".join(
        read(path)
        for path in [
            ROOT / "README.md",
            ROOT / "docs" / "NEXT_PHASES.md",
            ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md",
            ROOT / "docs" / "deployment" / "PHASE_9N_HOSTED_BROWSER_SMOKE_RESULT.md",
            RESULT_DOC,
        ]
    )

    check(SMOKE.exists(), "CORS smoke script exists", failures)
    check(RESULT_DOC.exists(), "result doc exists", failures)
    check(ORIGIN in result, "result doc records exact origin", failures)
    check("wildcard CORS used: NO" in result or "no wildcard" in result.lower(), "result doc confirms no wildcard", failures)
    check("Public launch: NO" in result or "public launch remains NO-GO" in result, "result doc confirms public launch NO-GO", failures)
    check("Production DB modified: NO" in result, "result doc confirms no DB changes", failures)
    check("Secret Manager changed: NO" in result, "result doc confirms no Secret Manager changes", failures)

    check("/chat/session/start" in frontend, "frontend uses /chat/session/start", failures)
    check("/chat/message" in frontend, "frontend uses /chat/message", failures)
    for forbidden in ["/chat/messages", "/api/chat", "api.anthropic.com", "ANTHROPIC_API_KEY", "sk-ant-"]:
        check(forbidden not in frontend, f"frontend excludes {forbidden}", failures)

    main_py = read(BACKEND / "app" / "main.py")
    check("error responses, including backend 500s" in main_py, "CORS outermost error-response note exists", failures)

    check("HOSTED_BROWSER_SMOKE_STATUS=PASSED" not in docs, "browser smoke not falsely marked passed", failures)
    check("PUBLIC_LAUNCH_DECISION=GO_APPROVED_FOR_PUBLIC_LAUNCH" not in docs, "public launch not complete", failures)
    check(not tracked(".env"), ".env not tracked", failures)
    check(not tracked(".local-secrets"), ".local-secrets not tracked", failures)

    if failures:
        print("verify_phase_9v_restore_netlify_chat_cors=FAIL")
        return 1
    print("verify_phase_9v_restore_netlify_chat_cors=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
