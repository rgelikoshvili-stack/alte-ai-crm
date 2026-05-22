from __future__ import annotations

import json

from app.api.routes_system import is_placeholder_key
from app.core.config import get_settings
from app.services.ai_service import analyze_with_ai


SAFE_KNOWLEDGE_CONTEXT = [
    {
        "id": "local-safe-contact",
        "title": "Alte University general contact",
        "content": (
            "Alte University's official website is alte.edu.ge. Exact address, phone and email details "
            "should be verified on the current official contact page or by the relevant consultant."
        ),
        "category": "contact",
        "source_key": "alte_contact_v1",
        "source_title": "alte_contact_v1",
        "source_domain": "alte.edu.ge",
        "sensitivity": "low",
    }
]


def validate_direct_dry_run_settings() -> tuple[bool, str]:
    settings = get_settings()
    provider = settings.AI_PROVIDER.lower().strip()
    if provider == "claude" and is_placeholder_key(settings.ANTHROPIC_API_KEY):
        return False, "Refusing Claude dry-run: ANTHROPIC_API_KEY is missing or placeholder."
    return True, "AI dry-run settings accepted."


def run_dry_run() -> dict:
    allowed, reason = validate_direct_dry_run_settings()
    if not allowed:
        return {"passed": False, "reason": reason}

    settings = get_settings()
    analysis, meta = analyze_with_ai(
        "სად მდებარეობს უნივერსიტეტი?",
        source_domain="alte.edu.ge",
        language_hint="ka",
        conversation_history=[],
        knowledge_context=SAFE_KNOWLEDGE_CONTEXT,
    )
    return {
        "passed": True,
        "provider": meta["provider"],
        "model": meta["model"],
        "configured_provider": settings.AI_PROVIDER,
        "intent": analysis.intent,
        "confidence": analysis.confidence,
        "should_handover": analysis.should_handover,
        "used_sources": analysis.used_sources,
        "reply_preview": analysis.reply[:180],
    }


def main() -> None:
    result = run_dry_run()
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    if not result.get("passed"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
