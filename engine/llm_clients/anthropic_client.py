"""Anthropic Claude LLM client implementation."""

import os
from typing import Any

from anthropic import AsyncAnthropic

from engine.llm_clients.base_client import BaseLLMClient


class AnthropicClient(BaseLLMClient):
    """Client for Anthropic Claude models."""

    def __init__(self, model: str = "claude-sonnet-4-20250514", **kwargs: Any):
        super().__init__(model, **kwargs)
        self.client = AsyncAnthropic(
            api_key=kwargs.get("api_key") or os.getenv("ANTHROPIC_API_KEY"),
        )

    async def invoke(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        tools: list[dict] | None = None,
    ) -> dict[str, Any]:
        # Separate system message from conversation
        system_msg = ""
        conversation = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                conversation.append(msg)

        kwargs_api: dict[str, Any] = {
            "model": self.model,
            "messages": conversation,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_msg:
            kwargs_api["system"] = system_msg
        if tools:
            kwargs_api["tools"] = [
                {
                    "name": t["function"]["name"],
                    "description": t["function"].get("description", ""),
                    "input_schema": t["function"]["parameters"],
                }
                for t in tools
            ]

        response = await self.client.messages.create(**kwargs_api)

        content = ""
        tool_calls = None
        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                if tool_calls is None:
                    tool_calls = []
                import json
                tool_calls.append({
                    "id": block.id,
                    "function": {
                        "name": block.name,
                        "arguments": json.dumps(block.input),
                    },
                })

        return {
            "content": content,
            "tool_calls": tool_calls,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        }

    async def invoke_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        system_msg = ""
        conversation = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                conversation.append(msg)

        kwargs_api: dict[str, Any] = {
            "model": self.model,
            "messages": conversation,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_msg:
            kwargs_api["system"] = system_msg

        async with self.client.messages.stream(**kwargs_api) as stream:
            async for text in stream.text_stream:
                yield text
