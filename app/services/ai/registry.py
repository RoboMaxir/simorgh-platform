"""Process-wide provider registry; adapters are not rebuilt for every request."""
from functools import lru_cache
from app.providers.anthropic import AnthropicProvider
from app.providers.openai import OpenAIProvider
from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.qwen import QwenProvider
@lru_cache
def get_provider_registry():
    return {"openai": OpenAIProvider(), "anthropic": AnthropicProvider(), "qwen": QwenProvider(), "openai_compatible": OpenAICompatibleProvider()}
