from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""
    critical: bool = True


def run_checks(project_root: Path = PROJECT_ROOT) -> list[Check]:
    checks = [
        file_exists(project_root / "README.md", "README.md exists"),
        file_exists(project_root / "backend" / ".env.local.example", ".env.local.example exists"),
        file_exists(project_root / "widget" / "demo.html", "widget demo exists"),
        file_exists(project_root / "widget" / "alte-chat-widget.js", "widget script exists"),
        file_exists(project_root / "docs" / "releases" / "v0.7-local-mvp.md", "release notes exist"),
        file_exists(project_root / "backend" / "app" / "knowledge_seed" / "alte_seed_v1.json", "Alte seed file exists"),
        migration_files_exist(project_root),
        env_not_tracked(project_root),
        app_imports(),
        diagnostics_route_registered(),
    ]
    return checks


def file_exists(path: Path, name: str) -> Check:
    return Check(name=name, passed=path.exists(), detail=str(path))


def migration_files_exist(project_root: Path) -> Check:
    versions = project_root / "backend" / "alembic" / "versions"
    files = list(versions.glob("*.py")) if versions.exists() else []
    return Check("Alembic migrations exist", bool(files), f"{len(files)} migration files")


def env_not_tracked(project_root: Path) -> Check:
    try:
        result = subprocess.run(
            ["git", "ls-files", ".env", "backend/.env"],
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return Check(".env is not tracked by git", False, str(exc))
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return Check(".env is not tracked by git", not tracked, ", ".join(tracked) if tracked else "not tracked")


def app_imports() -> Check:
    try:
        from app.main import app  # noqa: F401
    except Exception as exc:
        return Check("FastAPI app imports", False, repr(exc))
    return Check("FastAPI app imports", True)


def diagnostics_route_registered() -> Check:
    try:
        from app.main import app

        paths = {route.path for route in app.routes}
    except Exception as exc:
        return Check("diagnostics route registered", False, repr(exc))
    return Check(
        "diagnostics route registered",
        "/diagnostics/local-demo" in paths,
        "/diagnostics/local-demo" if "/diagnostics/local-demo" in paths else "missing",
    )


def main() -> None:
    checks = run_checks()
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"{status} {check.name}: {check.detail}")
    if any(check.critical and not check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
