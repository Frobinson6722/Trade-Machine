"""Factory function for creating LLM clients."""

from typing import Any

from engine.llm_clients.base_client import BaseLLMClient


def create_llm_client(provider: str, model: str | None = None, **kwargs: Any) -> BaseLLMClient:
    """Create an LLM client for the specified provider.

    Args:
        provider: One of 'openai', 'anthropic', 'google'
        model: Model name override. Uses provider default if None.
        **kwargs: Additional arguments passed to the client constructor.
    """
    provider = provider.lower()

    if provider == "openai":
        from engine.llm_clients.openai_client import OpenAIClient
        return OpenAIClient(model=model or "gpt-4o", **kwargs)
    elif provider == "anthropic":
        from engine.llm_clients.anthropic_client import AnthropicClient
        return AnthropicClient(model=model or "claude-sonnet-4-20250514", **kwargs)
    elif provider == "google":
        from engine.llm_clients.google_client import GoogleClient
        return GoogleClient(model=model or "gemini-2.0-flash", **kwargs)
    else:
        raise ValueError(
            f"Unknown LLM provider: {provider}. "
            f"Supported: openai, anthropic, google"
        )
