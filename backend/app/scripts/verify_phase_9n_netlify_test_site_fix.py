from __future__ import annotations

import re
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

NETLIFY_TOML = PROJECT_ROOT / "netlify.toml"
REDIRECTS = PROJECT_ROOT / "test_site" / "_redirects"
DEPLOY_README = PROJECT_ROOT / "test_site" / "NETLIFY_DEPLOY_README_GEO.md"
ZIP_PATH = PROJECT_ROOT / "dist" / "netlify_test_site_deploy.zip"
MANIFEST = PROJECT_ROOT / "docs" / "test_origin_handoff" / "NETLIFY_TEST_SITE_PACKAGE_MANIFEST.md"
RESULT_DOC = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_NETLIFY_TEST_SITE_FIX_RESULT.md"
TEST_WIDGET_JS = PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js"

README = PROJECT_ROOT / "README.md"
NEXT_PHASES = PROJECT_ROOT / "docs" / "NEXT_PHASES.md"
HOSTED_SMOKE = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_HOSTED_BROWSER_SMOKE_RESULT.md"
CORS_RESULT = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9N_CORS_TEST_ORIGIN_EXECUTION_RESULT.md"
PUBLIC_LAUNCH = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9P_PUBLIC_LAUNCH_DECISION.md"

DECISION_STATE = "BACKEND_DEPLOYED_NETLIFY_TEST_PACKAGE_READY_PENDING_REDEPLOY_AND_BROWSER_SMOKE"
PENDING_STATUS = "PHASE_9N_NETLIFY_FIX_STATUS=DEPLOY_PACKAGE_READY_PENDING_NETLIFY_REDEPLOY"
DEPLOYED_STATUS = "PHASE_9N_NETLIFY_FIX_STATUS=NETLIFY_DEPLOYED_PENDING_BROWSER_SMOKE"

EXPECTED_ZIP_ROOT = {
    "index.html",
    "join.html",
    "alte-ai-chat-widget.js",
    "alte-ai-chat-widget.html",
    "_redirects",
    "README_GEO.md",
    "NETLIFY_DEPLOY_README_GEO.md",
}

