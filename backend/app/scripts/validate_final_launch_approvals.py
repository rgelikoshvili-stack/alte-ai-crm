from __future__ import annotations

import json
import re
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

APPROVAL_INTAKE = PROJECT_ROOT / "docs" / "deployment" / "PHASE_9L_FINAL_APPROVAL_INTAKE.md"
SITE_APPROVAL_RECORD = PROJECT_ROOT / "docs" / "deployment" / "SITE_EMBED_FINAL_APPROVAL_RECORD.md"
SITE_CHECKLIST = PROJECT_ROOT / "docs" / "deployment" / "SITE_EMBED_GO_NO_GO_CHECKLIST.md"
PRIVACY_CHECKLIST = PROJECT_ROOT / "docs" / "deployment" / "PRIVACY_DATA_FINAL_APPROVAL_CHECKLIST.md"

APPROVAL_DOCS = [APPROVAL_INTAKE, SITE_APPROVAL_RECORD, SITE_CHECKLIST, PRIVACY_CHECKLIST]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def combined_approval_text() -> str:
    return "\n".join(read(path) for path in APPROVAL_DOCS)


def field_value(text: str, field_name: str) -> str:
    match = re.search(rf"^[ \t]*-[ \t]*{re.escape(field_name)}[ \t]*:[ \t]*([^\r\n]*)$", text, re.IGNORECASE | re.MULTILINE)
    if not match:
        match = re.search(rf"^[ \t]*{re.escape(field_name)}[ \t]*:[ \t]*([^\r\n]*)$", text, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""


def is_approved(text: str, field_name: str) -> bool:
    return field_value(text, field_name).upper() == "APPROVED"


def non_placeholder(value: str) -> bool:
    if not value:
        return False
    lowered = value.strip().lower()
    placeholders = {
        "pending",
        "tbd",
        "todo",
        "not set",
        "not_set",
        "#privacy-policy-pending",
        "placeholder",
    }
    return lowered not in placeholders and "pending" not in lowered and "placeholder" not in lowered


def real_domain_smoke_passed(text: str) -> bool:
    return bool(re.search(r"real_domain_smoke_status\s*:\s*PASSED", text, re.IGNORECASE)) or (
        "REAL_DOMAIN_SMOKE_STATUS=PASSED" in text
    )


def evaluate_approvals() -> dict[str, object]:
    text = combined_approval_text()
    missing: list[str] = []

    if not APPROVAL_INTAKE.exists():
        missing.append("Phase 9L final approval intake document is missing")
    if not SITE_APPROVAL_RECORD.exists():
        missing.append("site embed final approval record is missing")
    if not SITE_CHECKLIST.exists():
        missing.append("site embed GO/NO-GO checklist is missing")
    if not PRIVACY_CHECKLIST.exists():
        missing.append("privacy/data final approval checklist is missing")

    if not is_approved(text, "content_approval_status"):
        missing.append("content_approval_status must be APPROVED")
    if not is_approved(text, "privacy_approval_status"):
        missing.append("privacy_approval_status must be APPROVED")
    if not non_placeholder(field_value(text, "official_privacy_policy_url")):
        missing.append("official_privacy_policy_url must be present and not a placeholder")
    if not is_approved(text, "asset_upload_approval_status") and not is_approved(text, "website_asset_upload_approval_status"):
        missing.append("asset_upload_approval_status must be APPROVED")
    if not non_placeholder(field_value(text, "final_asset_url")):
        missing.append("final_asset_url must be present and not a placeholder")
    if not is_approved(text, "embed_approval_status") and not is_approved(text, "website_embed_approval_status"):
        missing.append("embed_approval_status must be APPROVED")
    if not non_placeholder(field_value(text, "rollback_owner")):
        missing.append("rollback_owner must be recorded")
    if not non_placeholder(field_value(text, "smoke_test_owner")):
        missing.append("smoke_test_owner must be recorded")
    if not real_domain_smoke_passed(text):
        missing.append("real_domain_smoke_status must be PASSED")
    if not is_approved(text, "public_launch_approval_status"):
        missing.append("public_launch_approval_status must be APPROVED")

    go_allowed = not missing
    return {
        "approval_status": "GO" if go_allowed else "NO_GO",
        "missing_blockers": missing,
        "go_allowed": go_allowed,
    }


def main() -> None:
    print(json.dumps(evaluate_approvals(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
