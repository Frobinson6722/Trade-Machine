"""Abstract base class for LLM clients."""

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMClient(ABC):
    """Base class all LLM provider clients must implement."""

    def __init__(self, model: str, **kwargs: Any):
        self.model = model
        self.kwargs = kwargs

    @abstractmethod
    async def invoke(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        tools: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Send messages to the LLM and return the response.

        Returns:
            dict with keys: content (str), tool_calls (list|None), usage (dict)
        """
        ...

    @abstractmethod
    async def invoke_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        """Stream responses from the LLM. Yields content chunks."""
        ...