FORBIDDEN_ASSET_PATTERNS = [
    re.compile(r"api\.anthropic\.com", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY", re.IGNORECASE),
    re.compile("sk" + r"-ant-", re.IGNORECASE),
    re.compile(r"DATABASE_URL", re.IGNORECASE),
    re.compile(r"DB_PASSWORD", re.IGNORECASE),
    re.compile(r"postgresql\+asyncpg://[^:\s]+:[^@\s]+@", re.IGNORECASE),
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def zip_names() -> list[str]:
    if not ZIP_PATH.exists():
        return []
    with zipfile.ZipFile(ZIP_PATH) as archive:
        return [info.filename.replace("\\", "/") for info in archive.infolist()]


def required_files_exist() -> list[Check]:
    files = [NETLIFY_TOML, REDIRECTS, DEPLOY_README, ZIP_PATH, MANIFEST, RESULT_DOC]
    return [Check(f"Required file exists: {path.name}", path.exists(), str(path)) for path in files]


def result_status_recorded() -> Check:
    text = read(RESULT_DOC)
    return Check("Result records Netlify fix status", PENDING_STATUS in text or DEPLOYED_STATUS in text)


def docs_record_decision_state() -> Check:
    text = "\n".join(read(path) for path in [README, NEXT_PHASES, HOSTED_SMOKE, CORS_RESULT, RESULT_DOC])
    return Check("Docs record Netlify package decision state", DECISION_STATE in text)


def browser_smoke_not_passed() -> Check:
    text = "\n".join(read(path).lower() for path in [HOSTED_SMOKE, CORS_RESULT, RESULT_DOC, NEXT_PHASES, README])
    bad = [
        phrase
        for phrase in [
            "hosted_browser_smoke_status=passed",
            "hosted browser smoke: passed",
            "browser smoke passed: yes",
        ]
        if phrase in text
    ]
    return Check("Browser smoke not marked passed", not bad, ", ".join(bad))


def public_launch_not_complete() -> Check:
    text = "\n".join(read(path).lower() for path in [PUBLIC_LAUNCH, README, NEXT_PHASES, RESULT_DOC])
    bad = [
        phrase
        for phrase in [
            "public launch complete",
            "full production launch complete",
            "public launch: complete",
            "public_launch_decision=go",
        ]
        if phrase in text
    ]
    return Check("Public launch not marked complete", not bad, ", ".join(bad))


def actual_alte_embed_not_complete() -> Check:
    text = "\n".join(read(path).lower() for path in [README, NEXT_PHASES, RESULT_DOC, CORS_RESULT])
    bad = [
        phrase
        for phrase in [
            "actual alte embed complete",
            "actual site embed completed",
            "actual site embed executed: yes",
            "actual embed complete: yes",
        ]
        if phrase in text
    ]
    return Check("Actual Alte embed not marked complete", not bad, ", ".join(bad))


def zip_root_is_valid() -> Check:
    names = zip_names()
    missing = sorted(EXPECTED_ZIP_ROOT - set(names))
    nested = sorted(name for name in names if name.startswith("test_site/"))
    passed = not missing and not nested
    detail_parts = []
    if missing:
        detail_parts.append("missing=" + ",".join(missing))
    if nested:
        detail_parts.append("nested=" + ",".join(nested))
    return Check("ZIP root contains expected files and is not nested", passed, "; ".join(detail_parts))


def package_assets_are_safe() -> Check:
    findings: list[str] = []
    paths = [
        PROJECT_ROOT / "test_site" / "index.html",
        PROJECT_ROOT / "test_site" / "join.html",
        PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.js",
        PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html",
        REDIRECTS,
    ]
    for path in paths:
        text = read(path)
        for pattern in FORBIDDEN_ASSET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.name}:{pattern.pattern}")
    if ZIP_PATH.exists():
        with zipfile.ZipFile(ZIP_PATH) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                text = archive.read(info).decode("utf-8", errors="ignore")
                for pattern in FORBIDDEN_ASSET_PATTERNS:
                    if pattern.search(text):
                        findings.append(f"zip:{info.filename}:{pattern.pattern}")
    return Check("Test-site assets and ZIP contain no forbidden secret/provider patterns", not findings, ", ".join(findings))


def backend_endpoints_present() -> Check:
    text = read(TEST_WIDGET_JS) + "\n" + read(PROJECT_ROOT / "test_site" / "alte-ai-chat-widget.html")
    missing = [endpoint for endpoint in ["/chat/session/start", "/chat/message"] if endpoint not in text]
    return Check("Test-site package contains backend chat endpoints", not missing, ", ".join(missing))


def env_not_tracked() -> Check:
    result = subprocess.run(["git", "ls-files", ".env", "backend/.env"], cwd=PROJECT_ROOT, capture_output=True, text=True, check=False)
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".env is not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def local_secrets_not_tracked() -> Check:
    result = subprocess.run(
        ["git", "ls-files", ".local-secrets", ".local-secrets/*", "backend/.local-secrets", "secret-values.local.txt", "secret-values.local.*"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".local-secrets are not tracked", not tracked, ", ".join(tracked) if tracked else "not tracked")


def run_checks() -> list[Check]:
    return [
        *required_files_exist(),
        result_status_recorded(),
        docs_record_decision_state(),
        browser_smoke_not_passed(),
        public_launch_not_complete(),
        actual_alte_embed_not_complete(),
        zip_root_is_valid(),
        package_assets_are_safe(),
        backend_endpoints_present(),
        env_not_tracked(),
        local_secrets_not_tracked(),
    ]


def main() -> None:
    checks = run_checks()
    for check in checks:
        print(f"{'PASS' if check.passed else 'FAIL'} {check.name}: {check.detail}")
    if any(not check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
