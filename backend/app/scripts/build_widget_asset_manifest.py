from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
MANIFEST = PROJECT_ROOT / "docs" / "final_handoff" / "WIDGET_ASSET_MANIFEST.md"

ASSETS = [
    PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.js",
    PROJECT_ROOT / "dist" / "widget" / "alte-ai-chat-widget.html",
    PROJECT_ROOT / "widget" / "alte-university-ai-chatbot-safe-pro.html",
]

FORBIDDEN_PATTERNS = [
    ("api.anthropic.com", re.compile(r"api\.anthropic\.com", re.IGNORECASE)),
    ("ANTHROPIC_API_KEY", re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE)),
    ("sk-ant-", re.compile("sk" + r"-ant-", re.IGNORECASE)),
    ("DATABASE_URL", re.compile(r"DATABASE_URL", re.IGNORECASE)),
    ("DB password patterns", re.compile(r"DB_PASSWORD|postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE)),
]

REQUIRED_PATTERNS = [
    "/chat/session/start",
    "/chat/message",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_assets() -> dict[str, bool]:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in ASSETS if path.exists())
    results: dict[str, bool] = {}
    for label, pattern in FORBIDDEN_PATTERNS:
        results[f"{label} absent"] = not pattern.search(combined)
    for pattern in REQUIRED_PATTERNS:
        results[f"{pattern} present"] = pattern in combined
    return results


def build_manifest() -> str:
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Widget Asset Manifest",
        "",
        f"Generated: `{generated_at}`",
        "",
        "## Assets",
        "",
        "| File | Size Bytes | SHA256 |",
        "| --- | ---: | --- |",
    ]
    for path in ASSETS:
        relative = path.relative_to(PROJECT_ROOT).as_posix()
        if path.exists():
            lines.append(f"| `{relative}` | {path.stat().st_size} | `{sha256(path)}` |")
        else:
            lines.append(f"| `{relative}` | MISSING | MISSING |")

    lines.extend(["", "## Safety Scan", ""])
    for label, passed in scan_assets().items():
        lines.append(f"- {label}: {'PASS' if passed else 'FAIL'}")

    lines.extend(
        [
            "",
            "## Launch Note",
            "",
            "The manifest records prepared assets only. Asset upload, actual site embed, real-domain smoke, and public launch remain pending until explicit approvals are recorded.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(build_manifest(), encoding="utf-8")
    print(f"Wrote {MANIFEST.relative_to(PROJECT_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
