from functools import lru_cache

import anthropic

from backend.config import settings


class AIUnavailableError(RuntimeError):
    """Raised when ANTHROPIC_API_KEY is not configured. Callers should treat
    this as a normal, expected condition and fall back to manual entry —
    not a bug to swallow silently."""


@lru_cache
def get_client() -> anthropic.Anthropic | None:
    if not settings.anthropic_api_key:
        return None
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)
