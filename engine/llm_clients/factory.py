"""Factory function for creating the Anthropic Claude LLM client."""

from typing import Any

from engine.llm_clients.base_client import BaseLLMClient


def create_llm_client(provider: str = "anthropic", model: str | None = None, **kwargs: Any) -> BaseLLMClient:
    """Create a Claude LLM client.

    Args:
        provider: Must be 'anthropic' (only supported provider)
        model: Model name override. Defaults to claude-sonnet-4-20250514.
        **kwargs: Additional arguments passed to the client constructor.
    """
    from engine.llm_clients.anthropic_client import AnthropicClient
    return AnthropicClient(model=model or "claude-sonnet-4-20250514", **kwargs)
