from dataclasses import dataclass

from anthropic import Anthropic

from app.core.config import get_settings


@dataclass(frozen=True)
class AnthropicClientHandle:
    provider: str
    model: str
    client: Anthropic


def get_ai_client() -> AnthropicClientHandle:
    settings = get_settings()
    return AnthropicClientHandle(
        provider="anthropic",
        model=settings.AI_MODEL,
        client=Anthropic(api_key=settings.ANTHROPIC_API_KEY),
    )
